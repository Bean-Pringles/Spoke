import os 

def run(args):
    if not args:
        print("Usage: head <file>")
        return

    file_path = args[0] 
    
    if len(args) == 2:
        n = int(args[1])
    else:
        n = 10
                
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()  
            for line in lines[:n]: 
                print(line.strip()) 
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
