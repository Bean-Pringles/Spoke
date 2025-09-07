def run(tokens, variables, functions, get_val, errorLine, lineNum, line):
    """Sort list in place: sort mylist"""
    try:
        if len(tokens) < 2:
            print(f"Error: 'sort' command requires 1 argument on line {lineNum}")
            return False
        
        list_name = tokens[1]
        if list_name not in variables:
            print(f"Error: Variable '{list_name}' does not exist on line {lineNum}")
            return False
        
        if not isinstance(variables[list_name], list):
            print(f"Error: Variable '{list_name}' is not a list on line {lineNum}")
            return False
        
        try:
            variables[list_name].sort()
            return True
        except TypeError as te:
            print(f"Error: Cannot sort list with mixed types on line {lineNum}: {te}")
            return False
    except Exception as e:
        print(f"Error in sort command on line {lineNum}: {e}")
        return False