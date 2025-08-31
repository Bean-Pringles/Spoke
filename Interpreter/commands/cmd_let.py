def run(tokens, variables, functions, get_val, errorLine, lineNum, line):
    """
    Let command for variable assignment: let var = value OR let var = a + b
    """
    if len(tokens) == 4 and tokens[2] == '=':
        # Simple assignment: let var = value
        varname = tokens[1]
        value = get_val(tokens[3])
        variables[varname] = value
        return True
    elif len(tokens) >= 6 and tokens[2] == '=':
        # Mathematical assignment: let var = a + b
        varname = tokens[1]
        left_val = get_val(tokens[3])
        op = tokens[4]
        right_val = get_val(tokens[5])

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

            variables[varname] = result
            return True
        except Exception as e:
            print(f"Let operation error: {e}")
            return False
    else:
        return False