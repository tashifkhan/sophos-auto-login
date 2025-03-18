import requests
import xml.etree.ElementTree as ET
from Credentials import Creditial

def logout(credential : Creditial) -> bool | None:

    username = credential["username"]
    password = credential["password"]

    payload = {
        'mode': '193',
        'username': username,
        'password': password,
        'a': '1661062428616'
    }

    """ Note: htat just visiting this endpoint logs out whatever id is logged in """

    with requests.Session() as s:
        p = s.post('http://172.16.68.6:8090/httpclient.html', data=payload)
        if p.status_code == 200:
            xml_content = p.content
            root = ET.fromstring(xml_content)
            message_element = root.find('message')
            if message_element is not None:
                message_text = message_element.text
                if message_text == "You&#39;ve signed out":
                    print(f"Logged out {username}")
                    return True
            else:
                print("Message element not found.")
                return False
        else:
            print("Error Response:", p)
            return False

if __name__ == "__main__":
    credential = {
        "username": "username",
        "password": "password"
    }
    logout(credential)