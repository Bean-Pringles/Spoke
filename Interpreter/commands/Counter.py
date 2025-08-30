import os

def list_commands():
    # Get all files in current folder
    files = os.listdir(".")
    
    # Filter only .py files
    py_files = [f for f in files if f.endswith(".py")]
    
    cleaned = []
    for f in py_files:
        name = f
        if name.startswith("cmd_"):
            name = name[len("cmd_"):]  # remove prefix
        if name.endswith(".py"):
            name = name[:-3]  # remove .py
        cleaned.append(name)

    # Print nicely
    print("Available commands:\n")
    for c in sorted(cleaned):
        print(f" - {c}")

if __name__ == "__main__":
    list_commands()