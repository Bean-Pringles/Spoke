import time

def run(tokens, variables, functions, get_val, errorLine, lineNum, line):
    """
    Time command: time OR time varname
    """
    if len(tokens) == 1:
        print(time.strftime("%Y-%m-%d %H:%M:%S"))
        return True
    elif len(tokens) == 2:
        variables[tokens[1]] = time.strftime("%Y-%m-%d %H:%M:%S")
        return True
    else:
        print("Invalid argument(s)")
        return False