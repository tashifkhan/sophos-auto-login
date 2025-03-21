import db.CredentialManager as CredManager
import module
import atexit
import signal
import os
import time
from colorama import init, Fore, Back, Style

# Initialize colorama
init(autoreset=True)

def print_header():
    """Print a stylized header for the application."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.CYAN}={Fore.WHITE}{Style.BRIGHT} SOPHOS AUTO LOGIN {Fore.CYAN + Style.NORMAL}{'=' * 40}")
    print(f"{Fore.CYAN}{'=' * 60}\n")

def print_menu():
    """Display the main menu options."""
    print(f"\n{Fore.YELLOW}Choose an option:{Style.RESET_ALL}")
    print(f"{Fore.GREEN}[1]{Style.RESET_ALL} Add new login credentials")
    print(f"{Fore.GREEN}[2]{Style.RESET_ALL} Start auto-login process")
    print(f"{Fore.GREEN}[3]{Style.RESET_ALL} Edit existing credentials")
    print(f"{Fore.GREEN}[4]{Style.RESET_ALL} Delete credentials")
    print(f"{Fore.GREEN}[5]{Style.RESET_ALL} Export credentials to CSV")
    print(f"{Fore.GREEN}[6]{Style.RESET_ALL} Import credentials from CSV")
    print(f"{Fore.GREEN}[7]{Style.RESET_ALL} Exit")
    
    return input(f"\n{Fore.YELLOW}Enter your choice (1-7): {Style.RESET_ALL}")

def display_status(message, status_type="info"):
    """Display a formatted status message."""
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
    """Display a simple spinner animation to indicate progress."""
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
    """Format minutes into hours and minutes."""
    hrs = minutes // 60
    mins = minutes % 60
    if hrs == 0:
        return f"{mins} minutes"
    else:
        return f"{hrs} hours {mins} minutes"

def main():
    credential_manager = CredManager.CredentialManger()
    cred_index = 0
    credentials = credential_manager.get_credentials()
    running = True
    
    signal.signal(signal.SIGINT, lambda sig, frame: module.exit_handler(cred_index, credentials, sig, frame))
    
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
            
            if len(credentials) == 0:
                display_status("No credentials found. Please add credentials first.", "error")
                continue
                
            print(f"{Fore.YELLOW}Starting auto-login process. Press Ctrl+C to stop.{Style.RESET_ALL}\n")
            count = 0
            cred_index = 0
            
            try:
                while True:
                    count += 1
                    duration = (count-1) * 2
                    
                    print(f"\n{Fore.CYAN}Login attempt {count}{Style.RESET_ALL}")
                    if count > 1:
                        print(f"{Fore.BLUE}Running for {format_time(duration)}...{Style.RESET_ALL}\n")
                    
                    stop, cred_index = module.login(credential_manager.get_credentials())
                    if stop:
                        if len(credentials) == 0:
                            display_status("No credentials found.", "error")
                        else:
                            module.logout(credential_manager.get_credentials()[cred_index])
                            display_status("Auto-login stopped.", "warning")
                        break
            except KeyboardInterrupt:
                print()
                display_status("Auto-login interrupted by user.", "warning")
                if cred_index is not None and 0 <= cred_index < len(credentials):
                    module.logout(credentials[cred_index])
        
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
