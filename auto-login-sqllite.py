import os
import requests
import time
import xml.etree.ElementTree as ET
import atexit
import signal
import sys
import sqlite3
import bcrypt
from cryptography.fernet import Fernet
from getpass import getpass
import logout

class CredentialManager:
    def __init__(self, db_path="credentials.db"):
        self.db_path = db_path
        self.key_path = "encryption.key"
        self.initialize_encryption()
        self.setup_database()

    def initialize_encryption(self):
        if not os.path.exists(self.key_path):
            key = Fernet.generate_key()
            with open(self.key_path, "wb") as key_file:
                key_file.write(key)
        else:
            with open(self.key_path, "rb") as key_file:
                key = key_file.read()
        self.fernet = Fernet(key)

    def setup_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS credentials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    password_encrypted TEXT NOT NULL
                )
            ''')
            conn.commit()

    def add_credential(self):
        username = input("Enter username: ")
        password = getpass("Enter password: ")
        
        # Hash password for verification
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        # Encrypt password for payload
        password_encrypted = self.fernet.encrypt(password.encode('utf-8'))
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO credentials 
                    (username, password_hash, password_encrypted) 
                    VALUES (?, ?, ?)""",
                    (username, password_hash, password_encrypted))
                conn.commit()
                print("Credential added successfully!")
        except sqlite3.IntegrityError:
            print("Username already exists!")

    def get_credentials(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username, password_hash, password_encrypted FROM credentials")
            return [{
                'username': row[0],
                'password_hash': row[1],
                'password': self.fernet.decrypt(row[2]).decode('utf-8')
            } for row in cursor.fetchall()]

    def verify_password(self, stored_password_hash, provided_password):
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password_hash)

def login(credential_manager) -> int:
    global cred_index
    cred_index = 0
    credentials = credential_manager.get_credentials()
    
    for cred in credentials:
        username = cred['username']
        password = cred['password']  # Now using decrypted password

        payload = {
            'mode': '191',
            'username': username,
            'password': password,  # Plain text password for payload
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
                    if message_text == f"You are signed in as {username}":
                        print(f"Success\nConnected using {username}!\n")
                        time.sleep(2*60)
                        os.system("clear")
                        return 0
                    else:
                        print(f'Login failed for {username}. Trying next credentials.\n')
                else:
                    print("Message element not found.")
            else:
                print("Error Response:", p)
        cred_index += 1

    print("All login attempts failed.")
    return 1

def exit_handler(credential, signal=None, frame=None):
    print("\nExiting...")
    logout.logout(credential)
    sys.exit(0)

def main():
    credential_manager = CredentialManager()
    
    
    while True:
        print("\n1. Add new login credentials")
        print("2. Start auto-login process")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == "1":
            credential_manager.add_credential()
        elif choice == "2":
            count = 0
            while True:
                signal.signal(signal.SIGINT, exit_handler)
                count += 1
                duration = (count-1) * 2
                hrs = duration // 60
                mins = duration % 60
                
                print(f"\nLogin attempt {count}")
                if count > 1:
                    if hrs == 0:
                        print(f"Running for {mins} minutes...\n")
                    else:
                        print(f"Running for {hrs} hours {mins} minutes...\n")
                
                if login(credential_manager) != 0:
                    break
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    atexit.register(exit_handler)
    main()