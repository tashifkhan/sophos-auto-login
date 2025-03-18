import sys
from Credentials import Creditial
from logout import logout

def exit_handler(credentials: Creditial, cred_index: int | None = None,  signal=None, frame=None):
    """Handles exit by logging out and terminating the script."""
    print("\nExiting...")
    if not cred_index:
        for cred in credentials:
            logout(cred)
    else:
        logout(cred_index[cred_index])
    sys.exit(0)