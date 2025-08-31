import os
import importlib

# Get the current user's home folder
home_dir = os.path.expanduser("~")

# Change to that directory
os.chdir(home_dir)

def get_shortcut_replacement(cmd):
    """
    Looks for a shortcut match in configs.txt and returns the full replacement command line.
    If not found, returns None.
    """
    shell_dir = os.path.dirname(os.path.abspath(__file__))
    shortcut_path = os.path.join(shell_dir, "configs.txt")

    if not os.path.isfile(shortcut_path):
        return None

    with open(shortcut_path, "r") as f:
        for line in f:
            if '=' not in line:
                continue
            key, value = line.split('=', 1)
            if key.strip() == cmd:
                return value.strip()
    return None

def shell_loop():
    while True:
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(script_dir, "configs.txt")

            with open(file_path, "r") as file:
                first_line = file.readline()
                letter = first_line.strip()
            
            path = os.getcwd()
            command_input = input(f"{path} {letter} ").strip()

            if not command_input:
                continue
            if command_input == "exit":
                break

            parts = command_input.split()
            cmd = parts[0]
            args = parts[1:]

            try:
                # Try to import and run the command module from shellCommands
                module = importlib.import_module(f"shellCommands.{cmd}")
                importlib.reload(module)
                if hasattr(module, 'run'):
                    module.run(args)
                else:
                    print(f"{cmd}: command module has no 'run' function")

            except ModuleNotFoundError:
                # Check configs.txt
                replacement = get_shortcut_replacement(cmd)
                if replacement:
                    # Rebuild the new command line with original args appended
                    new_command_input = replacement + " " + " ".join(args)
                    # Recursively re-run with the new command line
                    print(f"{cmd}: shortcut found, running -> {new_command_input}")
                    # Simulate entering the new command in the shell
                    parts = new_command_input.strip().split()
                    cmd = parts[0]
                    args = parts[1:]
                    try:
                        module = importlib.import_module(f"shellCommands.{cmd}")
                        importlib.reload(module)
                        if hasattr(module, 'run'):
                            module.run(args)
                        else:
                            print(f"{cmd}: command module has no 'run' function")
                    except ModuleNotFoundError:
                        print(f"{cmd}: command not found")
                else:
                    print(f"{cmd}: command not found")

        except KeyboardInterrupt:
            print("\nUse 'exit' to quit.")
        except EOFError:
            print("\nExiting.")
            break

if __name__ == "__main__":
    shell_loop()