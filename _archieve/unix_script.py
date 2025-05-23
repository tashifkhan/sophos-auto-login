#!/Users/taf/Scripts/.sal/bin/python

import os
import sys
import time
import signal
import sal_module.module as module
import atexit
import logging
import datetime
import argparse
import sal_module.db.CredentialManager as CredManager
from colorama import init, Fore, Back, Style
from sal_module.module import state


init(autoreset=True)

# Flag to prevent multiple signal handlers from running
signal_handler_running = False

def parse_arguments():
    parser = argparse.ArgumentParser(description='Sophos Auto Login Tool')
    parser.add_argument('--start', '-s', action='store_true', help='Start auto-login process immediately')
    parser.add_argument('--add', '-a', action='store_true', help='Add new credentials')
    parser.add_argument('--edit', '-e', action='store_true', help='Edit existing credentials')
    parser.add_argument('--delete', '-del', action='store_true', help='Delete credentials')
    parser.add_argument('--export', '-x', type=str, nargs='?', const='', help='Export credentials to CSV (optional path)')
    parser.add_argument('--import', '-i', dest='import_csv', type=str, help='Import credentials from CSV file')
    parser.add_argument('--show', '-l', action='store_true', help='Display all stored credentials')
    parser.add_argument('--daemon', '-d', action='store_true', help='Run auto-login process in background (daemon mode)')
    parser.add_argument('--exit', '-q', action='store_true', help='Exit the daemon process and logout all credentials')
    parser.add_argument('--logout', '-lo', action='store_true', help='Logout from all credentials')
    parser.add_argument('--speedtest', '-t', action='store_true', help='Run speed test')   
    parser.add_argument('--status', '-st', action='store_true', help='Display daemon status')
    
    return parser.parse_args()

