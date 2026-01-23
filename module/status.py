"""
Daemon Status Module with Rich TUI
"""

import os
import re
from pathlib import Path
from datetime import datetime
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.box import ROUNDED
from rich.console import Group

# Import shared console
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.console import console


def get_daemon_status(with_colors: bool = True) -> dict:
    """
    Get the running status of the sophos-autologin daemon by reading from the log file.

    Args:
        with_colors (bool): Whether to include Rich markup in status strings

    Returns:
        dict: A dictionary containing status information like:
            - running (bool): Whether the daemon appears to be active
            - last_activity (str): Timestamp of the last log entry
            - last_action (str): The last action performed
            - error (str): Any error message if present
            - status_str (str): A human-readable status string
            - time_since_activity (str): Human-readable time since last activity
            - runtime (str): The daemon runtime if available
            - connection_status (str): Current connection status (Connected/Disconnected)
            - active_credential (str): Currently active credential being used
    """
    log_path = Path(
        os.path.join(Path.home(), ".sophos-autologin", "sophos-autologin.log")
    )

    status = {
        "running": False,
        "last_activity": None,
        "last_action": None,
        "error": None,
        "status_str": "Unknown",
        "time_since_activity": None,
        "runtime": None,
        "connection_status": None,
        "active_credential": None,
    }

    if not log_path.exists():
        status["error"] = "Log file not found, daemon may not be running"
        status["status_str"] = _create_status_text(
            "Not running (no log file)", False, with_colors
        )
        return status

    try:
        # Read the last few lines from the log file (most recent entries)
        with open(log_path, "r") as log_file:
            lines = log_file.readlines()[-20:] if log_file.readable() else []

        if not lines:
            status["error"] = "Log file is empty"
            status["status_str"] = _create_status_text(
                "Not running (empty log file)", False, with_colors
            )
            return status

        # Extract timestamp from the most recent log entry
        timestamp_pattern = r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"
        for line in reversed(lines):
            timestamp_match = re.search(timestamp_pattern, line)
            if timestamp_match:
                timestamp_str = timestamp_match.group(1)
                status["last_activity"] = timestamp_str
                break

        # Check for connection status, runtime, and active credential
        connection_pattern = r"CONNECTION CHECK \| Status: ([✓✗]) (Connected|Disconnected) \| Runtime: (.*?)$"
        credential_pattern = r"Active credential: (.*?)$"

        for line in reversed(lines):
            conn_match = re.search(connection_pattern, line)
            if conn_match and not status.get("connection_status"):
                status["connection_status"] = conn_match.group(2)
                status["runtime"] = conn_match.group(3)
                continue

            cred_match = re.search(credential_pattern, line)
            if cred_match and not status.get("active_credential"):
                status["active_credential"] = cred_match.group(1)
                continue

            if "➤ Internet is connected" in line:
                status["last_action"] = "Internet is connected"
                status["running"] = True
                if not status.get("connection_status"):
                    status["connection_status"] = "Connected"

            elif "⟳ Performing scheduled re-login" in line:
                status["last_action"] = "Performing scheduled re-login"
                status["running"] = True

            elif "LOGIN ATTEMPT" in line:
                login_match = re.search(r"LOGIN ATTEMPT #(\d+)", line)
                if login_match:
                    attempt_num = login_match.group(1)
                    status["last_action"] = f"Login attempt #{attempt_num}"
                else:
                    status["last_action"] = "Login attempt"
                status["running"] = True

            elif "login successful" in line.lower():
                status["last_action"] = "Login successful"
                status["running"] = True
                if not status.get("connection_status"):
                    status["connection_status"] = "Connected"

            elif "daemon started" in line.lower():
                status["last_action"] = "Daemon started"
                status["running"] = True
                break

            elif "daemon stopped" in line.lower():
                status["last_action"] = "Daemon stopped"
                status["running"] = False
                break

            if (
                status["last_action"]
                and status["connection_status"]
                and status["active_credential"]
                and status["runtime"]
            ):
                break

        # Check if daemon might be stuck
        if status["last_activity"]:
            try:
                last_time = datetime.strptime(
                    status["last_activity"], "%Y-%m-%d %H:%M:%S"
                )
                current_time = datetime.now()
                time_diff_seconds = (current_time - last_time).total_seconds()
                time_diff_minutes = time_diff_seconds / 60

                status["time_since_activity"] = _format_time_difference(
                    time_diff_seconds
                )

                if time_diff_minutes > 30:
                    status["running"] = False
                    status["error"] = (
                        f"No activity for {status['time_since_activity']}, daemon may be stuck"
                    )
            except ValueError:
                pass

        # Create status string
        status["status_str"] = _create_status_text(
            "Running" if status["running"] else "Not running",
            status["running"],
            with_colors,
        )

    except Exception as e:
        status["error"] = f"Error reading log file: {str(e)}"
        status["status_str"] = _create_status_text(
            f"Error: {str(e)}", False, with_colors
        )

    return status


