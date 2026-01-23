"""
Internet Speed Test Module with Rich TUI
"""

import time
import threading
import speedtest
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
)
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.box import ROUNDED

# Import shared console
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.console import console


def display_status(message: str, status_type: str = "info"):
    """Displays a styled status message in a panel."""
    styles = {
        "success": ("✓", "green"),
        "error": ("✗", "red"),
        "warning": ("⚠", "yellow"),
        "info": ("ℹ", "cyan"),
    }

    icon, style = styles.get(status_type, styles["info"])

    content = Text()
    content.append(f"{icon} ", style=style)
    content.append(message, style=style)

    panel = Panel(
        content,
        box=ROUNDED,
        border_style=style,
        padding=(0, 2),
    )
    console.print()
    console.print(panel)


def display_results(
    download: float, upload: float, ping: float, server_info: str = None
):
    """Displays the speed test results in a styled table."""
    table = Table(
        title="[bold cyan]⚡ SPEED TEST RESULTS ⚡[/bold cyan]",
        box=ROUNDED,
        border_style="cyan",
        header_style="bold cyan",
        show_header=True,
    )

    table.add_column("Metric", style="white", justify="left")
    table.add_column("Value", justify="right")

    if server_info:
        table.add_row("[dim]Server[/dim]", f"[dim]{server_info}[/dim]")
        table.add_section()

    table.add_row(
        "[green]↓ Download[/green]", f"[bold green]{download:.2f} Mbps[/bold green]"
    )
    table.add_row(
        "[yellow]↑ Upload[/yellow]", f"[bold yellow]{upload:.2f} Mbps[/bold yellow]"
    )
    table.add_row(
        "[magenta]◉ Ping[/magenta]", f"[bold magenta]{ping:.2f} ms[/bold magenta]"
    )

    console.print()
    console.print(table)


def run_speed_test(cli_show: bool = True) -> tuple:
    """
    Runs the internet speed test and returns the results.

    Args:
        cli_show: Whether to display progress in the terminal

    Returns:
        Tuple of (download_mbps, upload_mbps, ping_ms, server_info) or (None, None, None, None) on error
    """
    try:
        st = speedtest.Speedtest()
        server_info = None

        if cli_show:
            with console.status(
                "[yellow]Finding the best server...[/yellow]", spinner="dots"
            ) as status:
                st.get_best_server()
                server_info = f"{st.results.server['sponsor']} ({st.results.server['name']}, {st.results.server['country']})"
                status.update(f"[green]✓ Selected: {server_info}[/green]")
                time.sleep(0.5)

            console.print(f"[green]✓ Server:[/green] {server_info}")
            console.print()

            # Run tests with progress bar
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(bar_width=30),
                TaskProgressColumn(),
                console=console,
            ) as progress:
                # Download test
                download_task = progress.add_task(
                    "[cyan]Testing download speed...", total=100
                )

                # Run download in thread and update progress
                download_result = [None]

                def do_download():
                    download_result[0] = st.download()

                download_thread = threading.Thread(target=do_download)
                download_thread.start()

                # Simulate progress while download runs
                while download_thread.is_alive():
                    if not progress.finished:
                        progress.update(download_task, advance=2)
                    time.sleep(0.1)
                download_thread.join()
                progress.update(download_task, completed=100)

                download_speed_mbps = download_result[0] / 1_000_000
                progress.update(
                    download_task,
                    description=f"[green]✓ Download: {download_speed_mbps:.2f} Mbps",
                )

                # Upload test
                upload_task = progress.add_task(
                    "[cyan]Testing upload speed...", total=100
                )

                upload_result = [None]

                def do_upload():
                    upload_result[0] = st.upload()

                upload_thread = threading.Thread(target=do_upload)
                upload_thread.start()

                while upload_thread.is_alive():
                    if not progress.finished:
                        progress.update(upload_task, advance=2)
                    time.sleep(0.1)
                upload_thread.join()
                progress.update(upload_task, completed=100)

                upload_speed_mbps = upload_result[0] / 1_000_000
                progress.update(
                    upload_task,
                    description=f"[green]✓ Upload: {upload_speed_mbps:.2f} Mbps",
                )

                # Ping (already done during server selection)
                ping_task = progress.add_task("[cyan]Measuring ping...", total=100)
                time.sleep(0.3)
                progress.update(ping_task, completed=100)
                ping_ms = st.results.ping
                progress.update(
                    ping_task, description=f"[green]✓ Ping: {ping_ms:.2f} ms"
                )

            return download_speed_mbps, upload_speed_mbps, ping_ms, server_info

        else:
            # Silent mode for daemon/background operations
            st.get_best_server()
            server_info = f"{st.results.server['sponsor']} ({st.results.server['name']}, {st.results.server['country']})"

            download_speed_bps = st.download()
            download_speed_mbps = download_speed_bps / 1_000_000

            upload_speed_bps = st.upload()
            upload_speed_mbps = upload_speed_bps / 1_000_000

            ping_ms = st.results.ping

            return download_speed_mbps, upload_speed_mbps, ping_ms, server_info

    except Exception as e:
        if cli_show:
            display_status(f"An unexpected error occurred: {e}", "error")
        return None, None, None, None


if __name__ == "__main__":
    from ui.console import print_header

    print_header()
    display_status("Starting Internet Speed Test...", "info")

    download, upload, ping, server_info = run_speed_test()

    if download is not None:
        display_results(download, upload, ping, server_info)
    else:
        display_status("Speed test failed.", "error")

    console.input("\n[cyan]Press Enter to exit...[/cyan]")