def daemonize():
    """Convert the current process to a daemon process."""
    # Check if we're on a Unix-like system
    if os.name != 'posix':
        print(f"{Fore.RED}Daemon mode is only supported on Unix-like systems.{Style.RESET_ALL}")
        sys.exit(1)
        
    # First fork
    try:
        pid = os.fork()
        if pid > 0:
            # Exit first parent
            sys.exit(0)
    except OSError as e:
        print(f"{Fore.RED}Fork #1 failed: {e}{Style.RESET_ALL}")
        sys.exit(1)
    
    # Decouple from parent environment
    os.chdir('/')
    os.setsid()
    os.umask(0)
    
    # Second fork
    try:
        pid = os.fork()
        if pid > 0:
            # Exit from second parent
            sys.exit(0)
    except OSError as e:
        print(f"{Fore.RED}Fork #2 failed: {e}{Style.RESET_ALL}")
        sys.exit(1)
    
    # Redirect standard file descriptors
    sys.stdout.flush()
    sys.stderr.flush()
    
    # Set up logging for daemon mode with improved format
    log_dir = os.path.expanduser("~/.sophos-autologin")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, "sophos-autologin.log")
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s │ %(levelname)-8s │ %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.info("╔══════════════════════════════════════════════════════════╗")
    logging.info("║                 SOPHOS AUTO LOGIN DAEMON                 ║")
    logging.info("╚══════════════════════════════════════════════════════════╝")
    logging.info("Daemon started")
    
    # Redirect standard file descriptors to /dev/null
    si = open(os.devnull, 'r')
    so = open(os.devnull, 'a+')
    se = open(os.devnull, 'a+')
    
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())
    
    # Write PID file
    pid_file = os.path.join(log_dir, "sophos-autologin.pid")
    with open(pid_file, 'w') as f:
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
            display_status("No credentials found. Please add credentials first.", "error")
            return None
    
    if not daemon_mode:
        print(f"{Fore.YELLOW}Starting auto-login process. Press Ctrl+C to stop.{Style.RESET_ALL}")    
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
        active_username = credentials[cred_index]['username']
        if not daemon_mode:
            display_status(f"Logged in with credential ID #{cred_index+1} ({active_username})", "success")
        else:
            logging.info(f"Logged in with credential ID #{cred_index+1} ({active_username})")
        
        # Update global state - redundant but safer
        state.update_active_credential(cred_index, credentials)
        
        # Update the signal handler with the current credential index
        signal.signal(signal.SIGINT, lambda sig, frame: module.exit_handler(cred_index, credentials, sig, frame))
        signal.signal(signal.SIGTERM, lambda sig, frame: module.exit_handler(cred_index, credentials, sig, frame))
        
        # Debug print to verify correct credential index
        print(f"Debug: Active credential index is {cred_index}, username: {credentials[cred_index]['username']}")
    
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
                
                # Log running time with every connection check
                if not daemon_mode:
                    status = f"{Fore.GREEN}✓ Connected{Style.RESET_ALL}" if has_internet else f"{Fore.RED}✗ Disconnected{Style.RESET_ALL}"
                    
                    print(f"\n{Fore.CYAN}CONNECTION CHECK{Style.RESET_ALL}")
                    print(f"Status: {status}")
                    print(f"Runtime: {duration}")
                    
                    if cred_index is not None and 0 <= cred_index < len(credentials):
                        active_username = credentials[cred_index]['username']
                        print(f"Active: ID #{cred_index+1} ({active_username})")
                else:
                    status = "✓ Connected" if has_internet else "✗ Disconnected"
                    logging.info(f"CONNECTION CHECK | Status: {status} | Runtime: {duration}")
                    if cred_index is not None and 0 <= cred_index < len(credentials):
                        active_username = credentials[cred_index]['username']
                        logging.info(f"Active credential: ID #{cred_index+1} ({active_username})")
                
                force_relogin = current_time - last_login_time >= FORCED_RELOGIN_INTERVAL
                
                if has_internet and not force_relogin:
                    if not daemon_mode:
                        print(f"{Fore.GREEN}➤ Internet is connected. No login needed.{Style.RESET_ALL}")
                    else:
                        logging.info("➤ Internet is connected. No login needed.")
                    time.sleep(10)
                    continue
                elif force_relogin:
                    message = "⟳ Performing scheduled re-login"
                    if not daemon_mode:
                        print(f"{Fore.YELLOW}\n{message}{Style.RESET_ALL}")
                    else:
                        logging.info(message)
                
                if (not has_internet) or force_relogin:
                    if not daemon_mode:
                        print(f"\n{Fore.CYAN}Login attempt #{count} | Running for: {duration}{Style.RESET_ALL}")
                    else:
                        logging.info(f"LOGIN ATTEMPT #{count} | Running for: {duration}")
                    
                    stop, cred_index = module.login(credentials)
                    last_login_time = time.time()
                    
                    # Log which credential was used for login
                    if cred_index is not None and 0 <= cred_index < len(credentials):
                        active_username = credentials[cred_index]['username']
                        if not daemon_mode:
                            display_status(f"Logged in with ID #{cred_index+1} ({active_username})", "success")
                        else:
                            logging.info(f"✓ Logged in with credential ID #{cred_index+1} ({active_username})")
                    
                    if stop:
                        if len(credentials) == 0:
                            if daemon_mode:
                                module.send_notification("Sophos Auto Login", "No credentials found. Daemon exiting.")
                                logging.error("No credentials found. Daemon exiting.")
                            else:
                                display_status("No credentials found.", "error")
                        else:
                            module.logout(credentials[cred_index])
                            if daemon_mode:
                                module.send_notification("Sophos Auto Login", f"Logged out {credentials[cred_index]['username']} & Exiting")
                                logging.info("Auto-login stopped.")
                            else:
                                display_status("Auto-login stopped.", "warning")
                        break
            
            time.sleep(10)
            
    except KeyboardInterrupt:
        if not daemon_mode:
            display_status("Auto-login interrupted by user.", "warning")
        else:
            module.send_notification("Sophos Auto Login", "Daemon interrupted by user.")
            logging.info("Auto-login daemon interrupted by user.")
    
    return cred_index

