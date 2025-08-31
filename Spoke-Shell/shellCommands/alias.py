import os

def run(args):
    if len(args) < 2:
        print("Usage: alias <name> <command>")
        return

    shortcut = args[0]
    command = " ".join(args[1:])

    # Get parent directory of this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)

    # Path to shortcuts.txt in the shell's root
    file_path = os.path.join(parent_dir, "configs.txt")

    try:
        with open(file_path, "a") as f:
            f.write(f"{shortcut} = {command}\n")
    except Exception as e:
        print(f"Error writing alias: {e}")
