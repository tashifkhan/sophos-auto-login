import sqlite3
import os
import sys
from getpass import getpass
import csv

class CredentialManger: 
    def __init__(self, db_path=None):
        self.db_path = db_path if db_path else self.get_db_path()
        self.setup_database()
    
    def get_db_path(self):
        """Get the correct database path based on execution context."""
        if getattr(sys, 'frozen', False):  # Running as a PyInstaller EXE
            base_dir = sys._MEIPASS  # PyInstaller's temp directory
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))  # Normal script directory
        
        return os.path.join(base_dir, "credentials.db")

    def setup_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
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
                selection = int(input("\nSelect a user to edit (number): "))
                if selection < 1 or selection > len(users):
                    print("Invalid selection.")
                    return None
                
                user_id, username = users[selection-1]
                
                cursor.execute("SELECT password FROM credentials WHERE id = ?", (user_id,))
                current_password = cursor.fetchone()[0]
                
                print(f"\nEditing credentials for: {username}")
                
                new_username = input(f"Enter new username (leave empty to keep '{username}'): ")
                print(f"\nCurrent password: {current_password}")
                new_password = getpass("\nEnter new password (leave empty to keep current): ")
                
                changes_made = False
                
                if new_username and new_username != username:
                    try:
                        cursor.execute("UPDATE credentials SET username = ? WHERE id = ?", 
                                     (new_username, user_id))
                        username = new_username
                        changes_made = True
                        print("Username updated successfully!")
                    except sqlite3.IntegrityError:
                        print("Error: That username already exists! Username not updated.")
                
                if new_password:
                    cursor.execute("UPDATE credentials SET password = ? WHERE id = ?", 
                                 (new_password, user_id))
                    current_password = new_password
                    changes_made = True
                    print("Password updated successfully!")
                
                if changes_made:
                    conn.commit()
                else:
                    print("No changes made.")
                
                return {
                    'username': username,
                    'password': current_password
                }
                
            except (ValueError, IndexError):
                print("Invalid selection. Please try again.")
                return None

    def delete_credential(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id, username FROM credentials")
            users = cursor.fetchall()
            
            if not users:
                print("No credentials found to delete.")
                return False
            
            print("Available users:")
            for i, (_, username) in enumerate(users, 1):
                print(f"{i}. {username}")
            
            try:
                selection = int(input("Select a user to delete (number) or 0 to cancel: "))
                if selection == 0:
                    print("Deletion cancelled.")
                    return False
                    
                if selection < 1 or selection > len(users):
                    print("Invalid selection.")
                    return False
                
                user_id, username = users[selection-1]
                
                confirm = input(f"Are you sure you want to delete credentials for '{username}'? (y/n): ").lower()
                if confirm != 'y':
                    print("Deletion cancelled.")
                    return False
                
                cursor.execute("DELETE FROM credentials WHERE id = ?", (user_id,))
                conn.commit()
                
                print(f"Credentials for '{username}' deleted successfully!")
                return True
                
            except (ValueError, IndexError):
                print("Invalid selection. Please try again.")
                return False

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

    def import_from_csv(self, csv_path):
        if not os.path.exists(csv_path):
            print(f"Error: CSV file not found at {csv_path}")
            return (0, 0)
        
        try:
            with open(csv_path, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                field_mapping = {}
                for field in reader.fieldnames:
                    field_lower = field.strip().lower()

                    if field_lower in ["username", "userid (enrolment number)"]:
                        field_mapping["username"] = field

                    elif field_lower == "password":
                        field_mapping["password"] = field
                        
                if "username" not in field_mapping or "password" not in field_mapping:
                    print("Error: CSV must contain 'username' (or 'UserID (Enrolment Number)') and 'password' columns")
                    return False

                records_added = 0
                records_skipped = 0

                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    for row in reader:
                        try:
                            username = row[field_mapping["username"]]
                            password = row[field_mapping["password"]]
                            cursor.execute(
                                "INSERT INTO credentials (username, password) VALUES (?, ?)",
                                (username, password)
                            )
                            records_added += 1
                        except sqlite3.IntegrityError:
                            records_skipped += 1
                    conn.commit()

                print(f"Import completed: {records_added} records added, {records_skipped} duplicates skipped")
                return True
                
        except Exception as e:
            print(f"Error importing CSV data: {e}")
            return (0, 0)

