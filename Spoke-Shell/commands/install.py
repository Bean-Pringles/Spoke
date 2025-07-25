# commands/install.py

import os
import urllib.request
import json

def run(args):
    if not args:
        print("Usage: install <command1> [<command2> ...] | install all")
        return

    commands_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(commands_dir, exist_ok=True)
    repo_base_url = "https://raw.githubusercontent.com/Bean-Pringles/Spoke-Shell-Commands/main/commands/"

    # Handle "all" command
    if len(args) == 1 and args[0].lower() == "all":
        try:
            api_url = "https://api.github.com/repos/Bean-Pringles/Spoke-Shell-Commands/contents/commands"
            with urllib.request.urlopen(api_url) as response:
                data = json.loads(response.read().decode())
            
            commands = []
            for item in data:
                if item['name'].endswith('.py') and item['type'] == 'file':
                    command_name = item['name'][:-3]  # Remove .py extension
                    if command_name != 'install':  # Skip install command itself
                        commands.append(command_name)
            
            print(f"Found {len(commands)} commands to install...")
            args = commands
        except Exception as e:
            print(f"Failed to fetch command list: {e}")
            return

    for command_name in args:
        if not command_name.isidentifier():
            print(f"Invalid command name '{command_name}'. Skipping.")
            continue

        filename = f"{command_name}.py"
        download_url = repo_base_url + filename
        dest_path = os.path.join(commands_dir, filename)

        if os.path.isfile(dest_path):
            confirm = input(f"'{filename}' already exists. Overwrite? (Y/n): ").strip().lower()
            if confirm == 'n':
                print(f"Skipped '{command_name}'")
                continue

        try:
            print(f"Installing '{command_name}' from {download_url}...")
            urllib.request.urlretrieve(download_url, dest_path)
            print(f"Installing '{command_name}' to {filename}")
        except Exception as e:
            print(f"Failed to install '{command_name}': {e}")