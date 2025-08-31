import os

def run(args):
    if args:
        print("Usage: tree")
        return

    cwd = os.getcwd()
    print(f"{os.path.basename(cwd) or cwd}/")

    stack = [(cwd, "")]  # stack holds tuples of (path, prefix)

    while stack:
        path, prefix = stack.pop()
        try:
            items = sorted(os.listdir(path))
        except PermissionError:
            print(prefix + "└── [Permission Denied]")
            continue

        files = [f for f in items if os.path.isfile(os.path.join(path, f))]
        dirs = [d for d in items if os.path.isdir(os.path.join(path, d))]
        total = len(dirs) + len(files)

        # We'll process in reverse order to simulate recursion with stack (last in first out)
        entries = dirs + files
        for i in reversed(range(total)):
            name = entries[i]
            full_path = os.path.join(path, name)
            connector = "└── " if i == total - 1 else "├── "
            print(prefix + connector + name)

            if os.path.isdir(full_path):
                extension = "    " if i == total - 1 else "│   "
                # Push next directory with updated prefix for further processing
                stack.append((full_path, prefix + extension))
