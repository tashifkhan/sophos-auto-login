import sys
from .Credentials import Creditial
from .logout import logout

def exit_handler(cred_index: int | None, credentials: Creditial, signal=None, frame=None):
    """Handles exit by logging out and terminating the script."""
    print("\nExiting...")
    if cred_index is None:
        for cred in credentials:
            logout(cred)
    else:
        logout(credentials[cred_index])
    # Only call sys.exit(0) if not invoked as an atexit callback.
    if signal is not None or frame is not None:
        sys.exit(0)