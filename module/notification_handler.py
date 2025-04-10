import subprocess
import sys

def mac_send_notification(title, message):
    script = f"""
    display notification "{message}" with title "{title}"
    """
    try:
        subprocess.run(['osascript', '-e', script], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error sending notification: {e}")

def windows_send_notification(title, message):
    from win10toast import ToastNotifier
    toaster = ToastNotifier()
    toaster.show_toast(
        title,
        message,
        duration=10,
        threaded=True,
    )

def linux_send_notification(title, message):
    import notify2

    notify2.init("Sophos Auto Login")

    n = notify2.Notification(title, message)
    n.set_urgency(notify2.URGENCY_NORMAL)
    n.show()


def send_notification(title, message):
    """Send a notification based on the operating system."""
    if sys.platform == "darwin":
        mac_send_notification(title, message)
    elif sys.platform.startswith("win"):
        windows_send_notification(title, message)
    elif sys.platform.startswith("linux"):
        linux_send_notification(title, message)
    else:
        print(f"Unsupported OS: {sys.platform}. Notification not sent.")

if __name__ == '__main__':
    mac_send_notification("Sophos Auto Login", "You have been logged out")
