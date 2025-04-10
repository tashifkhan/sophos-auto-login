from .notification_handler import send_notification
import subprocess
import sys
import os

# General purpose script to kill processes for any progarm
def find_autologin_pids():
    """
    Run 'ps aux' and filter for lines containing 'autologin'
    (ignoring the grep command itself) to extract PIDs.
    """
    try:
        ps_output = subprocess.run(
            ["ps", "aux"], check=True,
            stdout=subprocess.PIPE, text=True
        ).stdout
    except subprocess.CalledProcessError as error:
        print("Error running ps aux:", error)
        sys.exit(1)

    lines = ps_output.splitlines()
    pids = []
    for line in lines:
        # Filter lines that mention "autologin" but not the grep command
        if "autologin" in line and "grep" not in line:
            parts = line.split()
            if len(parts) > 1:
                # PID is the second column
                pids.append(parts[1])
    return pids

def kill_processes(pids):
    """
    Kill the processes with the provided PIDs.
    """
    if not pids:
        print("No autologin processes found.")
        return

    print(f"Found autologin processes with PIDs: {', '.join(pids)}")
    try:
        subprocess.run(["kill"] + pids, check=True)
        print("Processes killed successfully.")
    except subprocess.CalledProcessError as error:
        print("Error killing processes:", error)

# Forgot was storing PID in ~/.sophos-autologin/sophos-autologin.pid
def stop_sophos():
    """
    Stop the Sophos autologin process by killing it.
    """
    pid_file = os.path.expanduser("~/.sophos-autologin/sophos-autologin.pid")
    try:
        with open(pid_file, "r") as file:
            pid = file.read().strip()
            print(f"Stopping Sophos autologin process with PID: {pid}")
            subprocess.run(["kill", pid], check=True)
            print("Sophos autologin process stopped successfully.")
    except FileNotFoundError:
        print(f"PID file not found: {pid_file}")
    except subprocess.CalledProcessError as error:
        print("Error stopping Sophos autologin process:", error)

# but will the general purpose ?
# coz that shit aso exits the non deamon ones too

def main():
    pids = find_autologin_pids()
    send_notification("Sophos Auto Login", "Daemon terminated")
    kill_processes(pids)

if __name__ == "__main__":
    main()
