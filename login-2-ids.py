import requests
import time
from lxml import etree
import xml.etree.ElementTree as ET

#fill the username and password first
# username1 and password1 are secondary ids for login in case username1 is already logged in

username1 = '********'
password1 = '********'
username = '********'
password = '********'
def login(username, password):
    payload = {
        'mode': '191',
        'username': username,
        'password': password,
        'a': '1661062428616'
    }
    while True:
        with requests.Session() as s:
            p = s.post('http://172.16.68.6:8090/httpclient.html', data=payload)
            if p.status_code == 200:
                xml_content = p.content
                root = ET.fromstring(xml_content)
                message_element = root.find('message')
                if message_element is not None:
                    message_text = message_element.text
                    print(message_text)
                    if(message_text == 'Login failed. You have reached the maximum login limit.' or message_text == 'Your data transfer has been exceeded, Please contact the administrator'):
                        login(username1,password1)
                    elif(message_text == 'You are signed in as {username}'):
                        print("Connected!")
                        time.sleep(1700)
                else:
                    print("Message element not found.")
            else:
                print("Error Response:", p)

login(username, password)