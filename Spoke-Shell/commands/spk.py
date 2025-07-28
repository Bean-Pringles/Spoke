# commands/spk.py
import os
import subprocess

def run(args):
    if not args:
        print("Usage: spk <file.spk>")
        return
    
    filename = args[0]
    
    current_dir = os.path.dirname(os.path.abspath(__file__))  
    parent_dir = os.path.dirname(current_dir)                

    editor_path = os.path.join(parent_dir, "spoke.py")
    if not os.path.isfile(editor_path):
        print("Error: spoke.py not found in parent directory.")
        return

    # Check if it's a .spk file
    if not filename.endswith('.spk'):
        print("Error: File must have .spk extension")
        return

    # Make the .spk file path absolute if it's not already
    file_path = filename
    if not os.path.isabs(filename):
        file_path = os.path.abspath(os.path.join(os.getcwd(), filename))

    try:
        # Run the spoke program with the correct full path
        process = subprocess.Popen(
            ["python", "-u", editor_path, file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=0
        )
        
        # Print output in real-time
        for line in process.stdout:
            print(line, end='')
            
        process.wait()
            
        if process.returncode != 0:
            print(f"Program exited with code {process.returncode}")
        else:
            print("Program completed successfully")

    except Exception as e:
        print(f"Error: Could not run program: {e}")