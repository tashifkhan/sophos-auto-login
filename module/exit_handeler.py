import sys
from .Credentials import Creditial
from .notification_handler import send_notification
from .logout import logout

def exit_handler(cred_index: int | None, credentials: Creditial, signal=None, frame=None):
    """Handles exit by logging out and terminating the script."""
    send_notification("Sophos Auto Login", "Exiting...")
    print("\nExiting...")
    if cred_index is None:
        for cred in credentials:
            logout(cred)
    else:
        if not (0 <= cred_index < len(credentials)):
            print("Warning: credential index out of range, logging out all credentials")
            for cred in credentials:
                logout(cred)
        else:
            logout(credentials[cred_index])
    
    send_notification("Sophos Auto Login", "You have been logged out & Exited")
    # Only call sys.exit(0) if not invoked as an atexit callback.
    if signal is not None or frame is not None:
        send_notification("Sophos Auto Login", "Exited")    
        sys.exit(0)