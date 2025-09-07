def run(tokens, variables, functions, get_val, errorLine, lineNum, line):
    """Insert element at index: insert mylist index value"""
    if len(tokens) >= 4:
        list_name = tokens[1]
        if list_name in variables and isinstance(variables[list_name], list):
            try:
                index = get_val(tokens[2])
                value = get_val(tokens[3])
                if isinstance(index, int) and 0 <= index <= len(variables[list_name]):
                    variables[list_name].insert(index, value)
                    return True
            except (ValueError, IndexError):
                pass
    return False