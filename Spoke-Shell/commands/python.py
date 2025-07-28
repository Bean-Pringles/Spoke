# commands/python.py
import os
import subprocess

def run(args):
    if not args:
        print("Usage: python <file.py>")
        return
    
    filename = args[0]
    
    # Check if file exists
    if not os.path.isfile(filename):
        print(f"Error: File '{filename}' not found")
        return
    
    # Check if it's a .py file
    if not filename.endswith('.py'):
        print("Error: File must have .py extension")
        return
    
    try:
        # Run the python program
        process = subprocess.Popen(
            ["python", "-u", filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=0,
            universal_newlines=True
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