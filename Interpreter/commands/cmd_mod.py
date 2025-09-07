# mod newVar = abs(originalVar) 
# abs, floor, ceiling, sin, cos, tan, asin, acos, atan
import os
import math

def run(tokens, variables, functions, get_val, errorLine, lineNum, line):
    if len(tokens) < 4:
        print("Incorrect Arguements")
        errorLine(lineNum, line)
        return False
    
    try:
        index = tokens.index("=") 
    except ValueError:
        print("Incorrect Arguements")
        errorLine(lineNum, line)
        return False
    
    operation = tokens[index + 1]
    operand = get_val(tokens[index + 3])  # This gets 'originalVar'
    
    # Convert string numbers to actual numbers
    if isinstance(operand, str):
        if operand.lstrip('-').replace('.', '').isdigit():
            operand = float(operand) if '.' in operand else int(operand)
        else:
            print("Invalid number")
            errorLine(lineNum, line)
            return False
        
    if tokens[len(tokens) - 1] != ")" or tokens[index + 2] != "(":
        print("Incorrect Arguements")
        errorLine(lineNum, line)
        return False

    if operation == "abs":
        value = abs(operand)
    elif operation == "floor":
        value = math.floor(operand)
    elif operation == "ceiling":
        value = math.ceil(operand)
    elif operation == "sin":
        value = math.sin(operand)
    elif operation == "cos":
        value = math.cos(operand)
    elif operation == "tan":
        value = math.tan(operand)
    elif operation == "asin":
        value = math.asin(operand)
    elif operation == "acos":
        value = math.acos(operand)   
    elif operation == "atan":
        value = math.atan(operand)
    else:
        print("Operation Not Found")
        errorLine(lineNum, line)
        return False
    
    variables[tokens[1]] = value
    return True