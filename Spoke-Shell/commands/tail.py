import os
from collections import deque

def run(args):
    if not args:
        print("Usage: tail <file> [n]")
        return

    file = args[0]
    if len(args) == 2:
        n = int(args[1])
    else:
        n = 10

    if not os.path.isfile(file):
        print(f"File not found: {file}")
        return

    try:
        with open(file, "r") as f:
            lines = deque(f, maxlen=n)
            for line in lines:
                print(line.rstrip())  # Avoid double newlines
    except Exception as e:
        print(f"Error reading file: {e}")
