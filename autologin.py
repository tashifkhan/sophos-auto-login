import os
import sys
import time
import signal
import module
import atexit
import logging
import datetime
import argparse
import db.CredentialManager as CredManager
from module import state
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.box import ROUNDED, DOUBLE
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

# Initialize Rich console
console = Console()

# Import custom theme from ui module
from ui.console import (
    print_header,
    print_status,
    create_table,
    create_credentials_table,
    format_time,
)

# Flag to prevent multiple signal handlers from running
signal_handler_running = False


def parse_arguments():
    parser = argparse.ArgumentParser(description="Sophos Auto Login Tool")
    parser.add_argument(
        "--start",
        "-s",
        action="store_true",
        help="Start auto-login process immediately",
    )
    parser.add_argument("--add", "-a", action="store_true", help="Add new credentials")
    parser.add_argument(
        "--edit", "-e", action="store_true", help="Edit existing credentials"
    )
    parser.add_argument(
        "--delete", "-del", action="store_true", help="Delete credentials"
    )
    parser.add_argument(
        "--export",
        "-x",
        type=str,
        nargs="?",
        const="",
        help="Export credentials to CSV (optional path)",
    )
    parser.add_argument(
        "--import",
        "-i",
        dest="import_csv",
        type=str,
        help="Import credentials from CSV file",
    )
    parser.add_argument(
        "--show", "-l", action="store_true", help="Display all stored credentials"
    )
    parser.add_argument(
        "--daemon",
        "-d",
        action="store_true",
        help="Run auto-login process in background (daemon mode)",
    )
    parser.add_argument(
        "--exit",
        "-q",
        action="store_true",
        help="Exit the daemon process and logout all credentials",
    )
    parser.add_argument(
        "--logout", "-lo", action="store_true", help="Logout from all credentials"
    )
    parser.add_argument("--speedtest", "-t", action="store_true", help="Run speed test")
    parser.add_argument(
        "--status", "-st", action="store_true", help="Display daemon status"
    )

    return parser.parse_args()


def daemonize():
    """Convert the current process to a daemon process."""
    if os.name != "posix":
        console.print("[red]Daemon mode is only supported on Unix-like systems.[/red]")
        sys.exit(1)

    # First fork
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError as e:
        console.print(f"[red]Fork #1 failed: {e}[/red]")
        sys.exit(1)

    os.chdir("/")
    os.setsid()
    os.umask(0)

    # Second fork
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError as e:
        console.print(f"[red]Fork #2 failed: {e}[/red]")
        sys.exit(1)

    sys.stdout.flush()
    sys.stderr.flush()

    log_dir = os.path.expanduser("~/.sophos-autologin")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, "sophos-autologin.log")
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s │ %(levelname)-8s │ %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.info("╔══════════════════════════════════════════════════════════╗")
    logging.info("║                 SOPHOS AUTO LOGIN DAEMON                 ║")
    logging.info("╚══════════════════════════════════════════════════════════╝")
    logging.info("Daemon started")

    si = open(os.devnull, "r")
    so = open(os.devnull, "a+")
    se = open(os.devnull, "a+")

    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

    pid_file = os.path.join(log_dir, "sophos-autologin.pid")
    with open(pid_file, "w") as f:
        f.write(str(os.getpid()))

    logging.info(f"Daemon process started with PID {os.getpid()}")
    return log_file, pid_file


