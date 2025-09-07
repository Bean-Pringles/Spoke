def run(tokens, variables, functions, get_val, errorLine, lineNum, line):
    """
    Quit command: quit silent OR quit loud
    """
    if len(tokens) == 1:
        tokens.append("silent")
    
    if len(tokens) == 2:
        if tokens[1] == "loud":
            print("Quitting...")
            print("Quit Successful")
        elif tokens[1] == "silent":
            pass  # Quit silently
        else:
            print("Unknown Quit Argument, Fatal Error")
            return False
        
        quit()
    else:
        return False