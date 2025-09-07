def run(tokens, variables, functions, get_val, errorLine, lineNum, line):
    """Get list length: length mylist result_var"""
    if len(tokens) >= 3:
        list_name = tokens[1]
        result_var = tokens[2]
        if list_name in variables and isinstance(variables[list_name], list):
            variables[result_var] = len(variables[list_name])
            return True
    return False