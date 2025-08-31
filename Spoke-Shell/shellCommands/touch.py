import os

def run(args):
    if not args:
        print("Usage: touch <file_name>")
        return
    
    fileName = args[0]

    try:
        with open(fileName, "x") as file:
            file.write("")
    except FileExistsError:
        print("File already exists")
    except Exception as e:
        print(f"An error occured: {e}")

    