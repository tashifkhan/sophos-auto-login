import os
import requests
import time
import xml.etree.ElementTree as ET
import atexit
import signal
import sys

credentials = [
    {'username': 'username1', 'password': 'password1'},
    {'username': 'username2', 'password': 'password2'},
    {'username': 'username3', 'password': 'password3'},
    {'username': 'username4', 'password': 'password4'}
]

def login(credentials) -> int:

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
                        return 1
                    else:
                        print("Unknown response:", message_text)
                else:
                    print("Message element not found.")
            else:
                print("Error Response:", p)

    print("All login attempts failed.")
    return 0

def logout(credential) -> int:
    
    payload = {
        'mode': '193',
        'username': credential["username"],
        'password': credential["password"],
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
                if message_text == "You&#39;ve signed out":
                    print(f"Logged out {credential['username']}")
                    return 1
            else:
                print("Message element not found.")
                return 0
        else:
            print("Error Response:", p)
            return 0

def exit_handler(signal=None, frame=None):
    print("Exiting...")
    for credential in credentials:
        logout(credential)
    sys.exit(0)


count = 0 
while True: 
    signal.signal(signal.SIGINT, exit_handler)
    count += 1
    duration = (count-1) * 2
    hrs = duration // 60
    mins = duration % 60
    if count > 1:
        if hrs == 0:
            print(f"Running for {mins} minutes...\n\n")
        else:
            print(f"Running for {hrs} hours {mins} minutes...\n\n")
        print(f"Login attempt {count}")
    else:
        print(f"Login attempt {count}")
    if login(credentials) != 0:
        break

atexit.register(exit_handler)