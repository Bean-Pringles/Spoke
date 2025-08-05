import os
import importlib
import subprocess

# Get the current user's home folder and change to it
home_dir = os.path.expanduser("~")
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

            # Read prompt letter from the first line of configs.txt
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
                # Try to import and run the command module
                module = importlib.import_module(f"commands.{cmd}")
                importlib.reload(module)
                if hasattr(module, 'run'):
                    module.run(args)
                else:
                    print(f"{cmd}: command module has no 'run' function")

            except ModuleNotFoundError:
                # Check configs.txt for a shortcut
                replacement = get_shortcut_replacement(cmd)
                if replacement:
                    new_command_input = replacement + " " + " ".join(args)
                    print(f"{cmd}: shortcut found, running -> {new_command_input}")
                    parts = new_command_input.strip().split()
                    cmd = parts[0]
                    args = parts[1:]
                    try:
                        module = importlib.import_module(f"commands.{cmd}")
                        importlib.reload(module)
                        if hasattr(module, 'run'):
                            module.run(args)
                        else:
                            print(f"{cmd}: command module has no 'run' function")
                    except ModuleNotFoundError:
                        print(f"{cmd}: command not found")
                else:
                    # Fallback: run through OS shell and print output
                    try:
                        result = subprocess.check_output(command_input, shell=True, stderr=subprocess.STDOUT, text=True)
                        print(result)
                    except subprocess.CalledProcessError as e:
                        print("Error:", e.output)

        except KeyboardInterrupt:
            print("\nUse 'exit' to quit.")
        except EOFError:
            print("\nExiting.")
            break

if __name__ == "__main__":
    shell_loop()
