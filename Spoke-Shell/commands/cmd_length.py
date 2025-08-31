def run(tokens, variables, functions, get_val, errorLine, lineNum, line):
    """
    Length command: length varname loud/silent [output_var]
    Gets the length of a variable's string representation
    """
    if len(tokens) in (3, 4):
        if tokens[1] in variables:
            length = len(str(variables[tokens[1]]))
            
            if tokens[2] == "loud":
                print(length)
            elif tokens[2] != "silent":
                print("Invalid argument")
                return False
            
            if len(tokens) == 4:
                variables[tokens[3]] = length
            return True
        else:
            print("Variable not found")
            return False
    else:
        print("Invalid argument(s)")
        return False