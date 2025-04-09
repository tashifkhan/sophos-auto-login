import subprocess

def send_notification(title, message):
    script = f"""
    display notification "{message}" with title "{title}"
    """
    try:
        subprocess.run(['osascript', '-e', script], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error sending notification: {e}")

if __name__ == '__main__':
    send_notification("Sophos Auto Login", "You have been logged out")
