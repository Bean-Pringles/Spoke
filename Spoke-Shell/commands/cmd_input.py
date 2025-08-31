def run(tokens, variables, functions, get_val, errorLine, lineNum, line):
    """
    Input command: input varname OR input varname prompt
    """
    if len(tokens) == 2:
        inputVar = tokens[1]
        user_input = input("? ")
    elif len(tokens) >= 3:
        inputVar = tokens[1]
        prompt = " ".join(tokens[2:])
        user_input = input(prompt + " ")
    else:
        return False

    # Try to convert to int, otherwise keep as string
    try:
        variables[inputVar] = int(user_input)
    except ValueError:
        variables[inputVar] = user_input
    
    return True