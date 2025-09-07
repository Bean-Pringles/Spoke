import random

def run(args):
    """
    Shuffle command for shell
    Syntax:
    - shuffle varname
    - shuffle varname loud  
    - shuffle varname loud resultvar
    """
    
    if len(args) < 1 or len(args) > 3:
        print("Usage: shuffle varname [loud] [resultvar]")
        return
    
    varname = args[0]
    is_loud = len(args) >= 2 and args[1] == "loud"
    result_var = args[2] if len(args) == 3 else None
    
    # For demonstration, we'll create some sample data
    # In a real shell, you'd get this from your variable system
    sample_data = ["apple", "banana", "cherry", "date", "elderberry"]
    
    # Make a copy and shuffle it
    shuffled = sample_data.copy()
    random.shuffle(shuffled)
    
    if is_loud:
        print(f"Shuffled {varname}: {shuffled}")
    
    if result_var:
        print(f"Result stored in variable '{result_var}'")
        # In a real implementation: variables[result_var] = shuffled
    else:
        print(f"Variable '{varname}' has been shuffled")
        # In a real implementation: variables[varname] = shuffled