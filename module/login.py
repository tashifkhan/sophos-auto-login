import requests
from module.Credentials import Creditial
from .notification_handler import send_notification
from .check_internet import check_internet_connection
from .internet_speedtest import run_speed_test as speed_test
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
                        send_notification("Sophos Auto Login", f"{username} login failed")
                    elif message_text == "You are signed in as {username}":
                        print(f"Success\nConnected using {username}!\n")
                        time.sleep(2*60)
                        os.system("clear")
                        if check_internet_connection():
                            try:
                                speed_results = speed_test()
                                download_mbps = speed_results['download_speed_mbps']
                                upload_mbps = speed_results['upload_speed_mbps']
                                ping_ms = speed_results['ping_ms']
                                server_info = speed_results['server_info']

                                print(f"Speed Test Results:")
                                print(f"Download: {download_mbps:.2f} Mbps")
                                print(f"Upload: {upload_mbps:.2f} Mbps")
                                print(f"Ping: {ping_ms:.2f} ms")
                                print(f"Server: {server_info}")

                                speed_message = f"Connected using {username}\nDownload: {download_mbps:.2f} Mbps\nUpload: {upload_mbps:.2f} Mbps\nPing: {ping_ms:.2f} ms"
                                send_notification("Sophos Auto Login - Connected", speed_message)

                            except Exception as e:
                                print(f"Speed test failed: {str(e)}")
                                send_notification("Sophos Auto Login - Connected", f"Connected using {username}\nSpeed test failed: {str(e)}")

                        else:
                            print("\nNo internet connection.")
                            send_notification("Sophos Auto Login - Connected", f"Connected using {username}\nNo internet connection.")

                        return False, cred_index
                    else:
                        print("Unknown response:", message_text, "\nusername:", username)
                        send_notification("Sophos Auto Login", f"Unknown response for {username}")
                else:
                    print("Message element not found.")
                    send_notification("Sophos Auto Login", f"Error {username} - {"Message element not found."}")
            else:
                print("Error Response:", p)
                send_notification("Sophos Auto Login", f"Error {username} - {p}")
        cred_index += 1

    print("All login attempts failed.")
    return True, cred_index