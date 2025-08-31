# commands/cd.py
import os

def run(args):
    if len(args) == 0:
        path = os.path.expanduser("~")
    else:
        path = os.path.expanduser(args[0])  # Expand ~ to home directory
    
    try:
        os.chdir(path)
    except Exception as e:
        print(f"cd: {e}")