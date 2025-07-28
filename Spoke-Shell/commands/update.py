import os
import urllib.request

def run(args):
    if not args or len(args) < 1:
        print("Usage: update commands|apps")
        return

    target = args[0].lower()

    # This script is inside commands/, so:
    commands_dir = os.path.abspath(os.path.dirname(__file__))  # commands folder (current folder)
    apps_dir = os.path.abspath(os.path.join(commands_dir, "..", "apps"))  # go up one, then apps

    if target == "commands":
        base_raw_url = "https://raw.githubusercontent.com/Bean-Pringles/Spoke/main/Spoke-Shell/commands/"

        if not os.path.exists(commands_dir):
            print(f"Commands directory does not exist: {commands_dir}")
            return

        for root, dirs, files in os.walk(commands_dir):
            for filename in files:
                local_file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(local_file_path, commands_dir).replace("\\", "/")
                remote_url = base_raw_url + relative_path

                print(f"Updating command {relative_path} ...")
                try:
                    with urllib.request.urlopen(remote_url) as response:
                        content = response.read()
                    with open(local_file_path, "wb") as f:
                        f.write(content)
                    print(f"Updated {relative_path} successfully.")
                except Exception as e:
                    print(f"Failed to update {relative_path}: {e}")

    elif target == "apps":
        base_raw_url = "https://raw.githubusercontent.com/Bean-Pringles/Spoke/main/Spoke-Shell/apps/"

        if not os.path.exists(apps_dir):
            print(f"Apps directory does not exist: {apps_dir}")
            return

        for appname in os.listdir(apps_dir):
            app_folder = os.path.join(apps_dir, appname)
            if not os.path.isdir(app_folder):
                continue

            app_file = os.path.join(app_folder, f"{appname}.py")
            if not os.path.isfile(app_file):
                print(f"Warning: Expected app file not found: {app_file}")
                continue

            relative_path = f"{appname}/{appname}.py"
            remote_url = base_raw_url + relative_path

            print(f"Updating app {relative_path} ...")
            try:
                with urllib.request.urlopen(remote_url) as response:
                    content = response.read()
                with open(app_file, "wb") as f:
                    f.write(content)
                print(f"Updated {relative_path} successfully.")
            except Exception as e:
                print(f"Failed to update {relative_path}: {e}")

    else:
        print(f"Unknown update target: {target}")
        print("Usage: update commands|apps")