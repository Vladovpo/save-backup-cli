import os
import json
import subprocess

config_path = 'app.json'
version = "1.0.1"

def load_config():
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)

def clean_path(path):
    return path.strip().strip('"')

def configure_backup():
    config = load_config()
    
    while True:
        use_custom_path = input("Do you want to use a custom path for backups? (yes/no): ").strip().lower()
        if use_custom_path in ['yes', 'y']:
            config['use_custom_path'] = True
            while True:
                custom_path = input("Enter the custom backup path: ").strip()
                custom_path = clean_path(custom_path)
                if not os.path.exists(custom_path):
                    print(f"The path '{custom_path}' does not exist. Please enter a valid path.")
                    continue
                backup_folder_name = "backup"
                full_path = os.path.join(custom_path, backup_folder_name)
                confirm = input(f"Is this path correct for backups? {full_path} (yes/no): ").strip().lower()
                if confirm in ['yes', 'y']:
                    config['custom_path'] = full_path
                    os.makedirs(full_path, exist_ok=True)  # Create the backup folder if it doesn't exist
                    break
                else:
                    print("Please enter the correct path.")
            break
        elif use_custom_path in ['no', 'n']:
            config['use_custom_path'] = False
            config['custom_path'] = None
            break
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

    save_config(config)
    print("Configuration saved.")

def check_and_configure():
    config = load_config()
    if not config:
        print("Configuration is missing or incomplete. Starting configuration...")
        configure_backup()

def run_retriever():
    subprocess.run(["python", "retriever.py"])

def run_restoretool():
    subprocess.run(["python", "restorer.py"])

def main():
    check_and_configure()
    while True:
        print("Select an option:")
        print("1. Manage configurations")
        print("2. Restore game's save")
        print("3. Configure backup settings")
        print("4. Exit")
        choice = input("Enter your choice (1/2/3/4): ")

        if choice == '1':
            run_retriever()
        elif choice == '2':
            run_restoretool()
        elif choice == '3':
            configure_backup()
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    print(f'App version: {version}')
    main()