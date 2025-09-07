def run(tokens, variables, functions, get_val, errorLine, lineNum, line):
    """Clear all elements from list: clear mylist"""
    if len(tokens) >= 2:
        list_name = tokens[1]
        if list_name in variables and isinstance(variables[list_name], list):
            variables[list_name].clear()
            return True
    return False