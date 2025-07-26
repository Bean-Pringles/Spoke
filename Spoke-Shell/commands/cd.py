# commands/cd.py
import os

def run(args):
    if len(args) == 0 or args[0] == "~":
        os.chdir(os.path.expanduser("~"))
    else:
        try:
            os.chdir(args[0])
        except Exception as e:
            print(f"cd: {e}")
