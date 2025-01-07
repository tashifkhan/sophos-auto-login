import tkinter as tk
from tkinter import ttk, messagebox
import os
import requests
import time
import xml.etree.ElementTree as ET
import sqlite3
import bcrypt
from cryptography.fernet import Fernet
from getpass import getpass
import os
import threading
import time

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

def logout(credential) -> int:

    payload = {
        'mode': '193',
        'username': credential['username'],
        'password': credential['password'],
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


class SophosLoginGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sophos Auto Login")
        self.root.geometry("400x600")
        
        # Theme settings
        self.themes = {
            "light": {
                "bg": "#f0f0f0",
                "fg": "#000000",
                "button_bg": "#007bff",
                "button_fg": "#ffffff",
                "entry_bg": "#ffffff",
                "frame_bg": "#ffffff",
                "accent": "#e9ecef",
                "hover": "#0056b3"
            },
            "dark": {
                "bg": "#1e1e1e",
                "fg": "#ffffff",
                "button_bg": "#0d6efd",
                "button_fg": "#ffffff",
                "entry_bg": "#2d2d2d",
                "frame_bg": "#252526",
                "accent": "#3c3c3c",
                "hover": "#0b5ed7"
            }
        }
        
        self.current_theme = "dark"
        self.credential_manager = CredentialManager()
        self.login_thread = None
        self.running = False
        
        self.setup_styles()
        self.create_widgets()
        self.load_theme()
        
    def setup_styles(self):
        self.style = ttk.Style()
        
        # Configure common styles
        self.style.configure("TLabel", font=("Helvetica", 10))
        self.style.configure("TButton", font=("Helvetica", 10), padding=10)
        self.style.configure("TEntry", font=("Helvetica", 10), padding=5)
        self.style.configure("TLabelframe", font=("Helvetica", 10, "bold"))
        
        # Custom styles
        self.style.configure("Custom.TButton",
                           font=("Helvetica", 10, "bold"),
                           padding=10)
        
        self.style.configure("Theme.TButton",
                           font=("Helvetica", 10),
                           padding=5)
                           
    def create_widgets(self):
        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Theme switcher
        self.theme_frame = ttk.Frame(self.main_frame)
        self.theme_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.theme_btn = ttk.Button(
            self.theme_frame,
            text="🌙 Dark Mode" if self.current_theme == "light" else "☀️ Light Mode",
            command=self.toggle_theme,
            style="Theme.TButton"
        )
        self.theme_btn.pack(side=tk.RIGHT)
        
        # Credentials Frame
        self.cred_frame = ttk.LabelFrame(self.main_frame, text="Credentials", padding="10")
        self.cred_frame.pack(fill=tk.X, pady=10)
        
        # Username entry
        ttk.Label(self.cred_frame, text="Username:").pack(anchor="w")
        self.username_entry = ttk.Entry(self.cred_frame, style="Custom.TEntry")
        self.username_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Password entry
        ttk.Label(self.cred_frame, text="Password:").pack(anchor="w")
        self.password_entry = ttk.Entry(self.cred_frame, show="*", style="Custom.TEntry")
        self.password_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Add credential button
        self.add_cred_btn = ttk.Button(
            self.cred_frame,
            text="Add Credentials",
            command=self.add_credentials,
            style="Custom.TButton"
        )
        self.add_cred_btn.pack(fill=tk.X)
        
        # Control Frame
        self.control_frame = ttk.LabelFrame(self.main_frame, text="Auto Login Control", padding="10")
        self.control_frame.pack(fill=tk.X, pady=10)
        
        # Start/Stop button
        self.toggle_btn = ttk.Button(
            self.control_frame,
            text="Start Auto Login",
            command=self.toggle_auto_login,
            style="Custom.TButton"
        )
        self.toggle_btn.pack(fill=tk.X)
        
        # Status label
        self.status_var = tk.StringVar(value="Status: Stopped")
        self.status_label = ttk.Label(
            self.control_frame,
            textvariable=self.status_var
        )
        self.status_label.pack(pady=10)
        
    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.load_theme()
        
    def load_theme(self):
        theme = self.themes[self.current_theme]
        
        # Configure root window
        self.root.configure(bg=theme["bg"])
        
        # Configure ttk styles
        self.style.configure("TFrame", background=theme["bg"])
        self.style.configure("TLabel",
                           background=theme["bg"],
                           foreground=theme["fg"])
        
        self.style.configure("TLabelframe",
                           background=theme["frame_bg"])
        self.style.configure("TLabelframe.Label",
                           background=theme["bg"],
                           foreground=theme["fg"])
        
        # Configure custom button styles
        self.style.configure("Custom.TButton",
                           background=theme["button_bg"],
                           foreground=theme["button_fg"])
        self.style.map("Custom.TButton",
                      background=[("active", theme["hover"])])
        
        self.style.configure("Theme.TButton",
                           background=theme["accent"],
                           foreground=theme["fg"])
        self.style.map("Theme.TButton",
                      background=[("active", theme["hover"])])
        
        # Configure entry style
        self.style.configure("TEntry",
                           fieldbackground=theme["entry_bg"],
                           foreground=theme["fg"])
        
        # Update theme button text
        self.theme_btn.configure(
            text="🌙 Dark Mode" if self.current_theme == "light" else "☀️ Light Mode"
        )
        
        # Force update all widgets
        self.root.update_idletasks()
        
    def add_credentials(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
            
        try:
            self.credential_manager.add_credential_gui(username, password)
            messagebox.showinfo("Success", "Credentials added successfully!")
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def toggle_auto_login(self):
        if not self.running:
            self.running = True
            self.toggle_btn.configure(text="Stop Auto Login")
            self.login_thread = threading.Thread(target=self.auto_login_loop)
            self.login_thread.daemon = True
            self.login_thread.start()
        else:
            self.running = False
            self.toggle_btn.configure(text="Start Auto Login")
            self.status_var.set("Status: Stopped")
            
    def auto_login_loop(self):
        count = 0
        while self.running:
            count += 1
            self.status_var.set(f"Status: Login attempt {count}")
            if login(self.credential_manager) != 0:
                self.running = False
                self.root.after(0, self.toggle_auto_login)
                break
            
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        if self.running:
            self.running = False
            if self.login_thread:
                self.login_thread.join()
        self.root.destroy()

if __name__ == "__main__":
    app = SophosLoginGUI()
    app.run()
