import os

def run(args):
    if not args:
        print("Usage: file <exampleFile.py>")
        return
    
    file = args[0]
    
    _, extension = os.path.splitext(file)
    print("Extension: " + extension)  # Output: .txt