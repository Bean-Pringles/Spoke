import os 
import shutil

def run(args):
    if not args:
        print("Usage: cp <origin_file> <destanation>")
        return
    
    source = args[0]
    destanation = args[1]

    try:
        shutil.copyfile(source, destanation)
    except Exception as e:
        print(f"An Error Occured: {e}")