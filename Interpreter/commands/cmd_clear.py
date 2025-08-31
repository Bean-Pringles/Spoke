import os

def run(tokens, variables, functions, get_val, errorLine, lineNum, line):
    """
    Clear command: clears the screen
    """
    if len(tokens) == 1:
        if os.name == 'nt':  # For Windows
            os.system('cls')
        else:  # For Linux/macOS
            os.system('clear')
        return True
    else:
        return False