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
    sys.exit(0)