import sqlite3
import csv
import os
import argparse

def import_csv_to_sqlite(csv_path, db_path=None):
    if not db_path:
        db_path = os.path.join(os.path.dirname(__file__), "credentials.db")
    
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        return False
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
            )
        ''')
        conn.commit()
    
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

            with sqlite3.connect(db_path) as conn:
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
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import credentials from CSV to SQLite database")
    parser.add_argument("csv_file", help="Path to the CSV file containing credentials")
    parser.add_argument("--db", help="Path to the SQLite database file (optional)")
    
    args = parser.parse_args()
    
    import_csv_to_sqlite(args.csv_file, args.db)
