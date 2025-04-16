import os
import time
import speedtest
import threading
from colorama import init, Fore, Back, Style

init(autoreset=True)

def display_status(message, status_type="info"):
    """Displays a message in a formatted box based on status type."""
    box_width = 60
    
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
    else:  # info
        border_top = f"{Fore.BLUE}╔{'═' * box_width}╗{Style.RESET_ALL}"
        border_bottom = f"{Fore.BLUE}╚{'═' * box_width}╝{Style.RESET_ALL}"
        text = f"ℹ {message}"
        padding = (box_width - len(text)) // 2
        centered_text = f"{Fore.BLUE}║{' ' * padding}{text}{' ' * (box_width - len(text) - padding)}║{Style.RESET_ALL}"
        
    print("\n" + border_top)
    print(centered_text)
    print(border_bottom + "\n")
    

def display_results(download, upload, ping, server_info=None):
    """Displays the speed test results in a formatted box."""
    print(f"\n{Fore.CYAN}╔{'═' * 58}╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Fore.WHITE}{Style.BRIGHT} SPEED TEST RESULTS {' ' * 39}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╠{'═' * 58}╣{Style.RESET_ALL}")
    
    if server_info:
        print(f"{Fore.CYAN}║ {Fore.WHITE}Server: {server_info}{' ' * (50 - len(server_info))}{Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╠{'═' * 58}╣{Style.RESET_ALL}")
    
    download_str = f"{download:.2f} Mbps"
    upload_str = f"{upload:.2f} Mbps"
    ping_str = f"{ping:.2f} ms"
    
    print(f"{Fore.CYAN}║ {Fore.GREEN}Download: {download_str}{' ' * (48 - len(download_str))}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║ {Fore.YELLOW}Upload:   {upload_str}{' ' * (48 - len(upload_str))}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║ {Fore.MAGENTA}Ping:     {ping_str}{' ' * (48 - len(ping_str))}{Fore.CYAN}║{Style.RESET_ALL}")
    
    print(f"{Fore.CYAN}╚{'═' * 58}╝{Style.RESET_ALL}")

def run_spinner_thread(message, stop_event):
    """Run a spinner animation in a separate thread."""
    spinner = ['-', '\\', '|', '/']
    i = 0
    while not stop_event.is_set():
        print(f"\r{Fore.CYAN}{message} {spinner[i % len(spinner)]}{Style.RESET_ALL}", end="")
        i += 1
        time.sleep(0.1)

def clear_current_line():
    """Clear the current line in the terminal."""
    print('\r' + ' ' * 100 + '\r', end='')

def run_speed_test():
    """Runs the internet speed test and returns the results."""
    try:
        st = speedtest.Speedtest()
        server_info = None
        
        print(f"{Fore.YELLOW}Finding the best server...{Style.RESET_ALL}")
        
        server_stop_event = threading.Event()
        
        spinner_thread = threading.Thread(
            target=run_spinner_thread,
            args=("Selecting best server", server_stop_event)
        )
        spinner_thread.daemon = True
        spinner_thread.start()
        
        st.get_best_server()
        
        server_stop_event.set()
        spinner_thread.join(timeout=1)
        
        clear_current_line()
        server_info = f"{st.results.server['sponsor']} ({st.results.server['name']}, {st.results.server['country']})"
        print(f"{Fore.GREEN}Selected server: {server_info}{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}Starting download test...{Style.RESET_ALL}")
        
        download_stop_event = threading.Event()
        
        download_spinner = threading.Thread(
            target=run_spinner_thread,
            args=("Testing download speed", download_stop_event)
        )
        download_spinner.daemon = True
        download_spinner.start()
        
        download_speed_bps = st.download()
        
        download_stop_event.set()
        download_spinner.join(timeout=1)
        
        clear_current_line()
        download_speed_mbps = download_speed_bps / 1_000_000
        print(f"{Fore.GREEN}Download Speed: {download_speed_mbps:.2f} Mbps{Style.RESET_ALL}")
    
        print(f"\n{Fore.YELLOW}Starting upload test...{Style.RESET_ALL}")
    
        upload_stop_event = threading.Event()
        
        upload_spinner = threading.Thread(
            target=run_spinner_thread,
            args=("Testing upload speed", upload_stop_event)
        )
        upload_spinner.daemon = True
        upload_spinner.start()
        
        upload_speed_bps = st.upload()
        
        upload_stop_event.set()
        upload_spinner.join(timeout=1)
        
        clear_current_line()
        upload_speed_mbps = upload_speed_bps / 1_000_000
        print(f"{Fore.GREEN}Upload Speed: {upload_speed_mbps:.2f} Mbps{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}Measuring ping...{Style.RESET_ALL}")
        
        ping_stop_event = threading.Event()
        
        ping_spinner = threading.Thread(
            target=run_spinner_thread,
            args=("Measuring ping", ping_stop_event)
        )
        ping_spinner.daemon = True
        ping_spinner.start()
        
        time.sleep(0.5)
        
        ping_stop_event.set()
        ping_spinner.join(timeout=1)
        
        clear_current_line()
        ping_ms = st.results.ping
        print(f"{Fore.GREEN}Ping: {ping_ms:.2f} ms{Style.RESET_ALL}")
        
        return download_speed_mbps, upload_speed_mbps, ping_ms, server_info

    except Exception as e:
        clear_current_line()
        display_status(f"An unexpected error occurred: {e}", "error")
        return None, None, None, None

if __name__ == "__main__":
    display_status("Starting Internet Speed Test...", "info")
    
    download, upload, ping, server_info = run_speed_test()

    if download is not None:
        display_results(download, upload, ping, server_info)
    else:
        display_status("Speed test failed.", "error")
    
    input(f"\n{Fore.CYAN}Press Enter to exit...{Style.RESET_ALL}")

