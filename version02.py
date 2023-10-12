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
# username1, password1 and so on are just placeholders, you have to edit those with your actual credentials

# Defined the login fuction
def login(credentials):
    # Traverese the list for every userid and password stored 
    for cred in credentials:
        username = cred['username']
        password = cred['password']

        # Website meta deta --> essentially required + the login ids and all to be posted (submitted to the website)
        payload = {
            'mode': '191',
            'username': username,
            'password': password,
            'a': '1661062428616'
        }

        with requests.Session() as s:
            p = s.post('http://172.16.68.6:8090/httpclient.html', data=payload)  # p --> responce of the website after posting the payload
            # (JIIT Sophos Portal link) --> Change it to your institutions' link
            if p.status_code == 200:
                xml_content = p.content # Stores/Formats the responce (p) in the form of a xml
                root = ET.fromstring(xml_content) # Creates an XML ElementTree object (root) that can be used to navigate and extract data from the XML document
                message_element = root.find('message') # Only use of root was to locate message and we use it as follows
                if message_element is not None:
                    # Fetches the message produced --> Customise it as per your portal's error messages
                    message_text = message_element.text
                    print(message_text)
                    print("\n")
                    if (message_text == 'Login failed. You have reached the maximum login limit.' or
                            message_text == 'Your data transfer has been exceeded, Please contact the administrator'):
                        print(f'Login failed for {username}. Trying the next credentials.\n')
                    elif message_text == "You are signed in as {username}":
                        print(f"Connected using {username}!\n")
                        time.sleep(1700) # After a successfull login it waits for 28 mins and 20 secs to try to login again
                    else:
                        print("Unknown response:", message_text)
                else:
                    print("Message element not found.")
            else:
                print("Error Response:", p)

    print("All login attempts failed.")

# Call the function with the list of credentials
login(credentials)
