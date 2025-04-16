import sys
from .Credentials import Creditial
from .notification_handler import send_notification
from .logout import logout

def exit_handler(cred_index: int | None, credentials: Creditial, signal=None, frame=None):
    """Handles exit by logging out and terminating the script."""
    send_notification("Sophos Auto Login", "Exiting...")

    fail = False

    print("\nExiting...")
    try:
        if cred_index is None:
            for cred in credentials:
                result = logout(cred)
                if result is "Fail":
                    print("Warning: Timeout occurred while logging out. Stopping logout process.")
                    send_notification("Sophos Auto Login", "Timeout occurred during logout. Process stopped.")
                    fail = True
                    break
                elif result is False:
                    print("Warning: Failed to logout user. Continuing with next credential.")
                    fail = True
        else:
            if not (0 <= cred_index < len(credentials)):
                print("Warning: credential index out of range, logging out all credentials")
                for cred in credentials:
                    result = logout(cred)
                    if result is "Fail":
                        print("Warning: Timeout occurred while logging out. Stopping logout process.")
                        send_notification("Sophos Auto Login", "Timeout occurred during logout. Process stopped.")
                        fail = True
                        break
                    elif result is False:
                        print("Warning: Failed to logout user. Continuing with next credential.")
                        fail = True
            else:
                if logout(credentials[cred_index]) is None:
                    print("Warning: Timeout occurred while logging out.")
                    fail = True
        
        if not fail:
            send_notification("Sophos Auto Login", "You have been logged out & Exited")
        else:
            send_notification("Sophos Auto Login", "Some logout operations failed. Exited.")

    except Exception as e:
        print(f"Error during logout: {e}")
        send_notification("Sophos Auto Login", f"Error during logout: {e}")
        fail = True

    finally:
        if fail:
            print("Logout failed, but exiting anyway.")
        else:
            print("Logout successful.")

    # Only call sys.exit(0) if not invoked as an atexit callback.
    if signal is not None or frame is not None:
        send_notification("Sophos Auto Login", "Exited")    
        sys.exit(0)