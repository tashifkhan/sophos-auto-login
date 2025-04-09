import subprocess
import sys

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

def main():
    pids = find_autologin_pids()
    kill_processes(pids)

if __name__ == "__main__":
    main()
