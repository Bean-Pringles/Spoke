import random

def run(args):
    """
    Random number generator command for shell
    Syntax:
    - random (min, max) varname
    - random (min, max) varname loud
    """
    
    if len(args) < 3:
        print("Usage: random (min, max) varname [loud]")
        return
    
    # Parse arguments: ['(', 'min,', 'max)', 'varname'] or similar
    # Look for parentheses pattern
    if args[0] != "(" or ")" not in args:
        print("Usage: random (min, max) varname [loud]")
        return
    
    try:
        # Find the closing parenthesis
        paren_end = -1
        for i, arg in enumerate(args):
            if ")" in arg:
                paren_end = i
                break
        
        if paren_end == -1:
            print("Usage: random (min, max) varname [loud]")
            return
        
        # Extract range values
        range_parts = []
        for i in range(1, paren_end + 1):
            part = args[i].replace(")", "").replace(",", "")
            if part:
                range_parts.append(part)
        
        if len(range_parts) != 2:
            print("Usage: random (min, max) varname [loud]")
            return
        
        min_val = int(range_parts[0])
        max_val = int(range_parts[1])
        
        # Get variable name and loud flag
        remaining_args = args[paren_end + 1:]
        if len(remaining_args) < 1:
            print("Usage: random (min, max) varname [loud]")
            return
        
        varname = remaining_args[0]
        is_loud = len(remaining_args) >= 2 and remaining_args[1] == "loud"
        
        # Generate random number
        random_num = random.randint(min_val, max_val)
        
        if is_loud:
            print(f"Generated random number: {random_num}")
        
        print(f"Random number {random_num} stored in variable '{varname}'")
        # In a real implementation: variables[varname] = random_num
        
    except ValueError:
        print("Error: Min and max values must be integers")
    except Exception as e:
        print(f"Error: {e}")