def _format_time_difference(seconds: float) -> str:
    """Format a time difference in seconds to a human-readable string."""
    if seconds < 60:
        return f"{int(seconds)} seconds"
    elif seconds < 3600:
        return f"{int(seconds/60)} minutes"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours} hours{f', {minutes} minutes' if minutes else ''}"
    else:
        days = int(seconds / 86400)
        hours = int((seconds % 86400) / 3600)
        return f"{days} days{f', {hours} hours' if hours else ''}"


def _create_status_text(
    message: str, is_running: bool, with_colors: bool = True
) -> str:
    """Create a status text string with optional Rich markup."""
    if is_running:
        icon = "✓"
        style = "green" if with_colors else ""
    else:
        icon = "⨯"
        style = "red" if with_colors else ""

    if with_colors:
        return f"[{style}]{icon} {message}[/{style}]"
    return f"{icon} {message}"


def print_daemon_status(status: dict):
    """Print a formatted daemon status display using Rich."""
    # Main status line
    if status["running"]:
        icon = "✓"
        style = "green"
        state = "Running"
    else:
        icon = "⨯"
        style = "red"
        state = "Not running"

    status_text = Text()
    status_text.append(f"{icon} ", style=style)
    status_text.append(state, style=f"bold {style}")

    if status.get("connection_status"):
        conn_style = "green" if status["connection_status"] == "Connected" else "red"
        conn_icon = "✓" if status["connection_status"] == "Connected" else "✗"
        status_text.append(" │ Network: ", style="dim")
        status_text.append(
            f"{conn_icon} {status['connection_status']}", style=conn_style
        )

    console.print(status_text)

    # Error/warning
    if status.get("error"):
        console.print()
        console.print(f"[bold red]⚠️  WARNING:[/bold red]")
        console.print(f"  [red]{status['error']}[/red]")

    # Details table
    console.print()
    console.print("[bold]DETAILS:[/bold]")

    details_table = Table(show_header=False, box=None, padding=(0, 1))
    details_table.add_column("Label", style="cyan", width=20)
    details_table.add_column("Value", style="white")

    if status.get("last_activity"):
        time_ago = status.get("time_since_activity", "")
        details_table.add_row(
            "Last Activity:", f"[bold]{status['last_activity']}[/bold] ({time_ago} ago)"
        )

    if status.get("last_action"):
        details_table.add_row("Last Action:", status["last_action"])

    if status.get("connection_status"):
        conn_style = "green" if status["connection_status"] == "Connected" else "red"
        details_table.add_row(
            "Network Status:",
            f"[{conn_style} bold]{status['connection_status']}[/{conn_style} bold]",
        )

    if status.get("active_credential"):
        details_table.add_row(
            "Active Credential:", f"[bold]{status['active_credential']}[/bold]"
        )

    if status.get("runtime"):
        details_table.add_row("Daemon Runtime:", status["runtime"])

    console.print(details_table)


if __name__ == "__main__":
    from ui.console import print_header

    print_header()
    console.print("[bold cyan]=== DAEMON STATUS ===[/bold cyan]")
    console.print()

    status = get_daemon_status()
    print_daemon_status(status)

    console.print()
    console.rule(style="dim")
