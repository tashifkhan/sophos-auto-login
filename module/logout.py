import requests
import xml.etree.ElementTree as ET
from module.Credentials import Credential
from typing import Union
from .notification_handler import send_notification

def logout(credential : Credential, timeout: int = 5) -> Union[bool, str]: 
    """
    Logs out a user from Sophos
    
    Args:
        credential: User credentials
        timeout: Connection timeout in seconds (default: 10)
    
    Returns:
        Union[bool, str]: True if logout successful, False if failed, "Fail" on timeout
    """
    username = credential["username"]
    password = credential["password"]

    payload = {
        'mode': '193',
        'username': username,
        'password': password,
        'a': '1661062428616'
    }

    """ Note: that just visiting this endpoint logs out whatever id is logged in """

    try:
        with requests.Session() as s:
            p = s.post('http://172.16.68.6:8090/httpclient.html', data=payload, timeout=timeout)
            if p.status_code == 200:
                xml_content = p.content
                root = ET.fromstring(xml_content)
                message_element = root.find('message')
                if message_element is not None:
                    message_text = message_element.text
                    if message_text == "You&#39;ve signed out":
                        print(f"Logged out {username}")
                        send_notification("Sophos Auto Login", f"{username} have been logged out")
                        return True
                else:
                    print("Message element not found.")
                    send_notification("Sophos Auto Login", f"Error logging out {username}")
                    return False
            else:
                print("Error Response:", p)
                return False
            
    except requests.exceptions.Timeout:
        print(f"Timeout occurred while trying to logout {username}")
        send_notification("Sophos Auto Login", f"Timeout occurred while trying to logout {username}")
        return "Fail"
    
    except requests.exceptions.RequestException as e:
        print(f"Request exception: {e}")
        send_notification("Sophos Auto Login", f"Error logging out {username}: {e}")
        return False

if __name__ == "__main__":
    credential = {
        "username": "username",
        "password": "password"
    }
    logout(credential)