def run(tokens, variables, functions, get_val, errorLine, lineNum, line):
    """
    Pause command: pause silent OR pause loud [message]
    """
    if len(tokens) == 1:
        tokens.append("silent")

    if len(tokens) in (2, 3):
        if tokens[1] == "loud":
            if len(tokens) == 3:
                input(tokens[2])
            else:
                input("Press Enter to continue")
        elif tokens[1] == "silent":
            input('')
        else:
            print("Invalid argument")
            return False
        return True
    else:
        print("Invalid argument(s)")
        return False