def run_auto_login(credential_manager, daemon_mode=False):
    credentials = credential_manager.get_credentials()
    state.update_active_credential(None, credentials)
    cred_index = None

    if len(credentials) == 0:
        if daemon_mode:
            logging.error("No credentials found. Daemon exiting.")
            return None
        else:
            print_status("No credentials found. Please add credentials first.", "error")
            return None

    if not daemon_mode:
        console.print(
            "[yellow]Starting auto-login process. Press Ctrl+C to stop.[/yellow]"
        )
    else:
        module.send_notification("Sophos Auto Login", "Daemon started")
        logging.info("Starting auto-login process in daemon mode")

    count = 0
    last_login_time = time.time()
    start_time = time.time()

    CONNECTION_CHECK_INTERVAL = 90
    FORCED_RELOGIN_INTERVAL = 30 * 60
    last_connection_check = time.time()

    # Initial login attempt
    stop, cred_index = module.login(credentials)
    if cred_index is not None:
        active_username = credentials[cred_index]["username"]
        if not daemon_mode:
            print_status(
                f"Logged in with credential ID #{cred_index+1} ({active_username})",
                "success",
            )
        else:
            logging.info(
                f"Logged in with credential ID #{cred_index+1} ({active_username})"
            )

        state.update_active_credential(cred_index, credentials)

        signal.signal(
            signal.SIGINT,
            lambda sig, frame: module.exit_handler(cred_index, credentials, sig, frame),
        )
        signal.signal(
            signal.SIGTERM,
            lambda sig, frame: module.exit_handler(cred_index, credentials, sig, frame),
        )

        console.print(
            f"[dim]Debug: Active credential index is {cred_index}, username: {credentials[cred_index]['username']}[/dim]"
        )

    try:
        while True:
            current_time = time.time()
            count += 1
            running_time_seconds = current_time - start_time
            running_time_mins = running_time_seconds / 60
            duration = format_time(int(running_time_mins))

            if current_time - last_connection_check >= CONNECTION_CHECK_INTERVAL:
                has_internet = module.check_internet_connection()
                last_connection_check = current_time

                if not daemon_mode:
                    status_icon = (
                        "[green]✓ Connected[/green]"
                        if has_internet
                        else "[red]✗ Disconnected[/red]"
                    )

                    console.print()
                    console.print("[cyan bold]CONNECTION CHECK[/cyan bold]")
                    console.print(f"Status: {status_icon}")
                    console.print(f"Runtime: {duration}")

                    if cred_index is not None and 0 <= cred_index < len(credentials):
                        active_username = credentials[cred_index]["username"]
                        console.print(f"Active: ID #{cred_index+1} ({active_username})")
                else:
                    status = "✓ Connected" if has_internet else "✗ Disconnected"
                    logging.info(
                        f"CONNECTION CHECK | Status: {status} | Runtime: {duration}"
                    )
                    if cred_index is not None and 0 <= cred_index < len(credentials):
                        active_username = credentials[cred_index]["username"]
                        logging.info(
                            f"Active credential: ID #{cred_index+1} ({active_username})"
                        )

                force_relogin = (
                    current_time - last_login_time >= FORCED_RELOGIN_INTERVAL
                )

                if has_internet and not force_relogin:
                    if not daemon_mode:
                        console.print(
                            "[green]➤ Internet is connected. No login needed.[/green]"
                        )
                    else:
                        logging.info("➤ Internet is connected. No login needed.")
                    time.sleep(10)
                    continue
                elif force_relogin:
                    message = "⟳ Performing scheduled re-login"
                    if not daemon_mode:
                        console.print(f"\n[yellow]{message}[/yellow]")
                    else:
                        logging.info(message)

                if (not has_internet) or force_relogin:
                    if not daemon_mode:
                        console.print(
                            f"\n[cyan]Login attempt #{count} | Running for: {duration}[/cyan]"
                        )
                    else:
                        logging.info(
                            f"LOGIN ATTEMPT #{count} | Running for: {duration}"
                        )

                    stop, cred_index = module.login(credentials)
                    last_login_time = time.time()

                    if cred_index is not None and 0 <= cred_index < len(credentials):
                        active_username = credentials[cred_index]["username"]
                        if not daemon_mode:
                            print_status(
                                f"Logged in with ID #{cred_index+1} ({active_username})",
                                "success",
                            )
                        else:
                            logging.info(
                                f"✓ Logged in with credential ID #{cred_index+1} ({active_username})"
                            )

                    if stop:
                        if len(credentials) == 0:
                            if daemon_mode:
                                module.send_notification(
                                    "Sophos Auto Login",
                                    "No credentials found. Daemon exiting.",
                                )
                                logging.error("No credentials found. Daemon exiting.")
                            else:
                                print_status("No credentials found.", "error")
                        else:
                            module.logout(credentials[cred_index])
                            if daemon_mode:
                                module.send_notification(
                                    "Sophos Auto Login",
                                    f"Logged out {credentials[cred_index]['username']} & Exiting",
                                )
                                logging.info("Auto-login stopped.")
                            else:
                                print_status("Auto-login stopped.", "warning")
                        break

            time.sleep(10)

    except KeyboardInterrupt:
        if not daemon_mode:
            print_status("Auto-login interrupted by user.", "warning")
        else:
            module.send_notification("Sophos Auto Login", "Daemon interrupted by user.")
            logging.info("Auto-login daemon interrupted by user.")

    return cred_index


