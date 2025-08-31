def run(tokens, variables, functions, get_val, errorLine, lineNum, line):
    """
    Delete command: delete varname
    Deletes a variable from memory
    """
    if len(tokens) == 2:
        var_delete = tokens[1]
        if var_delete in variables:
            del variables[var_delete]
            return True
        else:
            print("Variable not found")
            return False
    else:
        return False