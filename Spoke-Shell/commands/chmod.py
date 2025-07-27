import os

def run(args):
    if len(args) < 2:
        print("Usage: chmod <permissions> <filename>")
        return
    
    permissions = args[0]
    file_name = args[1]
    
    # Check if file exists
    if not os.path.exists(file_name):
        print(f"chmod: cannot access '{file_name}': No such file or directory")
        return
    
    # Parse permissions
    try:
        # Handle octal permissions (like 755, 644)
        if permissions.isdigit() and len(permissions) == 3:
            # Convert octal string to integer
            perm_int = int(permissions, 8)
        else:
            print(f"chmod: invalid mode: '{permissions}'")
            return
            
    except ValueError:
        print(f"chmod: invalid mode: '{permissions}'")
        return
    
    # Apply permissions
    try:
        os.chmod(file_name, perm_int)
    except PermissionError:
        print(f"chmod: changing permissions of '{file_name}': Operation not permitted")
    except Exception as e:
        print(f"chmod: error changing permissions: {e}")