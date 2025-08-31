def run(tokens, variables, functions, get_val, errorLine, lineNum, line):
    """
    Math command: math a + b silent/loud varname
    """
    if len(tokens) < 4 or len(tokens) > 6:
        return False
    
    # Default to loud if not specified
    if len(tokens) == 4:
        tokens.append('loud')
    
    if tokens[4] not in ['silent', 'loud']:
        return False
    
    left_val = get_val(tokens[1])
    op = tokens[2]
    right_val = get_val(tokens[3])
    output_mode = tokens[4]
    
    try:
        if op == '+':
            result = left_val + right_val
        elif op == '-':
            result = left_val - right_val
        elif op == '*':
            result = left_val * right_val
        elif op == '/':
            if right_val == 0:
                print("Error: Division by zero")
                return False
            result = left_val / right_val
        elif op == '%':
            result = left_val % right_val
        else:
            print("Invalid operator")
            return False
        
        if output_mode == "loud":
            print(result)
        
        if len(tokens) == 6:
            variables[tokens[5]] = result
        
        return True
    except Exception as e:
        print(f"Math error: {e}")
        return False