import requests
from .Credentials import Creditial
import xml.etree.ElementTree as ET
import time
import os

def login(credentials: list[Creditial]) -> tuple[bool, int]:
    cred_index = 0
    if len(credentials) == 0:
        print("No credentials found.")
        return True, cred_index

    for cred in credentials:
        username = cred['username']
        password = cred['password']

        payload = {
            'mode': '191',
            'username': username,
            'password': password, 
            'a': '1661062428616'
        }

        with requests.Session() as s:
            p = s.post('http://172.16.68.6:8090/httpclient.html', data=payload)
            if p.status_code == 200:
                xml_content = p.content
                root = ET.fromstring(xml_content)
                message_element = root.find('message')
                if message_element is not None:
                    message_text = message_element.text
                    if (message_text == 'Login failed. You have reached the maximum login limit.' or
                        message_text == 'Your data transfer has been exceeded, Please contact the administrator'):
                        print(f'Login failed for {username}. Trying the next credentials.\n')
                    elif message_text == "You are signed in as {username}":
                        print(f"Success\nConnected using {username}!\n")
                        time.sleep(2*60)
                        os.system("clear")
                        return False, cred_index
                    else:
                        print("Unknown response:", message_text, "\nusername:", username)
                else:
                    print("Message element not found.")
            else:
                print("Error Response:", p)
        cred_index += 1

    print("All login attempts failed.")
    return True, cred_index