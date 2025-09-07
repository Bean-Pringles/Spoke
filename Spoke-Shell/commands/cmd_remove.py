def run(tokens, variables, functions, get_val, errorLine, lineNum, line):
    """Remove element by index: remove mylist index"""
    if len(tokens) >= 3:
        list_name = tokens[1]
        if list_name in variables and isinstance(variables[list_name], list):
            try:
                index = get_val(tokens[2])
                if isinstance(index, int) and 0 <= index < len(variables[list_name]):
                    variables[list_name].pop(index)
                    return True
            except (ValueError, IndexError):
                pass
    return False