def signal_handler(sig, frame):
    if state.signal_handler_running:
        console.print(
            "[dim]Signal handler already running, ignoring additional signals...[/dim]"
        )
        return

    state.signal_handler_running = True

    try:
        idx, credential = state.get_active_credential()
        if idx is not None and credential is not None:
            console.print(f"\n[yellow]Exiting...[/yellow]")
            console.print(f"Logging out credential: {credential['username']}")
            result = module.logout(credential)
            if result:
                console.print(
                    f"[green]Successfully logged out: {credential['username']}[/green]"
                )
            else:
                console.print(
                    f"[yellow]Failed to logout: {credential['username']}[/yellow]"
                )
        else:
            console.print("\n[yellow]Exiting...[/yellow]")
            console.print("No active credential to logout.")
            console.print("[green]Logout successful.[/green]")

    except Exception as e:
        console.print(f"[red]Error during logout: {e}[/red]")

    finally:
        state.signal_handler_running = False
        sys.exit(0)


def print_menu_rich():
    """Print the interactive menu and get user choice."""
    console.print("\n[yellow]Choose an option:[/yellow]")

    menu_items = [
        ("1", "Add new login credentials"),
        ("2", "Start auto-login process"),
        ("3", "Edit existing credentials"),
        ("4", "Delete credentials"),
        ("5", "Export credentials to CSV"),
        ("6", "Import credentials from CSV"),
        ("7", "Show stored credentials"),
        ("8", "Run SpeedTest"),
        ("9", "Logout from all credentials"),
        ("10", "Check daemon status"),
        ("11", "Exit"),
    ]

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Key", style="green bold", width=6)
    table.add_column("Option", style="white")

    for key, description in menu_items:
        table.add_row(f"[{key}]", description)

    console.print(table)

    return Prompt.ask("\n[yellow]Enter your choice (1-11)[/yellow]")


def show_spinner(seconds: float, message: str = "Processing"):
    """Show a spinner for a given duration."""
    with console.status(f"[cyan]{message}...[/cyan]", spinner="dots"):
        time.sleep(seconds)


