# commands/ls.py

import os

def run(args):
    # Get target directory (default is current)
    target = args[0] if args else "."

    # Normalize path (like expanding "~" or "." or "..")
    target = os.path.expanduser(target)

    if not os.path.isdir(target):
        print(f"ls: cannot access '{target}': No such directory")
        return

    # List all files and dirs
    for item in os.listdir(target):
        print(item)
