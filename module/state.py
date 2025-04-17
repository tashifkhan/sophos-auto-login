"""
Module to maintain global state for the Sophos Auto Login application.
"""

# Store the active credential index
active_credential_index = None

# Store the list of credentials
credentials = []

# Flag to prevent multiple signal handlers from running simultaneously
signal_handler_running = False

def update_active_credential(index, creds=None):
    """Update the active credential index and credentials list."""
    global active_credential_index, credentials
    active_credential_index = index
    if creds is not None:
        credentials = creds
    return active_credential_index

def get_active_credential():
    """Get the currently active credential info."""
    if active_credential_index is not None and 0 <= active_credential_index < len(credentials):
        return active_credential_index, credentials[active_credential_index]
    return None, None