def main():
    args = parse_arguments()

    credential_manager = CredManager.CredentialManger()
    credentials = credential_manager.get_credentials()
    state.update_active_credential(None, credentials)
    running = True

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Status check command
    if args.status:
        print_header()
        console.print("[cyan bold]=== DAEMON STATUS ===[/cyan bold]\n")

        status = module.get_daemon_status()
        from module.status import print_daemon_status

        print_daemon_status(status)

        console.print()
        console.rule(style="dim")
        return

    if args.exit:
        print_header()
        console.print("[cyan bold]=== STOPPING DAEMON PROCESS ===[/cyan bold]\n")

        print_status("Exiting...", "warning")
        creds = credential_manager.get_credentials()
        fail = False

        try:
            idx, credential = state.get_active_credential()
            if idx is not None and credential is not None:
                console.print(f"Logging out credential: {credential['username']}")
                result = module.logout(credential)
                if result == "Fail":
                    console.print(
                        "[red]Warning: Timeout occurred while logging out.[/red]"
                    )
                    fail = True
                elif result is False:
                    console.print("[yellow]Warning: Failed to logout user.[/yellow]")
                    fail = True
                else:
                    console.print(
                        f"[green]Successfully logged out: {credential['username']}[/green]"
                    )
            else:
                console.print("No active credential to logout.")

            if not fail:
                module.send_notification(
                    "Sophos Auto Login", "You have been logged out & Exited"
                )
            else:
                module.send_notification("Sophos Auto Login", "Logout failed. Exited.")

        except Exception as e:
            console.print(f"[red]Error during logout: {e}[/red]")
            module.send_notification("Sophos Auto Login", f"Error during logout: {e}")
            fail = True

        finally:
            if fail:
                console.print("[yellow]Logout failed, but exiting anyway.[/yellow]")
            else:
                console.print("[green]Logout successful.[/green]")

        running = False

        if not sys.platform.startswith("win"):
            module.deamon_exit()

    # Daemon mode
    if args.daemon:
        if args.start:
            try:
                log_file, pid_file = daemonize()
                console.print(
                    f"[green]Daemon started. Log file: {log_file}, PID file: {pid_file}[/green]"
                )

                def daemon_exit_handler():
                    try:
                        if os.path.exists(pid_file):
                            with open(pid_file, "r") as f:
                                if int(f.read().strip()) == os.getpid():
                                    module.send_notification(
                                        "Sophos Auto Login", "Daemon has exited"
                                    )
                                    logging.info("Daemon process has exited")
                    except Exception as e:
                        logging.error(f"Error in daemon exit handler: {e}")

                atexit.register(daemon_exit_handler)

                try:
                    cred_index = run_auto_login(credential_manager, daemon_mode=True)
                    state.update_active_credential(
                        cred_index, credential_manager.get_credentials()
                    )
                except Exception as e:
                    module.send_notification(
                        "Sophos Auto Login", f"Daemon error: {str(e)}"
                    )
                    logging.error(f"Daemon error during auto-login: {e}")
                    raise

            except KeyboardInterrupt:
                module.send_notification(
                    "Sophos Auto Login", "Daemon was stopped by keyboard interrupt"
                )
                logging.info("Daemon stopped by keyboard interrupt")
                sys.exit(0)
            except Exception as e:
                error_msg = f"Daemon error: {str(e)}"
                try:
                    module.send_notification("Sophos Auto Login", error_msg)
                except:
                    pass
                logging.error(error_msg)
                sys.exit(1)
        else:
            console.print("[red]--daemon must be used with --start[/red]")
            sys.exit(1)
        return

    if args.show:
        print_header()
        console.print("[cyan bold]=== STORED CREDENTIALS ===[/cyan bold]\n")

        if len(credentials) == 0:
            print_status("No credentials found.", "warning")
            return

        table = create_credentials_table(credentials)
        console.print(table)
        console.print()
        print_status(f"Total credentials: {len(credentials)}", "info")
        return

    elif args.add:
        print_header()
        console.print("[cyan bold]=== ADD NEW CREDENTIALS ===[/cyan bold]\n")
        credential_manager.add_credential()
        credentials = credential_manager.get_credentials()
        state.update_active_credential(None, credentials)
        show_spinner(1, "Updating credentials")
        print_status("Credentials added successfully", "success")
        return

    elif args.edit:
        print_header()
        console.print("[cyan bold]=== EDIT CREDENTIALS ===[/cyan bold]\n")
        result = credential_manager.edit_credentials()
        credentials = credential_manager.get_credentials()
        state.update_active_credential(None, credentials)
        if result:
            show_spinner(1, "Updating credentials")
            print_status("Credentials updated successfully", "success")
        return

    elif args.delete:
        print_header()
        console.print("[cyan bold]=== DELETE CREDENTIALS ===[/cyan bold]\n")
        credential_manager.delete_credential()
        credentials = credential_manager.get_credentials()
        state.update_active_credential(None, credentials)
        show_spinner(1, "Updating credentials")
        print_status("Credentials deleted", "success")
        return

    elif args.export is not None:
        print_header()
        console.print("[cyan bold]=== EXPORT CREDENTIALS ===[/cyan bold]\n")

        show_spinner(1, "Exporting")

        if args.export:
            result = credential_manager.export_to_csv(args.export)
        else:
            result = credential_manager.export_to_csv()

        if result:
            print_status(f"Credentials exported to: {result}", "success")
        return

    elif args.import_csv:
        print_header()
        console.print("[cyan bold]=== IMPORT CREDENTIALS ===[/cyan bold]\n")

        if os.path.exists(args.import_csv):
            show_spinner(1, "Importing")
            credential_manager.import_from_csv(args.import_csv)
            credentials = credential_manager.get_credentials()
            state.update_active_credential(None, credentials)
            print_status("Import process completed", "success")
        else:
            print_status(f"File not found: {args.import_csv}", "error")
        return

    elif args.speedtest:
        print_header()
        console.print("[cyan bold]=== RUNNING SPEED TEST ===[/cyan bold]\n")

        download, upload, ping, server_info = module.speed_test()

        if download is not None and upload is not None and ping is not None:
            module.speedtest_results(download, upload, ping, server_info)
        else:
            print_status("Speed test failed", "error")
        return

    elif args.logout:
        print_header()
        console.print("[cyan bold]=== LOGGING OUT ===[/cyan bold]\n")

        creds = credential_manager.get_credentials()
        fail = False

        try:
            for cred in creds:
                console.print(f"Logging out credential: {cred['username']}")
                result = module.logout(cred)
                if result == "Fail":
                    console.print(
                        "[red]Warning: Timeout occurred while logging out.[/red]"
                    )
                    fail = True
                elif result is False:
                    console.print("[yellow]Warning: Failed to logout user.[/yellow]")
                    fail = True
                else:
                    console.print(
                        f"[green]Successfully logged out: {cred['username']}[/green]"
                    )

            if not fail:
                module.send_notification(
                    "Sophos Auto Login", "You have been logged out"
                )
                print_status("All users logged out successfully", "success")
            else:
                module.send_notification("Sophos Auto Login", "Logout failed.")
                print_status("Some users failed to log out", "warning")

        except Exception as e:
            console.print(f"[red]Error during logout: {e}[/red]")
            fail = True

        console.print("[yellow]Exiting program...[/yellow]")
        sys.exit(0)

    elif args.start:
        print_header()
        console.print("[cyan bold]=== AUTO-LOGIN PROCESS ===[/cyan bold]\n")
        cred_index = run_auto_login(credential_manager)
        return

    # Interactive menu loop
    while running:
        print_header()

        cred_count = len(credentials)
        if cred_count > 0:
            console.print(f"[blue]You have {cred_count} stored credential(s)[/blue]")
        else:
            console.print(
                "[yellow]No credentials stored yet. Please add credentials.[/yellow]"
            )

        choice = print_menu_rich()

        if choice == "1":
            print_header()
            console.print("[cyan bold]=== ADD NEW CREDENTIALS ===[/cyan bold]\n")
            credential_manager.add_credential()
            credentials = credential_manager.get_credentials()
            state.update_active_credential(None, credentials)
            show_spinner(1, "Updating credentials")

        elif choice == "2":
            print_header()
            console.print("[cyan bold]=== AUTO-LOGIN PROCESS ===[/cyan bold]\n")
            run_auto_login(credential_manager)

        elif choice == "3":
            print_header()
            console.print("[cyan bold]=== EDIT CREDENTIALS ===[/cyan bold]\n")
            result = credential_manager.edit_credentials()
            credentials = credential_manager.get_credentials()
            state.update_active_credential(None, credentials)
            if result:
                show_spinner(1, "Updating credentials")

        elif choice == "4":
            print_header()
            console.print("[cyan bold]=== DELETE CREDENTIALS ===[/cyan bold]\n")
            credential_manager.delete_credential()
            credentials = credential_manager.get_credentials()
            state.update_active_credential(None, credentials)
            show_spinner(1, "Updating credentials")

        elif choice == "5":
            print_header()
            console.print("[cyan bold]=== EXPORT CREDENTIALS ===[/cyan bold]\n")
            output_path = Prompt.ask(
                "[yellow]Enter export path (leave empty for default)[/yellow]",
                default="",
            )

            show_spinner(1, "Exporting")

            if output_path.strip():
                result = credential_manager.export_to_csv(output_path)
            else:
                result = credential_manager.export_to_csv()

            if result:
                print_status(f"Credentials exported to: {result}", "success")

        elif choice == "6":
            print_header()
            console.print("[cyan bold]=== IMPORT CREDENTIALS ===[/cyan bold]\n")
            csv_path = Prompt.ask("[yellow]Enter CSV file path[/yellow]")

            if os.path.exists(csv_path):
                show_spinner(1, "Importing")
                credential_manager.import_from_csv(csv_path)
                credentials = credential_manager.get_credentials()
                state.update_active_credential(None, credentials)
                print_status("Import process completed", "success")
            else:
                print_status(f"File not found: {csv_path}", "error")

        elif choice == "7":
            print_header()
            console.print("[cyan bold]=== STORED CREDENTIALS ===[/cyan bold]\n")

            if len(credentials) == 0:
                print_status("No credentials found.", "warning")
                continue

            table = create_credentials_table(credentials)
            console.print(table)
            console.print()
            print_status(f"Total credentials: {len(credentials)}", "info")
            Prompt.ask(
                "\n[cyan]Press Enter to return to the main menu[/cyan]", default=""
            )

        elif choice == "8":
            print_header()
            console.print("[cyan bold]=== RUNNING SPEED TEST ===[/cyan bold]\n")

            download, upload, ping, server_info = module.speed_test()

            if download is not None and upload is not None and ping is not None:
                module.speedtest_results(download, upload, ping, server_info)
            else:
                print_status("Speed test failed", "error")

            Prompt.ask(
                "\n[cyan]Press Enter to return to the main menu[/cyan]", default=""
            )

        elif choice == "9":
            print_header()
            console.print("[cyan bold]=== LOGGING OUT ===[/cyan bold]\n")

            creds = credential_manager.get_credentials()
            fail = False

            try:
                for cred in creds:
                    console.print(f"Logging out credential: {cred['username']}")
                    result = module.logout(cred)
                    if result == "Fail":
                        console.print(
                            "[red]Warning: Timeout occurred while logging out.[/red]"
                        )
                        fail = True
                    elif result is False:
                        console.print(
                            "[yellow]Warning: Failed to logout user.[/yellow]"
                        )
                        fail = True
                    else:
                        console.print(
                            f"[green]Successfully logged out: {cred['username']}[/green]"
                        )

                if not fail:
                    module.send_notification(
                        "Sophos Auto Login", "You have been logged out"
                    )
                else:
                    module.send_notification("Sophos Auto Login", "Logout failed.")

            except Exception as e:
                console.print(f"[red]Error during logout: {e}[/red]")
                fail = True
            Prompt.ask(
                "\n[cyan]Press Enter to return to the main menu[/cyan]", default=""
            )

        elif choice == "10":
            print_header()
            console.print("[cyan bold]=== DAEMON STATUS ===[/cyan bold]\n")

            status = module.get_daemon_status()
            from module.status import print_daemon_status

            print_daemon_status(status)

            console.print()
            console.rule(style="dim")
            Prompt.ask(
                "\n[cyan]Press Enter to return to the main menu[/cyan]", default=""
            )

        elif choice == "11":
            print_status("Exiting...", "warning")

            creds = credential_manager.get_credentials()
            fail = False

            try:
                idx, credential = state.get_active_credential()
                if idx is not None and credential is not None:
                    console.print(f"Logging out credential: {credential['username']}")
                    result = module.logout(credential)
                    if result == "Fail":
                        console.print(
                            "[red]Warning: Timeout occurred while logging out.[/red]"
                        )
                        fail = True
                    elif result is False:
                        console.print(
                            "[yellow]Warning: Failed to logout user.[/yellow]"
                        )
                        fail = True
                    else:
                        console.print(
                            f"[green]Successfully logged out: {credential['username']}[/green]"
                        )
                else:
                    console.print("No active credential to logout.")

                if not fail:
                    module.send_notification(
                        "Sophos Auto Login", "You have been logged out & Exited"
                    )
                else:
                    module.send_notification(
                        "Sophos Auto Login", "Logout failed. Exited."
                    )

            except Exception as e:
                console.print(f"[red]Error during logout: {e}[/red]")
                module.send_notification(
                    "Sophos Auto Login", f"Error during logout: {e}"
                )
                fail = True

            finally:
                if fail:
                    console.print("[yellow]Logout failed, but exiting anyway.[/yellow]")
                else:
                    console.print("[green]Logout successful.[/green]")

            running = False

        else:
            print_status("Invalid choice. Please try again.", "error")

    atexit.register(module.exit_handler)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        module.send_notification("Sophos Auto Login", f"An error occurred: {e}")
        console.print(f"[red]An error occurred: {e}[/red]")
