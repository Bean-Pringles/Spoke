def run(tokens, variables, functions, get_val, errorLine, lineNum, line):
    """
    Toggle command: toggle varname
    Toggles between 0/1 or true/false
    """
    if len(tokens) == 2:
        if tokens[1] in variables:
            if variables[tokens[1]] in (0, 1):
                variables[tokens[1]] = 1 - variables[tokens[1]]
                return True
            elif variables[tokens[1]] in ("true", "false"):
                if variables[tokens[1]] == "false":
                    variables[tokens[1]] = "true"
                else:
                    variables[tokens[1]] = "false"
                return True
            else:
                print("Variable cannot be toggled")
                return False
        else:
            print("Variable not found")
            return False
    else:
        return False