import os

def run(args):
    if not args:
        print("Usage: uninstall <command1> [<command2> ...]")
        return

    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    for command in args:
        filename = os.path.join(script_dir, f"{command}.py")
        
        if os.path.exists(filename):
            confirm = input(f"Are you sure you want to uninstall '{command}'? (Y/n): ").strip().lower()
            if confirm == 'n':
                print(f"Skipped '{command}'.")
            else:
                os.remove(filename)
                print(f"Uninstalled '{command}'.")
        else:
            print(f"Command '{command}' not found.")