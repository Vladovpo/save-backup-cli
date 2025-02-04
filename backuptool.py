import os
import json
import shutil
import sys
import time
import psutil
from win32com.client import Dispatch

# Shortcut workings
def create_shortcut(destination_path):
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    exe_path = os.path.join(script_dir, "backuptool.exe")
    shortcut_path = os.path.join(destination_path, "BackupTool.lnk")
    
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortcut(shortcut_path)
    shortcut.TargetPath = exe_path
    shortcut.WorkingDirectory = script_dir
    shortcut.WindowStyle = 7  # Start minimized
    shortcut.Save()
    
    print(f"Shortcut created at: {shortcut_path}")

def get_startup_path():
    return os.path.join(os.getenv('APPDATA'), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")

def is_shortcut_created(destination_path):
    shortcut_path = os.path.join(destination_path, "BackupTool.lnk")
    return os.path.exists(shortcut_path)


# Load configuration files
def load_config(file_path):
    if not os.path.exists(file_path):
        print(f"Missing configuration file: {file_path}. Please run the main script to configure the app.")
        exit(1)
    with open(file_path, 'r') as f:
        return json.load(f)

routes_config = load_config('routes.json')
games_config = load_config('games.json')
app_config = load_config('app.json')

# List of games (process names without ".exe")
games_to_watch = games_config.get("games", [])

# Function to copy saves to backup folder
def backup_saves(game_name, save_route):
    try:
        if app_config.get('use_custom_path'):
            backup_folder = os.path.join(app_config['custom_path'], game_name)
        else:
            backup_folder = os.path.join("backup", game_name)
        
        os.makedirs(backup_folder, exist_ok=True)
        for root, dirs, files in os.walk(save_route):
            for file_name in files:
                full_file_name = os.path.join(root, file_name)
                relative_path = os.path.relpath(full_file_name, save_route)
                backup_file_path = os.path.join(backup_folder, relative_path)
                os.makedirs(os.path.dirname(backup_file_path), exist_ok=True)
                shutil.copy(full_file_name, backup_file_path)
        print(f"Saves for '{game_name}' backed up to '{backup_folder}'")
    except Exception as e:
        print(f"Failed to backup saves for '{game_name}': {e}")

# Monitor processes
def monitor_games():
    print('Starting automon tool')
    try:
        # Initial check for running games
        active_processes = [p.name() for p in psutil.process_iter()]
        monitored_running = [game for game in games_to_watch if f"{game}.exe" in active_processes]

        if monitored_running:
            print(f"Warning: The following monitored games are already running: {', '.join(monitored_running)}")

        while True:
            active_processes = [p.name() for p in psutil.process_iter()]
            monitored_running = [game for game in games_to_watch if f"{game}.exe" in active_processes]
            
            # If monitored games are running, wait for them to stop
            if monitored_running:
                print(f"Monitoring: {', '.join(monitored_running)}")
                while any(f"{game}.exe" in [p.name() for p in psutil.process_iter()] for game in monitored_running):
                    time.sleep(5)  # Check every 5 seconds

                print("Game closed. Waiting for final saves...")
                time.sleep(10)  # Wait for 10 seconds to ensure the game has saved

                print("Running backup...")
                for game in monitored_running:
                    backup_saves(game, routes_config[game])

            time.sleep(5)  # Re-check every 5 seconds if no monitored game is running
    except Exception as e:
        print(f"Error in monitoring games: {e}")

#Shortcut maintenance
def ensure_shortcut():
    startup_path = get_startup_path()
    if not is_shortcut_created(startup_path):
        print('Creating shortcut')
        create_shortcut(startup_path)
    else:
        print('Shortcut already exists')
    if is_shortcut_created(startup_path):
        print(f'Shortcut was created successfully at {startup_path}')

if __name__ == "__main__":
    ensure_shortcut()
    print('Shortcut exists')
    monitor_games()