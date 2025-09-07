def run(tokens, variables, functions, get_val, errorLine, lineNum, line):
    """Find index of value in list: indexof mylist value result_var"""
    if len(tokens) >= 4:
        list_name = tokens[1]
        value = get_val(tokens[2])
        result_var = tokens[3]
        if list_name in variables and isinstance(variables[list_name], list):
            try:
                variables[result_var] = variables[list_name].index(value)
            except ValueError:
                variables[result_var] = -1
            return True
    return False