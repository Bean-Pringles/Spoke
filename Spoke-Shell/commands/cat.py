import os

def run(args):
    if not args:
        print("Usage: cat <exampleFile.txt>")
        return

    file = args[0]
    
    with open(file, 'r') as file:
        contents = file.read()

    # Print the contents
    print(contents)