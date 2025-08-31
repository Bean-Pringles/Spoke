import os

def run(tokens, variables, functions, get_val, errorLine, lineNum, line):
    if len(tokens) != 2:
        print("Incorrect Arguements")
        errorLine(lineNum, line)
        return False
    
    var = tokens[1]
    
    try:
        value = get_val(var)
        
        # Convert string numbers to actual numbers
        if isinstance(value, str):
            if value.lstrip('-').replace('.', '').isdigit():
                value = float(value) if '.' in value else int(value)
            else:
                errorLine(lineNum, line)
                return False
        
        value = value - 1
        variables[var] = value
        return True

    except Exception as e:
        print(f"DEBUG: Exception occurred: {e}")
        errorLine(lineNum, line)
        return False