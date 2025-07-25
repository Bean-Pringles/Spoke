import os 

def run(args):
    if not args:
        print("Usage: mkdir <dir_name>")
        return
    
    dirName = args[0]

    try:
        os.mkdir(dirName)
    except FileExistsError:
        print("File already exists")
    except Exception as e:
        print(f"An error occured: {e}")