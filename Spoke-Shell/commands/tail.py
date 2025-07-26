import os
from collections import deque

def run(args):
    if not args:
        print("Usage: tail <file> [n]")
        return

    file = args[0]
    num_lines = int(args[1]) if len(args) > 1 and args[1].isdigit() else 10

    if not os.path.isfile(file):
        print(f"File not found: {file}")
        return

    try:
        with open(file, "r") as f:
            lines = deque(f, maxlen=num_lines)
            for line in lines:
                print(line.rstrip())  # Avoid double newlines
    except Exception as e:
        print(f"Error reading file: {e}")
