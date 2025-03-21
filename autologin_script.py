import db.CredentialManager as CredManager
import module

def main():
    credential_manager = CredManager.CredentialManger()
    
    while True:
        print("\n1. Add new login credentials")
        print("2. Start auto-login process")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == "1":
            credential_manager.add_credential()
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
                
                retry, cred_index = module.login(credential_manager.get_credentials())
                if not retry:
                    break
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
