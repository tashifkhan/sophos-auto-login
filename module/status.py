import os
import re
from pathlib import Path
from datetime import datetime
import colorama
from colorama import Fore, Back, Style

# Initialize colorama to support colors on all platforms
colorama.init(autoreset=False)

def get_daemon_status(with_colors=True):
    """
    Get the running status of the sophos-autologin daemon by reading from the log file.
    
    Args:
        with_colors (bool): Whether to include terminal color codes in status strings
    
    Returns:
        dict: A dictionary containing status information like:
            - running (bool): Whether the daemon appears to be active
            - last_activity (str): Timestamp of the last log entry
            - last_action (str): The last action performed
            - error (str): Any error message if present
            - status_str (str): A human-readable status string (colorized if with_colors=True)
            - time_since_activity (str): Human-readable time since last activity
            - runtime (str): The daemon runtime if available
            - connection_status (str): Current connection status (Connected/Disconnected)
            - active_credential (str): Currently active credential being used
    """
    log_path = Path(os.path.join(Path.home(), ".sophos-autologin", "sophos-autologin.log"))
    
    status = {
        "running": False,
        "last_activity": None,
        "last_action": None,
        "error": None,
        "status_str": "Unknown",
        "time_since_activity": None,
        "runtime": None,
        "connection_status": None,
        "active_credential": None
    }
    
    if not log_path.exists():
        status["error"] = "Log file not found, daemon may not be running"
        status["status_str"] = _colorize("⨯ Not running (no log file)", Fore.RED, with_colors)
        return status
    
    try:
        # Read the last few lines from the log file (most recent entries)
        with open(log_path, 'r') as log_file:
            # Get last 20 lines to analyze
            lines = log_file.readlines()[-20:] if log_file.readable() else []
            
        if not lines:
            status["error"] = "Log file is empty"
            status["status_str"] = _colorize("⨯ Not running (empty log file)", Fore.RED, with_colors)
            return status
        
        # Extract timestamp from the most recent log entry
        timestamp_pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'
        for line in reversed(lines):
            timestamp_match = re.search(timestamp_pattern, line)
            if timestamp_match:
                timestamp_str = timestamp_match.group(1)
                status["last_activity"] = timestamp_str
                break
        
        # Check for connection status, runtime, and active credential
        connection_pattern = r'CONNECTION CHECK \| Status: ([✓✗]) (Connected|Disconnected) \| Runtime: (.*?)$'
        credential_pattern = r'Active credential: (.*?)$'
        
        # Find the latest connection check, credential info and action
        for line in reversed(lines):
            # Check for connection status and runtime
            conn_match = re.search(connection_pattern, line)
            if conn_match and not status.get("connection_status"):
                status["connection_status"] = conn_match.group(2)
                status["runtime"] = conn_match.group(3)
                continue
                
            # Check for active credential
            cred_match = re.search(credential_pattern, line)
            if cred_match and not status.get("active_credential"):
                status["active_credential"] = cred_match.group(1)
                continue
                
            # Look for actions
            if "➤ Internet is connected" in line:
                status["last_action"] = "Internet is connected"
                status["running"] = True
                if not status.get("connection_status"):
                    status["connection_status"] = "Connected"
                
            elif "⟳ Performing scheduled re-login" in line:
                status["last_action"] = "Performing scheduled re-login"
                status["running"] = True
                
            elif "LOGIN ATTEMPT" in line:
                login_match = re.search(r'LOGIN ATTEMPT #(\d+)', line)
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
            
            # If we've found all the information we need, we can stop
            if status["last_action"] and status["connection_status"] and status["active_credential"] and status["runtime"]:
                break
        
        # If last log is older than 30 minutes, daemon might be stuck or not running
        if status["last_activity"]:
            try:
                last_time = datetime.strptime(status["last_activity"], "%Y-%m-%d %H:%M:%S")
                current_time = datetime.now()
                time_diff_seconds = (current_time - last_time).total_seconds()
                time_diff_minutes = time_diff_seconds / 60
                
                # Create human-readable time difference
                status["time_since_activity"] = _format_time_difference(time_diff_seconds)
                
                if time_diff_minutes > 30:
                    status["running"] = False
                    status["error"] = f"No activity for {status['time_since_activity']}, daemon may be stuck or not running"
            except ValueError:
                # If datetime parsing fails, ignore this check
                pass
        
        # Create a nice status string for terminal display
        status["status_str"] = _create_status_string(status, with_colors)
                
    except Exception as e:
        status["error"] = f"Error reading log file: {str(e)}"
        status["status_str"] = _colorize(f"⨯ Error: {str(e)}", Fore.RED, with_colors)
    
    return status

def _format_time_difference(seconds):
    """Format a time difference in seconds to a human-readable string."""
    if seconds < 60:
        return f"{int(seconds)} seconds"
    elif seconds < 3600:
        return f"{int(seconds/60)} minutes"
    elif seconds < 86400:
        hours = int(seconds/3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours} hours{f', {minutes} minutes' if minutes else ''}"
    else:
        days = int(seconds/86400)
        hours = int((seconds % 86400) / 3600)
        return f"{days} days{f', {hours} hours' if hours else ''}"

def _colorize(text, color_code, with_colors=True):
    """Add color to text if colors are enabled."""
    if with_colors:
        return f"{color_code}{text}{Style.RESET_ALL}"
    return text

def _create_status_string(status, with_colors=True):
    """Create a human-readable status string with optional color."""
    if status["running"]:
        symbol = "✓"
        color = Fore.GREEN
        base_msg = f"{symbol} Running"
        
        if status["connection_status"]:
            conn_color = Fore.GREEN if status["connection_status"] == "Connected" else Fore.RED
            conn_symbol = "✓" if status["connection_status"] == "Connected" else "✗"
            conn_status = _colorize(f"{conn_symbol} {status['connection_status']}", conn_color, with_colors)
            base_msg += f" - Network: {conn_status}"
        
        if status["last_action"]:
            base_msg += f" - Last action: {status['last_action']}"
            
        if status["runtime"]:
            base_msg += f" - Runtime: {status['runtime']}"
            
        if status["active_credential"]:
            base_msg += f" - Using: {status['active_credential']}"
            
        if status["time_since_activity"]:
            base_msg += f" ({status['time_since_activity']} ago)"
            
        return base_msg if not with_colors else f"{color}{symbol}{Style.RESET_ALL} {base_msg.split(' ', 1)[1]}"
    else:
        symbol = "⨯"
        color = Fore.RED
        base_msg = f"{symbol} Not running"
        
        if status["last_action"]:
            base_msg += f" - Last action: {status['last_action']}"
            
        return _colorize(base_msg, color, with_colors)
    
if __name__ == "__main__":
    status = get_daemon_status()
    
    print(f"\n{Style.BRIGHT}{'=' * 60}{Style.RESET_ALL}")
    print(f"{Style.BRIGHT}{Fore.BLUE}  SOPHOS AUTO LOGIN - STATUS{Style.RESET_ALL}")
    print(f"{Style.BRIGHT}{'=' * 60}{Style.RESET_ALL}\n")
    
    # Main status line
    print(status["status_str"])
    
    # If there's an error, show it immediately after the status line
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