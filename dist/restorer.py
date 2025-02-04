import os
import json
import shutil

# Load configuration files
def load_config(file_path):
    if not os.path.exists(file_path):
        print(f"Missing configuration file: {file_path}. Please run the main script to configure the app.")
        exit(1)
    with open(file_path, 'r') as f:
        return json.load(f)

routes_config = load_config('routes.json')
app_config = load_config('app.json')

def clean_path(path):
    return path.strip().strip('"')

def restore_saves(game_name, restore_path):
    try:
        if app_config.get('use_custom_path'):
            backup_folder = os.path.join(app_config['custom_path'], game_name)
        else:
            backup_folder = os.path.join("backup", game_name)
        
        if not os.path.exists(backup_folder):
            print(f"No backup found for '{game_name}'")
            return

        first_upper_directory = os.path.basename(os.path.normpath(routes_config[game_name]))
        if os.path.basename(os.path.normpath(restore_path)) == first_upper_directory:
            target_restore_path = restore_path
        else:
            target_restore_path = os.path.join(restore_path, first_upper_directory)
            os.makedirs(target_restore_path, exist_ok=True)

        for root, dirs, files in os.walk(backup_folder):
            for file_name in files:
                full_file_name = os.path.join(root, file_name)
                relative_path = os.path.relpath(full_file_name, backup_folder)
                restore_file_path = os.path.join(target_restore_path, relative_path)
                os.makedirs(os.path.dirname(restore_file_path), exist_ok=True)
                shutil.copy(full_file_name, restore_file_path)
        print(f"Saves for '{game_name}' restored to '{target_restore_path}'")
    except Exception as e:
        print(f"Failed to restore saves for '{game_name}': {e}")

def main():
    while True:
        print("Select an option:")
        print("1. Restore using saved path")
        print("2. Restore using custom path")
        print("3. Exit")
        choice = input("Enter your choice (1/2/3): ")

        if choice == '1':
            game_name = input("Enter the game name: ")
            if game_name in routes_config:
                restore_saves(game_name, routes_config[game_name])
            else:
                print(f"No saved path found for '{game_name}'")
        elif choice == '2':
            game_name = input("Enter the game name: ")
            custom_restore_path = input("Enter the custom restore path: ").strip()
            custom_restore_path = clean_path(custom_restore_path)
            restore_saves(game_name, custom_restore_path)
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()