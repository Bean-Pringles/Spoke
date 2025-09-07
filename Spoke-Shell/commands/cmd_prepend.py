def run(tokens, variables, functions, get_val, errorLine, lineNum, line):
    """Prepend element to list: prepend mylist value"""
    if len(tokens) >= 3:
        list_name = tokens[1]
        if list_name in variables and isinstance(variables[list_name], list):
            value = get_val(tokens[2])
            variables[list_name].insert(0, value)
            return True
    return False