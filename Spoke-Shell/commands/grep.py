import os
import sys
import re

def run(args):
    if not args:
        print("Usage: grep <pattern> <filename (optional)>")
        return

    # Step 1: Parse arguments properly
    ignore_case = False
    pattern = None
    file_path = None
    
    # Handle flags and arguments
    i = 0
    while i < len(args):
        if args[i] == '-i':
            ignore_case = True
        elif pattern is None:
            pattern = args[i]
        elif file_path is None:
            file_path = args[i]
        i += 1
    
    if pattern is None:
        print("Usage: grep [-i] <pattern> <filename (optional)>")
        return

    # Step 2: Set regex flags
    flags = re.IGNORECASE if ignore_case else 0

    # Step 3: Function to search the file or stdin
    def search_file(file_path):
        if file_path:
            # Search in the specified file
            full_file_path = os.path.abspath(file_path)

            if not os.path.exists(full_file_path):
                print(f"Error: '{file_path}' does not exist.")
                return

            try:
                with open(full_file_path, 'r') as file:
                    for line in file:
                        if re.search(pattern, line, flags):
                            print(line, end='')
            except Exception as e:
                print(f"Error reading file: {e}")
        else:
            # Search from stdin if no file path is provided
            print("Searching stdin... (Ctrl-D to end input)")
            try:
                for line in sys.stdin:
                    if re.search(pattern, line, flags):
                        print(line, end='')
            except KeyboardInterrupt:
                print("\nSearch interrupted.")

    # Step 4: Perform the search
    search_file(file_path)