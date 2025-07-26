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

    # Correct raw base URL
    repo_base_url = "https://raw.githubusercontent.com/Bean-Pringles/Spoke/main/Spoke-Shell/commands/"

    #Install all available commands from GitHub
    if len(args) == 1 and args[0].lower() == "all":
        try:
            # Correct GitHub API URL for file listing
            api_url = "https://api.github.com/repos/Bean-Pringles/Spoke/contents/Spoke-Shell/commands"
            req = urllib.request.Request(api_url, headers={"User-Agent": "Spoke-Installer"})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())

            commands = []
            for item in data:
                if item['name'].endswith('.py') and item['type'] == 'file':
                    command_name = item['name'][:-3]  # Remove .py
                    if command_name != 'install':
                        commands.append(command_name)

            if not commands:
                print("No commands found.")
                return

            print(f"Found {len(commands)} commands to install: {', '.join(commands)}")
            args = commands
        except Exception as e:
            print(f"Failed to fetch command list: {e}")
            return

    #Install each requested command
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
            print(f"Installed '{command_name}' to '{filename}'")
        except Exception as e:
            print(f"Failed to install '{command_name}': {e}")