# Define a proper signal handler that uses the global state
def signal_handler(sig, frame):
    if state.signal_handler_running:
        print("Signal handler already running, ignoring additional signals...")
        return
    
    state.signal_handler_running = True
    
    try:
        idx, credential = state.get_active_credential()
        if idx is not None and credential is not None:
            print(f"\nExiting...\nLogging out credential: {credential['username']}")
            result = module.logout(credential)
            if result:
                print(f"{Fore.GREEN}Successfully logged out: {credential['username']}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}Failed to logout: {credential['username']}{Style.RESET_ALL}")
        else:
            print("\nExiting...\nNo active credential to logout.")
            print("Logout successful.")
    
    except Exception as e:
        print(f"Error during logout: {e}")
    
    finally:
        state.signal_handler_running = False
        sys.exit(0)

def print_header():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.CYAN}={Fore.WHITE}{Style.BRIGHT} SOPHOS AUTO LOGIN {Fore.CYAN + Style.NORMAL}{'=' * 40}")
    print(f"{Fore.CYAN}{'=' * 60}\n")

def print_menu():
    print(f"\n{Fore.YELLOW}Choose an option:{Style.RESET_ALL}")
    print(f"{Fore.GREEN}[1]{Style.RESET_ALL} Add new login credentials")
    print(f"{Fore.GREEN}[2]{Style.RESET_ALL} Start auto-login process")
    print(f"{Fore.GREEN}[3]{Style.RESET_ALL} Edit existing credentials")
    print(f"{Fore.GREEN}[4]{Style.RESET_ALL} Delete credentials")
    print(f"{Fore.GREEN}[5]{Style.RESET_ALL} Export credentials to CSV")
    print(f"{Fore.GREEN}[6]{Style.RESET_ALL} Import credentials from CSV")
    print(f"{Fore.GREEN}[7]{Style.RESET_ALL} Show stored credentials")
    print(f"{Fore.GREEN}[8]{Style.RESET_ALL} Run SpeedTest")
    print(f"{Fore.GREEN}[9]{Style.RESET_ALL} Logout from all credentials")
    print(f"{Fore.GREEN}[10]{Style.RESET_ALL} Check daemon status")
    print(f"{Fore.GREEN}[11]{Style.RESET_ALL} Exit")
    
    return input(f"\n{Fore.YELLOW}Enter your choice (1-11): {Style.RESET_ALL}")

def display_status(message, status_type="info"):
    box_width = 50
    
    if status_type == "success":
        border_top = f"{Fore.GREEN}╔{'═' * box_width}╗{Style.RESET_ALL}"
        border_bottom = f"{Fore.GREEN}╚{'═' * box_width}╝{Style.RESET_ALL}"
        text = f"✓ {message}"
        padding = (box_width - len(text)) // 2
        centered_text = f"{Fore.GREEN}║{' ' * padding}{text}{' ' * (box_width - len(text) - padding)}║{Style.RESET_ALL}"
    elif status_type == "error":
        border_top = f"{Fore.RED}╔{'═' * box_width}╗{Style.RESET_ALL}"
        border_bottom = f"{Fore.RED}╚{'═' * box_width}╝{Style.RESET_ALL}"
        text = f"✗ {message}"
        padding = (box_width - len(text)) // 2
        centered_text = f"{Fore.RED}║{' ' * padding}{text}{' ' * (box_width - len(text) - padding)}║{Style.RESET_ALL}"
    elif status_type == "warning":
        border_top = f"{Fore.YELLOW}╔{'═' * box_width}╗{Style.RESET_ALL}"
        border_bottom = f"{Fore.YELLOW}╚{'═' * box_width}╝{Style.RESET_ALL}"
        text = f"⚠ {message}"
        padding = (box_width - len(text)) // 2
        centered_text = f"{Fore.YELLOW}║{' ' * padding}{text}{' ' * (box_width - len(text) - padding)}║{Style.RESET_ALL}"
    else:
        border_top = f"{Fore.BLUE}╔{'═' * box_width}╗{Style.RESET_ALL}"
        border_bottom = f"{Fore.BLUE}╚{'═' * box_width}╝{Style.RESET_ALL}"
        text = f"ℹ {message}"
        padding = (box_width - len(text)) // 2
        centered_text = f"{Fore.BLUE}║{' ' * padding}{text}{' ' * (box_width - len(text) - padding)}║{Style.RESET_ALL}"
        
    print("\n" + border_top)
    print(centered_text)
    print(border_bottom)
    
    time.sleep(1)

