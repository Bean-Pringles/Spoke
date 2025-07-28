import os

def run(args):
    if not args:
        print("Usage: du <path>")
        return

    path = args[0]

    try:
        if os.path.isfile(path):
            size = os.path.getsize(path)
        elif os.path.isdir(path):
            size = 0
            for root, dirs, files in os.walk(path):
                for f in files:
                    fp = os.path.join(root, f)
                    try:
                        size += os.path.getsize(fp)
                    except OSError:
                        pass  # skip unreadable files
        else:
            print("Path is neither a file nor a directory.")
            return

        print(f"Bytes: {size}")
    except FileNotFoundError:
        print("File not found")
    except OSError as e:
        print(f"An error occurred: {e}")
