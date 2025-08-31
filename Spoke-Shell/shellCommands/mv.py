import os 

def run(args):
    if not args:
        print("Usage: mv <file1> <file2>")
        return
    
    file1 = args[0]
    file2 = args[1]

    try:
        os.rename(file1, file2)
    except Exception as e:
        print(f"An error occured: {e}")