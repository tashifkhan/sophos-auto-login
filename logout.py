import requests
import xml.etree.ElementTree as ET

def logout(credential) -> int:

    payload = {
        'mode': '193',
        'username': credential[0],
        'password': credential[1],
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
                    print(f"Logged out {credential[0]}")
                    return 1
            else:
                print("Message element not found.")
                return 0
        else:
            print("Error Response:", p)
            return 0

if __name__ == "__main__":
    credential = ('username', 'password')
    credential = ('username', 'password')