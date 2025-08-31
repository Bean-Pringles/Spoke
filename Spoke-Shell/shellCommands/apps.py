import os
import urllib.request
import json
import subprocess
import sys

def run(args):
    if not args:
        print("Usage: app <command> <app>")
        return
    
    action = args[0]
    
    if action == "install":
        if len(args) < 2:
            print("Usage: app install <command> [command ...] | app install all")
            return
        
        # Assign install_args here before usage
        install_args = args[1:]
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        commands_dir = os.path.join(parent_dir, "apps")
        os.makedirs(commands_dir, exist_ok=True)
    
        repo_base_url = "https://raw.githubusercontent.com/Bean-Pringles/Spoke/main/Spoke-Shell/apps/"
        
        if len(install_args) == 1 and install_args[0].lower() == "all":
            try:
                api_url = "https://api.github.com/repos/Bean-Pringles/Spoke/contents/Spoke-Shell/apps"
                req = urllib.request.Request(api_url, headers={"User-Agent": "Spoke-Installer"})
                with urllib.request.urlopen(req) as response:
                    data = json.loads(response.read().decode())

                commands = []
                for item in data:
                    if item['name'].endswith('.py') and item['type'] == 'file':
                        command_name = item['name'][:-3]
                        if command_name != 'install':
                            commands.append(command_name)

                if not commands:
                    print("No commands found.")
                    return
                print(f"Found {len(commands)} commands to install: {', '.join(commands)}")
                install_args = commands
            except Exception as e:
                print(f"Failed to fetch command list: {e}")
                return

        for command_name in install_args:
            if not command_name.isidentifier():
                print(f"Invalid command name '{command_name}'. Skipping.")
                continue

            filename = f"{command_name}.py"
            download_url = repo_base_url + command_name + "/" + filename 
            dest_path = os.path.join(commands_dir, filename)

            if os.path.isfile(dest_path):
                confirm = input(f"'{filename}' already exists. Overwrite? (Y/n): ").strip().lower()
                if confirm == 'n':
                    print(f"Skipped '{command_name}'")
                    continue

            try:
                print(f"Installing '{command_name}' from {download_url}...")
                urllib.request.urlretrieve(download_url, dest_path)
                print(f"Installed '{command_name}' to '{dest_path}'")
                
                with open(dest_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                apt_commands = []
                for line in content.split('\n'):
                    stripped_line = line.strip()
                    if 'apt install' in stripped_line:
                        if stripped_line.startswith('#'):
                            cmd = stripped_line.lstrip('#').strip()
                        else:
                            cmd = stripped_line
                        
                        if cmd.startswith('apt install'):
                            apt_commands.append(cmd)
                
                if apt_commands:
                    print(f"Found apt install commands in {filename}")
                    for cmd in apt_commands:
                        try:
                            cmd_parts = cmd.split()
                            if cmd_parts[0] != 'sudo':
                                cmd_parts.insert(0, 'sudo')
                            subprocess.run(cmd_parts, check=True)
                            print(f"Executed: {' '.join(cmd_parts)}")
                        except subprocess.CalledProcessError:
                            print(f"Failed to execute: {cmd}")
                            
            except Exception as e:
                print(f"Failed to install '{command_name}': {e}")

    if action == "run":
        if len(args) < 2:
            print("Usage: app run <appname>")
            return

        app_name = args[1]
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        apps_dir = os.path.join(parent_dir, "apps")
        app_dir = os.path.join(apps_dir, app_name)
        app_path = os.path.join(app_dir, f"{app_name}.py")

        if not os.path.isfile(app_path):
            print(f"App '{app_name}' not found at {app_path}")
            return

        # Detect app's virtual environment
        if os.name == 'nt':
            venv_python = os.path.join(app_dir, "venv", "Scripts", "python.exe")
        else:
            venv_python = os.path.join(app_dir, "venv", "bin", "python")

        python_exe = venv_python if os.path.isfile(venv_python) else sys.executable

        try:
            print(f"Launched app '{app_name}' using: {python_exe}")
            subprocess.run([python_exe, app_path], cwd=app_dir)
        except Exception as e:
            print(f"Failed to launch app '{app_name}': {e}")

    elif action == "list":
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        apps_dir = os.path.join(parent_dir, "apps")

        if not os.path.isdir(apps_dir):
            print(f"No 'apps' directory found at {apps_dir}")
            return

        app_folders = [name for name in os.listdir(apps_dir)
                    if os.path.isdir(os.path.join(apps_dir, name))]

        if not app_folders:
            print("No apps found.")
        else:
            print("Available apps:")
            for app in app_folders:
                print(f"  - {app}")
            print("Run command: app run <app name>")

