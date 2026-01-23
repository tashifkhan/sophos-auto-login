"""
Rich Console Configuration and UI Utilities for Sophos Auto Login
"""

import os
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.theme import Theme
from rich.text import Text
from rich.style import Style
from rich.box import ROUNDED, DOUBLE, HEAVY

# Custom theme for consistent styling
custom_theme = Theme(
    {
        "info": "cyan",
        "success": "green",
        "warning": "yellow",
        "error": "red bold",
        "title": "bold cyan",
        "header": "bold white on blue",
        "menu.option": "green",
        "menu.text": "white",
        "highlight": "bold magenta",
        "credential.id": "bold green",
        "credential.user": "cyan",
        "credential.pass": "yellow",
        "status.running": "bold green",
        "status.stopped": "bold red",
        "status.label": "cyan",
        "speed.download": "green",
        "speed.upload": "yellow",
        "speed.ping": "magenta",
    }
)

# Main console instance - use this throughout the app
console = Console(theme=custom_theme)

# Error console for stderr output
error_console = Console(stderr=True, theme=custom_theme)


def clear_screen():
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def print_header(clear: bool = True):
    """Print the application header with a styled panel."""
    if clear:
        clear_screen()

    header_text = Text()
    header_text.append("⚡ ", style="yellow")
    header_text.append("SOPHOS AUTO LOGIN", style="bold white")
    header_text.append(" ⚡", style="yellow")

    panel = Panel(
        header_text,
        box=DOUBLE,
        style="cyan",
        padding=(0, 2),
    )
    console.print(panel)
    console.print()


def print_status(message: str, status_type: str = "info"):
    """
    Print a styled status message in a panel.

    Args:
        message: The message to display
        status_type: One of 'success', 'error', 'warning', 'info'
    """
    styles = {
        "success": ("✓", "green", "green"),
        "error": ("✗", "red", "red"),
        "warning": ("⚠", "yellow", "yellow"),
        "info": ("ℹ", "cyan", "cyan"),
    }

    icon, text_style, border_style = styles.get(status_type, styles["info"])

    content = Text()
    content.append(f"{icon} ", style=text_style)
    content.append(message, style=text_style)

    panel = Panel(
        content,
        box=ROUNDED,
        border_style=border_style,
        padding=(0, 2),
    )
    console.print()
    console.print(panel)


def print_menu(options: list[tuple[str, str]], title: str = "Choose an option") -> str:
    """
    Print an interactive menu and get user choice.

    Args:
        options: List of (key, description) tuples
        title: Menu title

    Returns:
        User's input string
    """
    console.print(f"\n[yellow]{title}:[/yellow]")

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="green bold", width=5)
    table.add_column("Option", style="white")

    for key, description in options:
        table.add_row(f"[{key}]", description)

    console.print(table)

    return console.input(f"\n[yellow]Enter your choice (1-{len(options)}): [/yellow]")


def create_table(
    title: str = None,
    columns: list[tuple[str, str]] = None,
    show_header: bool = True,
    box_style=ROUNDED,
) -> Table:
    """
    Create a styled table.

    Args:
        title: Optional table title
        columns: List of (name, style) tuples for columns
        show_header: Whether to show column headers
        box_style: Rich box style for borders

    Returns:
        Configured Rich Table instance
    """
    table = Table(
        title=title,
        show_header=show_header,
        header_style="bold cyan",
        box=box_style,
        border_style="cyan",
    )

    if columns:
        for name, style in columns:
            table.add_column(name, style=style, justify="center")

    return table


def format_time(minutes: int) -> str:
    """Format minutes into a human-readable time string."""
    hrs = minutes // 60
    mins = minutes % 60
    if hrs == 0:
        return f"{mins} minutes"
    return f"{hrs} hours {mins} minutes"


def create_credentials_table(credentials: list[dict]) -> Table:
    """Create a formatted table of credentials."""
    table = create_table(
        columns=[
            ("ID", "green bold"),
            ("Username", "cyan"),
            ("Password", "yellow"),
        ]
    )

    for i, cred in enumerate(credentials):
        table.add_row(
            str(i + 1),
            cred["username"],
            cred["password"],
        )

    return table


def create_status_panel(status: dict, with_details: bool = True) -> Panel:
    """
    Create a formatted status panel for daemon status.

    Args:
        status: Status dictionary from get_daemon_status()
        with_details: Whether to include detailed information
    """
    # Build main status line
    if status["running"]:
        icon = "✓"
        style = "green"
        state = "Running"
    else:
        icon = "⨯"
        style = "red"
        state = "Not running"

    content = Text()
    content.append(f"{icon} ", style=style)
    content.append(state, style=f"bold {style}")

    if status.get("connection_status"):
        conn_style = "green" if status["connection_status"] == "Connected" else "red"
        conn_icon = "✓" if status["connection_status"] == "Connected" else "✗"
        content.append(" │ Network: ", style="dim")
        content.append(f"{conn_icon} {status['connection_status']}", style=conn_style)

    if not with_details:
        return Panel(content, title="[bold]Daemon Status[/bold]", border_style="cyan")

    # Add details table
    from rich.columns import Columns

    details = Table(show_header=False, box=None, padding=(0, 1))
    details.add_column("Label", style="cyan")
    details.add_column("Value", style="white")

    if status.get("last_activity"):
        time_ago = status.get("time_since_activity", "")
        details.add_row("Last Activity:", f"{status['last_activity']} ({time_ago} ago)")

    if status.get("last_action"):
        details.add_row("Last Action:", status["last_action"])

    if status.get("active_credential"):
        details.add_row("Active Credential:", status["active_credential"])

    if status.get("runtime"):
        details.add_row("Daemon Runtime:", status["runtime"])

    from rich.console import Group

    group = Group(content, Text(), details)

    return Panel(
        group,
        title="[bold]Daemon Status[/bold]",
        border_style="cyan",
        box=ROUNDED,
    )
