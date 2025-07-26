import os 

def run(args):
    if not args:
        print("Usage: head <file>")
        return

    file_path = args[0]  

    try:
        with open(file_path, "r") as file:
            lines = file.readlines()  
            for line in lines[:10]: 
                print(line.strip()) 
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
