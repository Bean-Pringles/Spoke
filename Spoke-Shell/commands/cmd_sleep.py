import time

def run(tokens, variables, functions, get_val, errorLine, lineNum, line):
    """
    Sleep command: sleep seconds
    """
    if len(tokens) == 2:
        try:
            seconds = int(get_val(tokens[1]))
            time.sleep(seconds)
            return True
        except ValueError:
            print("Invalid sleep duration")
            return False
    else:
        return False