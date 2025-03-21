import sqlite3
import os
from getpass import getpass
import csv

class CredentialManger:
    def __init__(self, db_path = os.path.join(os.path.dirname(__file__), "credentials.db")):
        self.db_path = db_path
        self.setup_database()

    def setup_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                )
            ''')
            conn.commit()

    def add_credential(self):
        username = input("Enter username: ")
        password = getpass("Enter password: ")

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO credentials
                    (username, password)
                    VALUES (?, ?)""",
                    (username, password))
                conn.commit()
                print("Credential added successfully!")

        except sqlite3.IntegrityError:
            print("Username already exists!")

    def get_credentials(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username, password FROM credentials")
            return [{
                'username': row[0],
                'password': row[1],
            } for row in cursor.fetchall()]

    def edit_credentials(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id, username FROM credentials")
            users = cursor.fetchall()
            
            if not users:
                print("No credentials found to edit.")
                return None
            
            print("Available users:")
            for i, (_, username) in enumerate(users, 1):
                print(f"{i}. {username}")
            
            try:
                selection = int(input("Select a user to edit (number): "))
                if selection < 1 or selection > len(users):
                    print("Invalid selection.")
                    return None
                
                user_id, username = users[selection-1]
                
                cursor.execute("SELECT password FROM credentials WHERE id = ?", (user_id,))
                current_password = cursor.fetchone()[0]
                
                print(f"Editing credentials for: {username}")
                print(f"Current password: {current_password}")
                
                new_password = getpass("Enter new password (leave empty to keep current): ")
                
                if new_password:
                    cursor.execute("UPDATE credentials SET password = ? WHERE id = ?", 
                                  (new_password, user_id))
                    conn.commit()
                    print("Password updated successfully!")
                else:
                    print("Password unchanged.")
                
                return {
                    'username': username,
                    'password': new_password if new_password else current_password
                }
                
            except (ValueError, IndexError):
                print("Invalid selection. Please try again.")
                return None

    def export_to_csv(self, output_path=None):
        
        if not output_path:
            output_path = os.path.join(os.path.dirname(self.db_path), "credentials.csv")
        
        credentials = self.get_credentials()
        
        if not credentials:
            print("No credentials found to export.")
            return None
        
        try:
            with open(output_path, 'w', newline='') as csvfile:
                fieldnames = ['username', 'password']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for cred in credentials:
                    writer.writerow(cred)
                
            print(f"Credentials exported successfully to {output_path}")
            return output_path
        except Exception as e:
            print(f"Error exporting credentials: {e}")
            return None

