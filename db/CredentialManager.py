"""
Credential Manager with Rich TUI
"""

import sqlite3
import os
import sys
import shutil
from getpass import getpass
import csv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.box import ROUNDED

console = Console()


class CredentialManger:
    def __init__(self, db_path=None):
        self.db_path = db_path if db_path else self.get_db_path()
        self.setup_database()

    def get_db_path(self):
        """Get the correct database path based on execution context."""
        if getattr(sys, "frozen", False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        if sys.platform == "win32":
            persistent_db_path = os.path.join(
                os.getenv("APPDATA"), "autologin_script", "credentials.db"
            )
        else:
            persistent_db_path = os.path.expanduser(
                "~/.autologin_script/credentials.db"
            )

        os.makedirs(os.path.dirname(persistent_db_path), exist_ok=True)

        source_db_path = os.path.join(base_dir, "credentials.db")

        if not os.path.exists(persistent_db_path) and os.path.exists(source_db_path):
            shutil.copy(source_db_path, persistent_db_path)

        return persistent_db_path

    def setup_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
                )
            """
            )
            conn.commit()

    def add_credential(self):
        """Add new credentials with Rich prompts."""
        console.print()
        console.print(
            Panel(
                "[cyan]Enter new credentials[/cyan]", box=ROUNDED, border_style="cyan"
            )
        )
        console.print()

        username = Prompt.ask("[green]Username[/green]")
        password = Prompt.ask("[yellow]Password[/yellow]", password=True)

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO credentials
                    (username, password)
                    VALUES (?, ?)""",
                    (username, password),
                )
                conn.commit()
                console.print()
                console.print("[green]✓ Credential added successfully![/green]")

        except sqlite3.IntegrityError:
            console.print()
            console.print("[red]✗ Username already exists![/red]")

    def get_credentials(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username, password FROM credentials")
            return [
                {
                    "username": row[0],
                    "password": row[1],
                }
                for row in cursor.fetchall()
            ]

    def edit_credentials(self):
        """Edit existing credentials with Rich UI."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id, username FROM credentials")
            users = cursor.fetchall()

            if not users:
                console.print()
                console.print("[yellow]⚠ No credentials found to edit.[/yellow]")
                return None

            # Display users table
            console.print()
            table = Table(
                title="[bold cyan]Available Users[/bold cyan]",
                box=ROUNDED,
                border_style="cyan",
                header_style="bold cyan",
            )
            table.add_column("#", style="green bold", justify="center", width=5)
            table.add_column("Username", style="white")

            for i, (_, username) in enumerate(users, 1):
                table.add_row(str(i), username)

            console.print(table)
            console.print()

            try:
                selection = int(
                    Prompt.ask("[yellow]Select a user to edit (number)[/yellow]")
                )
                if selection < 1 or selection > len(users):
                    console.print("[red]✗ Invalid selection.[/red]")
                    return None

                user_id, username = users[selection - 1]

                cursor.execute(
                    "SELECT password FROM credentials WHERE id = ?", (user_id,)
                )
                current_password = cursor.fetchone()[0]

                console.print()
                console.print(
                    Panel(
                        f"[cyan]Editing credentials for: [bold]{username}[/bold][/cyan]",
                        box=ROUNDED,
                        border_style="cyan",
                    )
                )
                console.print()

                new_username = Prompt.ask(
                    f"[green]New username[/green] [dim](leave empty to keep '{username}')[/dim]",
                    default="",
                )
                console.print(f"[dim]Current password: {current_password}[/dim]")
                new_password = Prompt.ask(
                    "[yellow]New password[/yellow] [dim](leave empty to keep current)[/dim]",
                    password=True,
                    default="",
                )

                changes_made = False

                if new_username and new_username != username:
                    try:
                        cursor.execute(
                            "UPDATE credentials SET username = ? WHERE id = ?",
                            (new_username, user_id),
                        )
                        username = new_username
                        changes_made = True
                        console.print("[green]✓ Username updated successfully![/green]")
                    except sqlite3.IntegrityError:
                        console.print(
                            "[red]✗ Error: That username already exists! Username not updated.[/red]"
                        )

                if new_password:
                    cursor.execute(
                        "UPDATE credentials SET password = ? WHERE id = ?",
                        (new_password, user_id),
                    )
                    current_password = new_password
                    changes_made = True
                    console.print("[green]✓ Password updated successfully![/green]")

                if changes_made:
                    conn.commit()
                else:
                    console.print("[dim]No changes made.[/dim]")

                return {"username": username, "password": current_password}

            except (ValueError, IndexError):
                console.print("[red]✗ Invalid selection. Please try again.[/red]")
                return None

    def delete_credential(self):
        """Delete credentials with Rich UI."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id, username FROM credentials")
            users = cursor.fetchall()

            if not users:
                console.print()
                console.print("[yellow]⚠ No credentials found to delete.[/yellow]")
                return False

            # Display users table
            console.print()
            table = Table(
                title="[bold cyan]Available Users[/bold cyan]",
                box=ROUNDED,
                border_style="cyan",
                header_style="bold cyan",
            )
            table.add_column("#", style="green bold", justify="center", width=5)
            table.add_column("Username", style="white")

            for i, (_, username) in enumerate(users, 1):
                table.add_row(str(i), username)

            console.print(table)
            console.print()

            try:
                selection = int(
                    Prompt.ask(
                        "[yellow]Select a user to delete (number)[/yellow] [dim]or 0 to cancel[/dim]"
                    )
                )
                if selection == 0:
                    console.print("[dim]Deletion cancelled.[/dim]")
                    return False

                if selection < 1 or selection > len(users):
                    console.print("[red]✗ Invalid selection.[/red]")
                    return False

                user_id, username = users[selection - 1]

                if Confirm.ask(
                    f"[red]Are you sure you want to delete credentials for '[bold]{username}[/bold]'?[/red]"
                ):
                    cursor.execute("DELETE FROM credentials WHERE id = ?", (user_id,))
                    conn.commit()
                    console.print()
                    console.print(
                        f"[green]✓ Credentials for '{username}' deleted successfully![/green]"
                    )
                    return True
                else:
                    console.print("[dim]Deletion cancelled.[/dim]")
                    return False

            except (ValueError, IndexError):
                console.print("[red]✗ Invalid selection. Please try again.[/red]")
                return False

    def export_to_csv(self, output_path=None):
        """Export credentials to CSV with Rich feedback."""
        if not output_path:
            output_path = os.path.join(os.path.dirname(self.db_path), "credentials.csv")

        credentials = self.get_credentials()

        if not credentials:
            console.print("[yellow]⚠ No credentials found to export.[/yellow]")
            return None

        try:
            with open(output_path, "w", newline="") as csvfile:
                fieldnames = ["username", "password"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for cred in credentials:
                    writer.writerow(cred)

            console.print(
                f"[green]✓ Credentials exported successfully to {output_path}[/green]"
            )
            return output_path
        except Exception as e:
            console.print(f"[red]✗ Error exporting credentials: {e}[/red]")
            return None

    def import_from_csv(self, csv_path):
        """Import credentials from CSV with Rich feedback."""
        if not os.path.exists(csv_path):
            console.print(f"[red]✗ Error: CSV file not found at {csv_path}[/red]")
            return (0, 0)

        try:
            with open(csv_path, "r", newline="") as csvfile:
                reader = csv.DictReader(csvfile)
                field_mapping = {}
                for field in reader.fieldnames:
                    field_lower = field.strip().lower()

                    if field_lower in ["username", "userid (enrolment number)"]:
                        field_mapping["username"] = field

                    elif field_lower == "password":
                        field_mapping["password"] = field

                if "username" not in field_mapping or "password" not in field_mapping:
                    console.print(
                        "[red]✗ Error: CSV must contain 'username' (or 'UserID (Enrolment Number)') and 'password' columns[/red]"
                    )
                    return False

                records_added = 0
                records_skipped = 0

                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    for row in reader:
                        try:
                            username = row[field_mapping["username"]]
                            password = row[field_mapping["password"]]
                            cursor.execute(
                                "INSERT INTO credentials (username, password) VALUES (?, ?)",
                                (username, password),
                            )
                            records_added += 1
                        except sqlite3.IntegrityError:
                            records_skipped += 1
                    conn.commit()

                # Display results in a panel
                result_text = Text()
                result_text.append("✓ ", style="green")
                result_text.append("Import completed\n\n", style="green")
                result_text.append(f"  Records added:   ", style="cyan")
                result_text.append(f"{records_added}\n", style="bold green")
                result_text.append(f"  Duplicates skipped: ", style="cyan")
                result_text.append(
                    f"{records_skipped}",
                    style="yellow" if records_skipped > 0 else "dim",
                )

                console.print()
                console.print(Panel(result_text, box=ROUNDED, border_style="green"))
                return True

        except Exception as e:
            console.print(f"[red]✗ Error importing CSV data: {e}[/red]")
            return (0, 0)
