def run(tokens, variables, functions, get_val, errorLine, lineNum, line):
    """Reverse list in place: reverse mylist"""
    if len(tokens) >= 2:
        list_name = tokens[1]
        if list_name in variables and isinstance(variables[list_name], list):
            variables[list_name].reverse()
            return True
    return False