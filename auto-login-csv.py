import os
import requests
import time
import csv
import xml.etree.ElementTree as ET
import atexit
import signal
import sys

# Make a CSV file called Credentials.csv which will store all the Usernamws & Passwords 
with open("file_path", "r") as cred:    # Change the file_path varible to the the path where you saved your csv file
    file_object = csv.reader(cred)
    next(file_object)   # Considering first line is Headings only thus we skip that line
    credentials = []    # Define a list of dictionaries containing user IDs and passwords
    for creds in file_object:
        credentials.append({'username': creds[0], 'password': creds[1]})

cred_index = None # stores which credintial was used to login 
# Defined the login fuction
def login(credentials) -> int:
    # Traverese the list for every userid and password stored 
    global cred_index
    cred_index = 0
    for cred in credentials:
        username = cred['username']
        password = cred['password']

        # Post request data
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
                xml_content = p.content # Responce is XLM 
                root = ET.fromstring(xml_content) # Creates an XML ElementTree object (root) that can be used to navigate and extract data from the XML document
                message_element = root.find('message') # Only use of root was to locate message and we use it as follows
                if message_element is not None:
                    # Fetches the message produced --> Customise it as per your portal's error messages
                    message_text = message_element.text
                    if (message_text == 'Login failed. You have reached the maximum login limit.' or
                            message_text == 'Your data transfer has been exceeded, Please contact the administrator'):
                        print(f'Login failed for {username}. Trying the next credentials.\n')
                    elif message_text == "You are signed in as {username}":
                        print(f"Success\nConnected using {username}!\n")
                        time.sleep(2*60) # After a successfull login it waits for 2 mins and to try to login again
                        os.system("clear") # Clears the terminal
                        return 0
                    else:
                        print("Unknown response:", message_text)
                else:
                    print("Message element not found.")
            else:
                print("Error Response:", p)
        cred_index += 1

    print("All login attempts failed.")
    return 1

# Almost same process like login function just the mode of the payload has been changed 
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
                if message_text == "You&#39;ve signed out": # Customise it as per your portal's success message
                    print(f"Logged out {credential['username']}")
                    return 1
            else:
                print("Message element not found.")
                return 0
        else:
            print("Error Response:", p)
            return 0

def exit_handler(signal=None, frame=None):
    global cred_index
    print("\nExiting...")
    if cred_index is not None:
        logout(credentials[cred_index])
    sys.exit(0)


# Call the function with the list of credentials
count = 0 # Measures the number of login attempts
while True: 
    signal.signal(signal.SIGINT, exit_handler) # Handels the keyboard interrupt
    count += 1
    duration = (count-1) * 2
    hrs = duration // 60
    mins = duration % 60
    if count > 1:
        if hrs == 0:
            print(f"Running for {mins} minutes...\n")
        else:
            print(f"Running for {hrs} hours {mins} minutes...\n")
        print(f"Login attempt {count}")
    else:
        print(f"Login attempt {count}")
    if login(credentials) != 0:
        break

atexit.register(exit_handler) # Handels all the error exits except the keyboard interrupt