import os
import importlib

# Get the current user's home folder
home_dir = os.path.expanduser("~")

# Change to that directory
os.chdir(home_dir)

def shell_loop():
    while True:
        try:
            path = os.getcwd()
            command_input = input(f"{path} $ ").strip()

            if not command_input:
                continue
            if command_input == "exit":
                break

            parts = command_input.split()
            cmd = parts[0]
            args = parts[1:]

            try:
                # Dynamically import the command module
                module = importlib.import_module(f"commands.{cmd}")
                importlib.reload(module)
                # Call the run function
                if hasattr(module, 'run'):
                    module.run(args)
                else:
                    print(f"{cmd}: command module has no 'run' function")
            except ModuleNotFoundError:
                print(f"{cmd}: command not found")

        except KeyboardInterrupt:
            print("\nUse 'exit' to quit.")
        except EOFError:
            print("\nExiting.")
            break

if __name__ == "__main__":
    shell_loop()
