import os
import subprocess
import sys

def run(args):
    if not args:
        print("Usage: txted <filename.spk | folder>")
        return

    # Step 1: Get path to textEditor.py (assumed one level up)
    current_dir = os.path.dirname(os.path.abspath(__file__))  # .../commands/
    parent_dir = os.path.dirname(current_dir)                 # .../

    editor_path = os.path.join(parent_dir, "textEditor.py")
    if not os.path.isfile(editor_path):
        print("Error: textEditor.py not found in parent directory.")
        return

    # Step 2: Get the target path (file or folder)
    target_path = args[0]
    full_target_path = os.path.abspath(target_path)

    if not os.path.exists(full_target_path):
        print(f"Error: '{target_path}' does not exist.")
        return

    # Step 3: Launch editor with target (file or folder)
    try:
        subprocess.Popen([sys.executable, editor_path, full_target_path])
    except Exception as e:
        print(f"Failed to launch editor: {e}")