def show_spinner(seconds, message="Processing"):
    spinner = ['-', '\\', '|', '/']
    end_time = time.time() + seconds
    i = 0
    
    print()
    while time.time() < end_time:
        print(f"\r{Fore.CYAN}{message} {spinner[i % len(spinner)]}{Style.RESET_ALL}", end="")
        i += 1
        time.sleep(0.1)
    print("\r" + " " * (len(message) + 2) + "\r", end="")

def format_time(minutes):
    hrs = minutes // 60
    mins = minutes % 60
    if hrs == 0:
        return f"{mins} minutes"
    else:
        return f"{hrs} hours {mins} minutes"

def main():
    args = parse_arguments()
    
    credential_manager = CredManager.CredentialManger()
    credentials = credential_manager.get_credentials()
    state.update_active_credential(None, credentials)  
    running = True

    # Register the custom signal handler for SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Add status check command line argument
    if args.status:
        print_header()
        print(f"{Fore.CYAN}=== DAEMON STATUS ==={Style.RESET_ALL}\n")
        
        status = module.get_daemon_status()
        
        print(status["status_str"])
        
        if status["error"]:
            print(f"\n{Style.BRIGHT}{Fore.RED}⚠️  WARNING:{Style.RESET_ALL}")
            print(f"  {Fore.RED}{status['error']}{Style.RESET_ALL}")
        
        print(f"\n{Style.BRIGHT}DETAILS:{Style.RESET_ALL}")
        
        if status["last_activity"]:
            print(f"  {Fore.CYAN}Last Activity:{Style.RESET_ALL}      {Style.BRIGHT}{status['last_activity']}{Style.RESET_ALL} "
                f"({status['time_since_activity']} ago)")
        
        if status["last_action"]:
            print(f"  {Fore.CYAN}Last Action:{Style.RESET_ALL}        {status['last_action']}")
        
        if status["connection_status"]:
            conn_color = Fore.GREEN if status["connection_status"] == "Connected" else Fore.RED
            print(f"  {Fore.CYAN}Network Status:{Style.RESET_ALL}     "
                f"{conn_color}{Style.BRIGHT}{status['connection_status']}{Style.RESET_ALL}")
        
        if status["active_credential"]:
            print(f"  {Fore.CYAN}Active Credential:{Style.RESET_ALL}  {Style.BRIGHT}{status['active_credential']}{Style.RESET_ALL}")
        
        if status["runtime"]:
            print(f"  {Fore.CYAN}Daemon Runtime:{Style.RESET_ALL}     {status['runtime']}")
        
        print(f"\n{Style.BRIGHT}{'=' * 60}{Style.RESET_ALL}")
        return

    if args.exit:
        print_header()
        print(f"{Fore.CYAN}=== STOPPING DAEMON PROCESS ==={Style.RESET_ALL}\n")

        display_status("Exiting...", "warning")
        creds = credential_manager.get_credentials()
        fail = False
        
        try:
            idx, credential = state.get_active_credential()
            if idx is not None and credential is not None:
                print(f"Logging out credential: {credential['username']}")
                result = module.logout(credential)
                if result == "Fail":
                    print(f"{Fore.RED}Warning: Timeout occurred while logging out.{Style.RESET_ALL}")
                    fail = True
                elif result is False:
                    print(f"{Fore.YELLOW}Warning: Failed to logout user.{Style.RESET_ALL}")
                    fail = True
                else:
                    print(f"{Fore.GREEN}Successfully logged out: {cred['username']}{Style.RESET_ALL}")
            else:
                print("No active credential to logout.")
            
            if not fail:
                module.send_notification("Sophos Auto Login", "You have been logged out & Exited")
            else:
                module.send_notification("Sophos Auto Login", "Logout failed. Exited.")
        
        except Exception as e:
            print(f"{Fore.RED}Error during logout: {e}{Style.RESET_ALL}")
            module.send_notification("Sophos Auto Login", f"Error during logout: {e}")
            fail = True
        
        finally:
            if fail:
                print(f"{Fore.YELLOW}Logout failed, but exiting anyway.{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}Logout successful.{Style.RESET_ALL}")
        
        running = False

        if not sys.platform.startswith('win'):
            module.deamon_exit()

    # Handle daemon mode
    if args.daemon:
        if args.start:
            try:
                log_file, pid_file = daemonize()
                print(f"{Fore.GREEN}Daemon started. Log file: {log_file}, PID file: {pid_file}{Style.RESET_ALL}")
                
                def daemon_exit_handler():
                    try:
                        if os.path.exists(pid_file):
                            with open(pid_file, 'r') as f:
                                if int(f.read().strip()) == os.getpid():
                                    module.send_notification("Sophos Auto Login", "Daemon has exited")
                                    logging.info("Daemon process has exited")
                    except Exception as e:
                        logging.error(f"Error in daemon exit handler: {e}")
                
                atexit.register(daemon_exit_handler)
                
                try:
                    cred_index = run_auto_login(credential_manager, daemon_mode=True)
                    state.update_active_credential(cred_index, credential_manager.get_credentials())  
                except Exception as e:
                    module.send_notification("Sophos Auto Login", f"Daemon error: {str(e)}")
                    logging.error(f"Daemon error during auto-login: {e}")
                    raise
                    
            except KeyboardInterrupt:
                module.send_notification("Sophos Auto Login", "Daemon was stopped by keyboard interrupt")
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
            print(f"{Fore.RED}--daemon must be used with --start{Style.RESET_ALL}")
            sys.exit(1)
        return
    
    if args.show:
        print_header()
        print(f"{Fore.CYAN}=== STORED CREDENTIALS ==={Style.RESET_ALL}\n")
        
        if len(credentials) == 0:
            display_status("No credentials found.", "warning")
            return
            
        print(f"{Fore.YELLOW}{'ID':^5} | {'Username':^20} | {'Password':^15} |{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'-'*5:^5} | {'-'*20:^20} | {'-'*15:^15} |{Style.RESET_ALL}")
        
        for i, cred in enumerate(credentials):
            print(f"{Fore.GREEN}{i+1:^5} | {cred['username']:^20} | {cred['password']:^15} |{Style.RESET_ALL}")
            
        print()
        display_status(f"Total credentials: {len(credentials)}", "info")
        return
    
    elif args.add:
        print_header()
        print(f"{Fore.CYAN}=== ADD NEW CREDENTIALS ==={Style.RESET_ALL}\n")
        credential_manager.add_credential()
        credentials = credential_manager.get_credentials()
        state.update_active_credential(None, credentials)  
        show_spinner(1, "Updating credentials")
        display_status("Credentials added successfully", "success")
        return
    
    elif args.edit:
        print_header()
        print(f"{Fore.CYAN}=== EDIT CREDENTIALS ==={Style.RESET_ALL}\n")
        result = credential_manager.edit_credentials()
        credentials = credential_manager.get_credentials()
        state.update_active_credential(None, credentials)  
        if result:
            show_spinner(1, "Updating credentials")
            display_status("Credentials updated successfully", "success")
        return
    
    elif args.delete:
        print_header()
        print(f"{Fore.CYAN}=== DELETE CREDENTIALS ==={Style.RESET_ALL}\n")
        credential_manager.delete_credential()
        credentials = credential_manager.get_credentials()
        state.update_active_credential(None, credentials)  
        show_spinner(1, "Updating credentials")
        display_status("Credentials deleted", "success")
        return
    
    elif args.export is not None:
        print_header()
        print(f"{Fore.CYAN}=== EXPORT CREDENTIALS ==={Style.RESET_ALL}\n")
        
        show_spinner(1, "Exporting")
        
        if args.export:
            result = credential_manager.export_to_csv(args.export)
        else:
            result = credential_manager.export_to_csv()
            
        if result:
            display_status(f"Credentials exported to: {result}", "success")
        return
    
    elif args.import_csv:
        print_header()
        print(f"{Fore.CYAN}=== IMPORT CREDENTIALS ==={Style.RESET_ALL}\n")
        
        if os.path.exists(args.import_csv):
            show_spinner(1, "Importing")
            credential_manager.import_from_csv(args.import_csv)
            credentials = credential_manager.get_credentials()
            state.update_active_credential(None, credentials)  
            display_status("Import process completed", "success")
        else:
            display_status(f"File not found: {args.import_csv}", "error")
        return
    
    elif args.speedtest:
        print_header()
        print(f"{Fore.CYAN}=== RUNNING SPEED TEST ==={Style.RESET_ALL}\n")
        
        show_spinner(1, "Running speed test")
        download, upload, ping, server_info = module.speed_test()

        if download is not None and upload is not None and ping is not None:
            module.speedtest_results(download, upload, ping, server_info)
        else:
            display_status("Speed test failed", "error")
        return
    
    elif args.logout:
        print_header()
        print(f"{Fore.CYAN}=== LOGGING OUT ==={Style.RESET_ALL}\n")

        creds = credential_manager.get_credentials()
        fail = False

        try:
            for cred in creds:
                print(f"Logging out credential: {cred['username']}")
                result = module.logout(cred)
                if result == "Fail":
                    print(f"{Fore.RED}Warning: Timeout occurred while logging out.{Style.RESET_ALL}")
                    fail = True
                elif result is False:
                    print(f"{Fore.YELLOW}Warning: Failed to logout user.{Style.RESET_ALL}")
                    fail = True
                else:
                    print(f"{Fore.GREEN}Successfully logged out: {cred['username']}{Style.RESET_ALL}")

            if not fail:
                module.send_notification("Sophos Auto Login", "You have been logged out")
                display_status("All users logged out successfully", "success")
            else:
                module.send_notification("Sophos Auto Login", "Logout failed.")
                display_status("Some users failed to log out", "warning")
        
        except Exception as e:
            print(f"{Fore.RED}Error during logout: {e}{Style.RESET_ALL}")
            fail = True
            
        # Terminate the program after logging out
        print(f"{Fore.YELLOW}Exiting program...{Style.RESET_ALL}")
        sys.exit(0)
    
    elif args.start:
        print_header()
        print(f"{Fore.CYAN}=== AUTO-LOGIN PROCESS ==={Style.RESET_ALL}\n")
        cred_index = run_auto_login(credential_manager)
        # State is updated by run_auto_login
        return
    
    # If no command line arguments provided, run the interactive menu loop
    while running:
        print_header()
        
        cred_count = len(credentials)
        if cred_count > 0:
            print(f"{Fore.BLUE}You have {cred_count} stored credential(s){Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}No credentials stored yet. Please add credentials.{Style.RESET_ALL}")
        
        choice = print_menu()
        
        if choice == "1":
            print_header()
            print(f"{Fore.CYAN}=== ADD NEW CREDENTIALS ==={Style.RESET_ALL}\n")
            credential_manager.add_credential()
            credentials = credential_manager.get_credentials()
            state.update_active_credential(None, credentials) 
            show_spinner(1, "Updating credentials")
        
        elif choice == "2":
            print_header()
            print(f"{Fore.CYAN}=== AUTO-LOGIN PROCESS ==={Style.RESET_ALL}\n")
            run_auto_login(credential_manager)
            # State is updated by run_auto_login
        
        elif choice == "3":
            print_header()
            print(f"{Fore.CYAN}=== EDIT CREDENTIALS ==={Style.RESET_ALL}\n")
            result = credential_manager.edit_credentials()
            credentials = credential_manager.get_credentials()
            state.update_active_credential(None, credentials) 
            if result:
                show_spinner(1, "Updating credentials")
        
        elif choice == "4":
            print_header()
            print(f"{Fore.CYAN}=== DELETE CREDENTIALS ==={Style.RESET_ALL}\n")
            credential_manager.delete_credential()
            credentials = credential_manager.get_credentials()
            state.update_active_credential(None, credentials) 
            show_spinner(1, "Updating credentials")
        
        elif choice == "5":
            print_header()
            print(f"{Fore.CYAN}=== EXPORT CREDENTIALS ==={Style.RESET_ALL}\n")
            output_path = input(f"{Fore.YELLOW}Enter export path (leave empty for default): {Style.RESET_ALL}")
            
            show_spinner(1, "Exporting")
            
            if output_path.strip():
                result = credential_manager.export_to_csv(output_path)
            else:
                result = credential_manager.export_to_csv()
                
            if result:
                display_status(f"Credentials exported to: {result}", "success")
        
        elif choice == "6":
            print_header()
            print(f"{Fore.CYAN}=== IMPORT CREDENTIALS ==={Style.RESET_ALL}\n")
            csv_path = input(f"{Fore.YELLOW}Enter CSV file path: {Style.RESET_ALL}")
            
            if os.path.exists(csv_path):
                show_spinner(1, "Importing")
                credential_manager.import_from_csv(csv_path)
                credentials = credential_manager.get_credentials()
                state.update_active_credential(None, credentials) 
                display_status("Import process completed", "success")
            else:
                display_status(f"File not found: {csv_path}", "error")
        
        elif choice == "7":
            print_header()
            print(f"{Fore.CYAN}=== STORED CREDENTIALS ==={Style.RESET_ALL}\n")
            
            if len(credentials) == 0:
                display_status("No credentials found.", "warning")
                continue
                
            print(f"{Fore.YELLOW}{'ID':^5} | {'Username':^20} | {'Password':^15} |{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{'-'*5:^5} | {'-'*20:^20} | {'-'*15:^15} |{Style.RESET_ALL}")
            
            for i, cred in enumerate(credentials):
                print(f"{Fore.GREEN}{i+1:^5} | {cred['username']:^20} | {cred['password']:^15} |{Style.RESET_ALL}")
                
            print()
            display_status(f"Total credentials: {len(credentials)}", "info")
            input(f"\n{Fore.CYAN}Press Enter to return to the main menu...{Style.RESET_ALL}")
        
        elif choice == "8":
            print_header()
            print(f"{Fore.CYAN}=== RUNNING SPEED TEST ==={Style.RESET_ALL}\n")
            
            show_spinner(1, "Running speed test")
            download, upload, ping, server_info = module.speed_test()

            if download is not None and upload is not None and ping is not None:
                module.speedtest_results(download, upload, ping, server_info)
            else:
                display_status("Speed test failed", "error")
            
            input(f"\n{Fore.CYAN}Press Enter to return to the main menu...{Style.RESET_ALL}")

        elif choice == "9":
            print_header()
            print(f"{Fore.CYAN}=== LOGGING OUT ==={Style.RESET_ALL}\n")

            creds = credential_manager.get_credentials()
            fail = False

            try:
                for cred in creds:
                    print(f"Logging out credential: {cred['username']}")
                    result = module.logout(cred)
                    if result == "Fail":
                        print(f"{Fore.RED}Warning: Timeout occurred while logging out.{Style.RESET_ALL}")
                        fail = True
                    elif result is False:
                        print(f"{Fore.YELLOW}Warning: Failed to logout user.{Style.RESET_ALL}")
                        fail = True
                    else:
                        print(f"{Fore.GREEN}Successfully logged out: {cred['username']}{Style.RESET_ALL}")

                if not fail:
                    module.send_notification("Sophos Auto Login", "You have been logged out")
                else:
                    module.send_notification("Sophos Auto Login", "Logout failed.")
            
            except Exception as e:
                print(f"{Fore.RED}Error during logout: {e}{Style.RESET_ALL}")
                fail = True
            input(f"\n{Fore.CYAN}Press Enter to return to the main menu...{Style.RESET_ALL}")

        elif choice == "10":
            print_header()
            print(f"{Fore.CYAN}=== DAEMON STATUS ==={Style.RESET_ALL}\n")
            
            status = module.get_daemon_status()
            
            print(status["status_str"])
            
            if status["error"]:
                print(f"\n{Style.BRIGHT}{Fore.RED}⚠️  WARNING:{Style.RESET_ALL}")
                print(f"  {Fore.RED}{status['error']}{Style.RESET_ALL}")
            
            print(f"\n{Style.BRIGHT}DETAILS:{Style.RESET_ALL}")
            
            if status["last_activity"]:
                print(f"  {Fore.CYAN}Last Activity:{Style.RESET_ALL}      {Style.BRIGHT}{status['last_activity']}{Style.RESET_ALL} "
                    f"({status['time_since_activity']} ago)")
            
            if status["last_action"]:
                print(f"  {Fore.CYAN}Last Action:{Style.RESET_ALL}        {status['last_action']}")
            
            if status["connection_status"]:
                conn_color = Fore.GREEN if status["connection_status"] == "Connected" else Fore.RED
                print(f"  {Fore.CYAN}Network Status:{Style.RESET_ALL}     "
                    f"{conn_color}{Style.BRIGHT}{status['connection_status']}{Style.RESET_ALL}")
            
            if status["active_credential"]:
                print(f"  {Fore.CYAN}Active Credential:{Style.RESET_ALL}  {Style.BRIGHT}{status['active_credential']}{Style.RESET_ALL}")
            
            if status["runtime"]:
                print(f"  {Fore.CYAN}Daemon Runtime:{Style.RESET_ALL}     {status['runtime']}")
            
            print(f"\n{Style.BRIGHT}{'=' * 60}{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Press Enter to return to the main menu...{Style.RESET_ALL}")
        
        elif choice == "11":
            display_status("Exiting...", "warning")
            
            creds = credential_manager.get_credentials()
            fail = False
            
            try:
                idx, credential = state.get_active_credential()
                if idx is not None and credential is not None:
                    print(f"Logging out credential: {credential['username']}")
                    result = module.logout(credential)
                    if result == "Fail":
                        print(f"{Fore.RED}Warning: Timeout occurred while logging out.{Style.RESET_ALL}")
                        fail = True
                    elif result is False:
                        print(f"{Fore.YELLOW}Warning: Failed to logout user.{Style.RESET_ALL}")
                        fail = True
                    else:
                        print(f"{Fore.GREEN}Successfully logged out: {credential['username']}{Style.RESET_ALL}")
                else:
                    print("No active credential to logout.")
                
                if not fail:
                    module.send_notification("Sophos Auto Login", "You have been logged out & Exited")
                else:
                    module.send_notification("Sophos Auto Login", "Logout failed. Exited.")
            
            except Exception as e:
                print(f"{Fore.RED}Error during logout: {e}{Style.RESET_ALL}")
                module.send_notification("Sophos Auto Login", f"Error during logout: {e}")
                fail = True
            
            finally:
                if fail:
                    print(f"{Fore.YELLOW}Logout failed, but exiting anyway.{Style.RESET_ALL}")
                else:
                    print(f"{Fore.GREEN}Logout successful.{Style.RESET_ALL}")
                
            running = False
        
        else:
            display_status("Invalid choice. Please try again.", "error")
    
    atexit.register(module.exit_handler) 

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        module.send_notification("Sophos Auto Login", f"An error occurred: {e}")
        print(f"{Fore.RED}An error occurred: {e}{Style.RESET_ALL}")
