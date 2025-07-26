import os

def run(args):
    if not args:
        print("Usage: rmdir <dir_name>")
        return
    
    dir_name = args[0]

    try:
        os.rmdir(dir_name)
    except FileNotFoundError:
        print(f"File '{dir_name}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
