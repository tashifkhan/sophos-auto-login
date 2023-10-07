import requests
import time
import xml.etree.ElementTree as ET

# Define a list of dictionaries containing user IDs and passwords
credentials = [
    {'username': 'username1', 'password': 'password1'},
    {'username': 'username2', 'password': 'password2'},
    {'username': 'username3', 'password': 'password3'},
    {'username': 'username4', 'password': 'password4'}
]

def login_with_credentials(credentials):
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
            p = s.post('http://172.16.68.6:8090/httpclient.html', data=payload) #jiit sophos portal link change it to your institutions' link
            if p.status_code == 200:
                xml_content = p.content
                root = ET.fromstring(xml_content)
                message_element = root.find('message')
                if message_element is not None:
                    message_text = message_element.text
                    print(message_text)
                    if (message_text == 'Login failed. You have reached the maximum login limit.' or
                            message_text == 'Your data transfer has been exceeded, Please contact the administrator'):
                        print(f'Login failed for {username}. Trying the next credentials.')
                    elif message_text == 'You are signed in as {username}':
                        print(f"Connected using {username}!")
                        time.sleep(1700)
                        return  # Successful login, exit the loop
                    else:
                        print("Unknown response:", message_text)
                else:
                    print("Message element not found.")
            else:
                print("Error Response:", p)

    print("All login attempts failed.")

# Call the function with the list of credentials
login_with_credentials(credentials)
