def run(tokens, variables, functions, get_val, errorLine, lineNum, line):
    """Create a list: list mylist = [1,2,3]"""
    if len(tokens) >= 4 and tokens[2] == "=":
        list_name = tokens[1]
        list_value = get_val(tokens[3])
        if isinstance(list_value, list):
            variables[list_name] = list_value
            return True
        else:
            return False
    return False