def run(tokens, variables, functions, get_val, errorLine, lineNum, line):
    """Check if list contains value: contains mylist value result_var"""
    if len(tokens) >= 4:
        list_name = tokens[1]
        value = get_val(tokens[2])
        result_var = tokens[3]
        if list_name in variables and isinstance(variables[list_name], list):
            variables[result_var] = value in variables[list_name]
            return True
    return False