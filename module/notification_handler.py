import platform
import subprocess
import signal


def send_notification(title, message):
    """Send a notification using platform-specific methods."""
    try:

        system = platform.system()
        if system == "Darwin":
            script = f'display notification "{message}" with title "{title}"'
            try:
                subprocess.run(
                    ["osascript", "-e", script],
                    check=False,
                )

            except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
                if not any(sig[0] == signal.SIGINT for sig in signal.signal_check()):
                    print(f"Notification error: {e}")

        elif system == "Linux":
            try:
                subprocess.run(
                    ["notify-send", title, message],
                    check=False,
                )

            except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
                print(f"Notification error: {e}")

        elif system == "Windows":
            try:
                from win10toast import ToastNotifier

                toaster = ToastNotifier()
                toaster.show_toast(title, message, duration=5)

            except Exception as e:
                print(f"Notification error: {e}")

    except Exception as e:
        if not any(sig[0] == signal.SIGINT for sig in signal.signal_check()):
            print(f"Error sending notification: {e}")


if __name__ == "__main__":
    send_notification(
        "Sophos Auto Login",
        "You have been logged out",
    )
