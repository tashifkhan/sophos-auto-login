import db.CredentialManager as CredManager
import module
import atexit
import signal
import os
import time
import argparse
import sys
import logging
from colorama import init, Fore, Back, Style

init(autoreset=True)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Sophos Auto Login Tool')
    parser.add_argument('--start', action='store_true', help='Start auto-login process immediately')
    parser.add_argument('--add', action='store_true', help='Add new credentials')
    parser.add_argument('--edit', action='store_true', help='Edit existing credentials')
    parser.add_argument('--delete', action='store_true', help='Delete credentials')
    parser.add_argument('--export', type=str, nargs='?', const='', help='Export credentials to CSV (optional path)')
    parser.add_argument('--import', dest='import_csv', type=str, help='Import credentials from CSV file')
    parser.add_argument('--show', action='store_true', help='Display all stored credentials')
    parser.add_argument('--daemon', action='store_true', help='Run auto-login process in background (daemon mode)')
    
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
    
    # Set up logging for daemon mode
    log_dir = os.path.expanduser("~/.sophos-autologin")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, "sophos-autologin.log")
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
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
    cred_index = None
    
    if len(credentials) == 0:
        if daemon_mode:
            logging.error("No credentials found. Daemon exiting.")
            return
        else:
            display_status("No credentials found. Please add credentials first.", "error")
            return
    
    if not daemon_mode:
        print(f"{Fore.YELLOW}Starting auto-login process. Press Ctrl+C to stop.{Style.RESET_ALL}\n")
    else:
        logging.info("Starting auto-login process in daemon mode")
    
    count = 0
    
    try:
        while True:
            count += 1
            duration = (count-1) * 2  
            
            if not daemon_mode:
                print(f"\n{Fore.CYAN}Login attempt {count}{Style.RESET_ALL}")
                if count > 1:
                    print(f"{Fore.BLUE}Running for {format_time(duration)}...{Style.RESET_ALL}\n")
            else:
                logging.info(f"Login attempt {count}. Running for {format_time(duration)}")
            
            stop, cred_index = module.login(credentials)
            if stop:
                if len(credentials) == 0:
                    if daemon_mode:
                        logging.error("No credentials found. Daemon exiting.")
                    else:
                        display_status("No credentials found.", "error")
                else:
                    module.logout(credentials[cred_index])
                    if daemon_mode:
                        logging.info("Auto-login stopped.")
                    else:
                        display_status("Auto-login stopped.", "warning")
                break
    except KeyboardInterrupt:
        if not daemon_mode:
            print()
            display_status("Auto-login interrupted by user.", "warning")
        else:
            logging.info("Auto-login daemon interrupted by user.")
        
        if cred_index is not None and 0 <= cred_index < len(credentials):
            module.logout(credentials[cred_index])

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
    print(f"{Fore.GREEN}[8]{Style.RESET_ALL} Exit")
    
    return input(f"\n{Fore.YELLOW}Enter your choice (1-8): {Style.RESET_ALL}")

def display_status(message, status_type="info"):
    if status_type == "success":
        print(f"\n{Fore.GREEN}✓ {message}{Style.RESET_ALL}")
    elif status_type == "error":
        print(f"\n{Fore.RED}✗ {message}{Style.RESET_ALL}")
    elif status_type == "warning":
        print(f"\n{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")
    
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
    cred_index = None
    credentials = credential_manager.get_credentials()
    running = True

    # Handle daemon mode
    if args.daemon:
        if args.start:
            try:
                log_file, pid_file = daemonize()
                print(f"{Fore.GREEN}Daemon started. Log file: {log_file}, PID file: {pid_file}{Style.RESET_ALL}")
                signal.signal(signal.SIGINT, lambda sig, frame: module.exit_handler(cred_index, credentials, sig, frame))
                signal.signal(signal.SIGTERM, lambda sig, frame: module.exit_handler(cred_index, credentials, sig, frame))
                run_auto_login(credential_manager, daemon_mode=True)
            except Exception as e:
                if isinstance(e, KeyboardInterrupt):
                    sys.exit(0)
                logging.error(f"Daemon error: {e}")
                sys.exit(1)
        else:
            print(f"{Fore.RED}--daemon must be used with --start{Style.RESET_ALL}")
            sys.exit(1)
        return
    
    signal.signal(signal.SIGINT, lambda sig, frame: module.exit_handler(cred_index, credentials, sig, frame))
    
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
        show_spinner(1, "Updating credentials")
        display_status("Credentials added successfully", "success")
        return
    
    elif args.edit:
        print_header()
        print(f"{Fore.CYAN}=== EDIT CREDENTIALS ==={Style.RESET_ALL}\n")
        result = credential_manager.edit_credentials()
        credentials = credential_manager.get_credentials()
        if result:
            show_spinner(1, "Updating credentials")
            display_status("Credentials updated successfully", "success")
        return
    
    elif args.delete:
        print_header()
        print(f"{Fore.CYAN}=== DELETE CREDENTIALS ==={Style.RESET_ALL}\n")
        credential_manager.delete_credential()
        credentials = credential_manager.get_credentials()
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
            display_status("Import process completed", "success")
        else:
            display_status(f"File not found: {args.import_csv}", "error")
        return
    
    elif args.start:
        print_header()
        print(f"{Fore.CYAN}=== AUTO-LOGIN PROCESS ==={Style.RESET_ALL}\n")
        run_auto_login(credential_manager)
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
            show_spinner(1, "Updating credentials")
        
        elif choice == "2":
            print_header()
            print(f"{Fore.CYAN}=== AUTO-LOGIN PROCESS ==={Style.RESET_ALL}\n")
            run_auto_login(credential_manager)
        
        elif choice == "3":
            print_header()
            print(f"{Fore.CYAN}=== EDIT CREDENTIALS ==={Style.RESET_ALL}\n")
            result = credential_manager.edit_credentials()
            credentials = credential_manager.get_credentials()
            if result:
                show_spinner(1, "Updating credentials")
        
        elif choice == "4":
            print_header()
            print(f"{Fore.CYAN}=== DELETE CREDENTIALS ==={Style.RESET_ALL}\n")
            credential_manager.delete_credential()
            credentials = credential_manager.get_credentials()
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
            display_status("Exiting...", "warning")
            creds = credential_manager.get_credentials()
            if cred_index is None or not (0 <= cred_index < len(creds)):
                print("Logging out all credentials...")
                for cred in creds:
                    module.logout(cred)
            else:
                print(f"Logging out credential: {creds[cred_index]['username']}")
                module.logout(creds[cred_index])
            running = False
        
        else:
            display_status("Invalid choice. Please try again.", "error")
    
    atexit.register(lambda: module.exit_handler(cred_index, credentials))

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"{Fore.RED}An error occurred: {e}{Style.RESET_ALL}")
