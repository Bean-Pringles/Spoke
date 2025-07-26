import os

def run(args):
    if not args:
        print("Usage: rm <file_name>")
        return
    
    file_name = args[0]

    try:
        os.remove(file_name)
    except FileNotFoundError:
        print(f"File '{file_name}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
