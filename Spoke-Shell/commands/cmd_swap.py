def run(tokens, variables, functions, get_val, errorLine, lineNum, line):
    """
    Swap command: swap var1 var2
    Swaps the values of two variables
    """
    if len(tokens) == 3:
        if tokens[1] in variables and tokens[2] in variables:
            swap_1 = variables[tokens[1]]
            swap_2 = variables[tokens[2]]
            variables[tokens[1]] = swap_2
            variables[tokens[2]] = swap_1
            return True
        else:
            print("Variables don't exist")
            return False
    else:
        print("Wrong Amount of Arguments")
        return False