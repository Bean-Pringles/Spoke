import os

def run(args):
    if not args:
        print("Usage: skin <new_skin>")
        return

    new_line = args[0]

    # Get the directory above the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    file_path = os.path.join(parent_dir, "configs.txt")

    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        if lines:
            lines[0] = new_line.rstrip('\n') + '\n'
        else:
            lines = [new_line + '\n']

        with open(file_path, 'w') as file:
            file.writelines(lines)

    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
