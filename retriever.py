import os
import json
import subprocess

games_config_path = 'games.json'
routes_config_path = 'routes.json'

def get_route(game_name):
    try:
        with open(routes_config_path, 'r') as f:
            routes_config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("No routes found or routes.json is invalid.")
        return None

    return routes_config.get(game_name, None)

def clean_path(path):
    return path.strip().strip('"')

def update_routes_config(game_name, save_route):
    try:
        with open(routes_config_path, 'r') as f:
            routes_config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        routes_config = {}

    routes_config[game_name] = save_route

    with open(routes_config_path, 'w') as f:
        json.dump(routes_config, f, indent=4)

def update_games_config(game):
    try:
        with open(games_config_path, 'r') as f:
            games_config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        games_config = {"games": []}

    if game not in games_config["games"] and game != '':
        games_config["games"].append(game)

    with open(games_config_path, 'w') as f:
        json.dump(games_config, f, indent=4)
    print(f"Game '{game}' added to configuration and saved to {games_config_path}")

def delete_windows_task(game_name):
    task_name = f"BackupTool_{game_name}"
    command = f"schtasks /delete /tn \"{task_name}\" /f"
    subprocess.run(command, shell=True, check=True)
    print(f"Windows task '{task_name}' deleted")

def clear_old_task_if_exists(game_name):
    task_name = f"BackupTool_{game_name}"
    command = f"schtasks /query /tn \"{task_name}\""
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        delete_windows_task(game_name)

def remove_game_from_config(game):
    try:
        with open(games_config_path, 'r') as f:
            games_config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        games_config = {"games": []}

    if game in games_config["games"]:
        games_config["games"].remove(game)
        with open(games_config_path, 'w') as f:
            json.dump(games_config, f, indent=4)
        print(f"Game '{game}' removed from configuration and saved to {games_config_path}")
        delete_windows_task(game)
    else:
        print(f"Game '{game}' not found in configuration")

def add_game_to_config(new_game, save_route):
    clear_old_task_if_exists(new_game)
    update_routes_config(new_game, save_route)
    update_games_config(new_game)
    print(f"Game '{new_game}' with save route '{save_route}' added to configuration")

def delete_game_from_config(game_name):
    try:
        with open(games_config_path, 'r') as f:
            games_config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        games_config = {"games": []}

    if game_name in games_config["games"]:
        games_config["games"].remove(game_name)
        with open(games_config_path, 'w') as f:
            json.dump(games_config, f, indent=4)
        print(f"Game '{game_name}' removed from configuration")
    else:
        print(f"Game '{game_name}' not found in configuration")

    try:
        with open(routes_config_path, 'r') as f:
            routes_config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        routes_config = {}

    if game_name in routes_config:
        del routes_config[game_name]
        with open(routes_config_path, 'w') as f:
            json.dump(routes_config, f, indent=4)
        print(f"Route for '{game_name}' removed from configuration")
    else:
        print(f"Route for '{game_name}' not found in configuration")

def print_routes():
    try:
        with open(routes_config_path, 'r') as f:
            routes_config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("No routes found or routes.json is invalid.")
        return

    for game_name, save_route in routes_config.items():
        print(f"{game_name}: {save_route}")

def main():
    while True:
        print("Select an option:")
        print("1. Add a new game")
        print("2. Delete a game")
        print("3. Edit a game")
        print("4. List all games")
        print("5. Exit")
        choice = input("Enter your choice (1/2/3/4/5): ")

        if choice == '1':
            while True:
                game = input("Enter the name of game's .exe file to proceed: ")
                path = input(f"Enter full path to {game} save files: ")
                path = clean_path(path)
                if os.path.exists(path):
                    if game != '':
                        add_game_to_config(game, path)
                        break
                else:
                    print(f"Path '{path}' does not exist. Please enter a valid path.")
        elif choice == '2':
            print_routes()
            game = input("Enter the name of the game to delete: ")
            delete_game_from_config(game)
        elif choice == '3':
            print_routes()
            game = input("Enter the name of the game to edit: ")
            while True:
                microchoice = input("Enter 'name' to edit the game name or 'route' to edit the save location: ")
                if microchoice == 'name':
                    new_game_name = input("Enter the new name of the game: ")
                    route = get_route(game)
                    delete_game_from_config(game)
                    update_games_config(new_game_name)
                    update_routes_config(new_game_name, route)
                    break
                elif microchoice == 'route':
                    new_path = input(f"Enter the new full path to {game} save files: ")
                    new_path = clean_path(new_path)
                    if os.path.exists(new_path):
                        delete_game_from_config(game)
                        update_routes_config(game, new_path)
                        update_games_config(game)
                        break
                    else:
                        print(f"Path '{new_path}' does not exist. Please enter a valid path.")
                else:
                    print("Invalid choice. Please enter 'name' or 'route'.")
        elif choice == '4':
            try:
                print_routes()
            except:
                print('List exception occurred. Try recreating configuration files')
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()