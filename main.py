import sys
import getpass
from datetime import datetime, timedelta
import database
import auth
import utils

def initialize_app():
    database.init_db()
    user = database.get_user()
    if not user:
        print("--- App Initialization ---")
        while True:
            mp = getpass.getpass("Create a Master Password: ")
            valid, msg = auth.validate_master_password(mp)
            if not valid:
                print(f"Error: {msg}")
                continue
            confirm_mp = getpass.getpass("Confirm Master Password: ")
            if mp != confirm_mp:
                print("Passwords do not match.")
                continue
            database.create_user(auth.hash_password(mp))
            print("Master Password set successfully! Please restart the app.")
            sys.exit(0)

def login():
    user = database.get_user()
    if not user:
        return None
    
    user_id, mp_hash, attempts, lockout_until = user
    
    if auth.is_locked_out(lockout_until):
        remaining = auth.get_lockout_remaining(lockout_until)
        print(f"Account locked. Try again in {remaining} minutes.")
        sys.exit(0)
    
    attempts_left = 4 - attempts
    while attempts_left > 0:
        mp = getpass.getpass(f"Enter Master Password ({attempts_left} attempts left): ")
        if auth.hash_password(mp) == mp_hash:
            database.update_login_lockout(0, None)
            return True
        else:
            attempts += 1
            attempts_left = 4 - attempts
            if attempts >= 4:
                lockout_end = (datetime.now() + timedelta(hours=4)).isoformat()
                database.update_login_lockout(attempts, lockout_end)
                print("Too many failed attempts. Locked for 4 hours.")
                sys.exit(0)
            database.update_login_lockout(attempts, None)
            print("Incorrect password.")
    return False

def manage_sensitive_lock(vault_id, attempts, lockout_until, max_attempts=5, lockout_hours=2):
    if auth.is_locked_out(lockout_until):
        remaining = auth.get_lockout_remaining(lockout_until)
        print(f"This operation is locked for {remaining} minutes.")
        return False, attempts
    
    attempts_left = max_attempts - attempts
    mp = getpass.getpass(f"Confirm Master Password for sensitive operation ({attempts_left} attempts left): ")
    user = database.get_user()
    if auth.hash_password(mp) == user[1]:
        database.update_sensitive_lockout(vault_id, 0, None)
        return True, 0
    else:
        attempts += 1
        if attempts >= max_attempts:
            lockout_end = (datetime.now() + timedelta(hours=lockout_hours)).isoformat()
            database.update_sensitive_lockout(vault_id, attempts, lockout_end)
            print(f"Too many failed attempts. Locked for {lockout_hours} hours.")
        else:
            database.update_sensitive_lockout(vault_id, attempts, None)
            print("Incorrect password.")
        return False, attempts

def search_and_manage():
    url = input("Enter URL to search: ").strip()
    rows = database.get_passwords_by_url(url)
    
    if rows:
        print(f"Found {len(rows)} instance(s) for {url}.")
        choice = input("View email and passwords? (y/n): ").lower()
        if choice == 'y':
            # For simplicity, we check master password once for the set of results
            # But the requirement says "if URL(s) is there... ask for master password"
            # We'll use the lockout logic for the first item as a proxy or just create a general sensitive lock
            # The requirement implies localized lockout per URL entry? "Here, they have 5 attempts before they are locked out for 2 hours"
            # Let's apply it to each row individually if they want to view specific ones, or to the search result.
            # I'll implement it as: if they want to view ANY from this URL, they must pass the check.
            # I will use vault_id=0 as a "global" or just pick the first vault_id to track lockout for this URL.
            # Actually, let's track lockout per vault entry.
            
            authorized = False
            for row in rows:
                vid, email, pwd, s_attempts, s_lock = row
                success, _ = manage_sensitive_lock(vid, s_attempts, s_lock)
                if success:
                    authorized = True
                    break # One success lets them view all for this URL (common sense)
                else:
                    return # Locked or failed
            
            if authorized:
                content = []
                for row in rows:
                    content.append(f"Email: {row[1]}")
                    content.append(f"Password: {row[2]}")
                    content.append("-" * 20)
                utils.print_box(f"Passwords for {url}", content[:-1])
    else:
        print(f"No URL(s) matching '{url}' found.")
        choice = input("Create a new password triplet? (y/n): ").lower()
        if choice == 'y':
            add_new_password(url)

def add_new_password(prefilled_url=None):
    url = prefilled_url if prefilled_url else input("URL: ").strip()
    email = input("Email: ").strip()
    pwd = input("Password: ").strip()
    database.add_password(url, email, pwd)
    print("Password stored successfully.")

def update_password_flow():
    url = input("Enter URL to update: ").strip()
    rows = database.get_passwords_by_url(url)
    if not rows:
        print("URL not found.")
        return
    
    # Selection if multiple
    for i, row in enumerate(rows):
        print(f"{i+1}. {row[1]}")
    idx = int(input("Select entry to update (number): ")) - 1
    vid, old_email, old_pwd, s_attempts, s_lock = rows[idx]
    
    success, _ = manage_sensitive_lock(vid, s_attempts, s_lock)
    if success:
        new_email = input(f"New Email (current: {old_email}): ") or old_email
        new_pwd = input(f"New Password (current: {old_pwd}): ") or old_pwd
        database.update_password(vid, new_email, new_pwd)
        print("Updated successfully.")

def delete_password_flow():
    url = input("Enter URL to delete: ").strip()
    rows = database.get_passwords_by_url(url)
    if not rows:
        print("URL not found.")
        return
    
    for i, row in enumerate(rows):
        print(f"{i+1}. {row[1]}")
    idx = int(input("Select entry to delete (number): ")) - 1
    vid, email, pwd, s_attempts, s_lock = rows[idx]
    
    confirm = input("Are you sure? (y/n): ").lower()
    if confirm == 'y':
        success, _ = manage_sensitive_lock(vid, s_attempts, s_lock)
        if success:
            database.delete_password(vid)
            print("Deleted successfully.")

def main():
    utils.clear_screen()
    initialize_app()
    if login():
        print("\nWelcome to WinPWMG!")
        while True:
            print("\n--- Main Menu ---")
            print("1. Search/Add Password")
            print("2. Update Password")
            print("3. Delete Password")
            print("4. Exit")
            choice = input("Choice: ")
            
            if choice == '1':
                search_and_manage()
            elif choice == '2':
                update_password_flow()
            elif choice == '3':
                delete_password_flow()
            elif choice == '4':
                print("Goodbye!")
                break
            else:
                print("Invalid choice.")

if __name__ == "__main__":
    main()
