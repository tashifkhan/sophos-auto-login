import db.CredentialManager as CredManager
import module
import atexit
import signal
import os

def main():
    credential_manager = CredManager.CredentialManger()
    cred_index = 0
    credentials = credential_manager.get_credentials()
    runing = True
    
    while runing:
        signal.signal ( signal.SIGINT, 
                        lambda sig, frame: 
                            module.exit_handler(cred_index, credentials, sig, frame)
                      )
        print("\n1. Add new login credentials")
        print("2. Start auto-login process")
        print("3. Edit existing credentials")
        print("4. Export credentials to CSV")
        print("5. Import credentials from CSV")
        print("6. Exit")
        
        choice = input("Enter your choice (1-6): ")
        
        if choice == "1":
            credential_manager.add_credential()
            credentials = credential_manager.get_credentials()
        elif choice == "2":
            count = 0
            cred_index = 0
            while True:
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
                
                stop, cred_index = module.login(credential_manager.get_credentials())
                if stop:
                    if len(credentials) == 0:
                        print("No credentials found.")
                    else:
                        module.logout(credential_manager.get_credentials()[cred_index])
                    break
        elif choice == "3":
            credential_manager.edit_credentials()
            credentials = credential_manager.get_credentials()
            
        elif choice == "4":
            output_path = input("Enter export path (leave empty for default): ")
            if output_path.strip():
                credential_manager.export_to_csv(output_path)
            else:
                credential_manager.export_to_csv()
        elif choice == "5":
            csv_path = input("Enter CSV file path: ")
            if os.path.exists(csv_path):
                credential_manager.import_from_csv(csv_path)
                credentials = credential_manager.get_credentials()
            else:
                print(f"File not found: {csv_path}")
        elif choice == "6":
            print("Exiting...")
            creds = credential_manager.get_credentials()
            if cred_index is None or not (0 <= cred_index < len(creds)):
                print("Invalid or unspecified credential index, logging out all credentials")
                for cred in creds:
                    module.logout(cred)
            else:
                module.logout(creds[cred_index])
            break
        else:
            print("Invalid choice. Please try again.")
            if cred_index:
                module.logout(credential_manager.get_credentials()[cred_index])

    if not runing:
        print("Exiting...")
        module.exit_handler(cred_index, credentials)
    
    atexit.register(lambda: module.exit_handler(cred_index, credentials))

if __name__ == "__main__":
    main()
