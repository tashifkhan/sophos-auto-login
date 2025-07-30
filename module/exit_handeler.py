import sys
from .Credentials import Creditial
from .notification_handler import send_notification
from .logout import logout
from . import state


def exit_handler(
    cred_index: int | None = None,
    credentials: Creditial = None,
    signal=None,
    frame=None,
):
    """Handles exit by logging out and terminating the script."""

    # fallback if no cred_index passed
    if cred_index is None or credentials is None:
        cred_index, credential = state.get_active_credential()
        if credential is not None:
            credentials = state.credentials

    send_notification(
        "Sophos Auto Login",
        "Exiting...",
    )

    fail = False

    print("\nExiting...")
    try:
        if (
            cred_index is not None
            and credentials
            and 0 <= cred_index < len(credentials)
        ):
            print(
                f"Logging out active credential: {credentials[cred_index]['username']}"
            )

            result = logout(credentials[cred_index])
            if result == "Fail":
                print("Warning: Timeout occurred while logging out.")
                send_notification(
                    "Sophos Auto Login",
                    "Timeout occurred during logout.",
                )
                fail = True

            elif result is False:
                print("Warning: Failed to logout user.")
                send_notification(
                    "Sophos Auto Login",
                    "Failed to logout user.",
                )
                fail = True

            else:
                fail = False
                print(
                    f"Successfully logged out: {credentials[cred_index]['username']}",
                )
                send_notification("Sophos Auto Login", "Exited")
        else:
            print("No active credential to logout.")
            fail = False

        if not fail:
            send_notification(
                "Sophos Auto Login",
                "You have been logged out & Exited",
            )
        else:
            send_notification(
                "Sophos Auto Login",
                "Logout failed. Exited.",
            )

    except Exception as e:
        print(f"Error during logout: {e}")
        send_notification(
            "Sophos Auto Login",
            f"Error during logout: {e}",
        )
        fail = True

    finally:
        if fail:
            print("Logout failed, but exiting anyway.")
        else:
            print("Logout successful.")

    if signal is not None or frame is not None:
        send_notification(
            "Sophos Auto Login",
            "Exited",
        )
        sys.exit(0)
