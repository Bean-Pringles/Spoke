import os

def run(args):
    command_dir = os.path.dirname(os.path.abspath(__file__))

    files = os.listdir(command_dir)
    py_files = [
        f for f in files
        if f.endswith(".py") and f != "__init__.py"
    ]

    command_names = [os.path.splitext(f)[0] for f in py_files]

    if command_names:
        print("Available commands:")
        for name in sorted(command_names):
            print(" -", name)
        print("Run a command without arguements to see what it does")
    else:
        print("No command files found.")
