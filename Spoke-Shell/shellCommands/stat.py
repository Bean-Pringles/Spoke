import os
import time

def run(args):
    if not args:
        print("Usage: stat <filename>")
        return

    path = args[0]

    if not os.path.exists(path):
        print(f"stat: cannot stat '{path}': No such file")
        return

    stat = os.stat(path)

    print(f"File: {os.path.basename(path)}")
    print(f"Size: {stat.st_size} bytes")
    print(f"Created: {time.ctime(stat.st_ctime)}")
    print(f"Modified: {time.ctime(stat.st_mtime)}")
    print(f"Accessed: {time.ctime(stat.st_atime)}")
    print(f"Absolute Path: {os.path.abspath(path)}")
