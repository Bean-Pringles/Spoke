#round exampleVar 2 exampleVar2
# or round exampleVar 2 loud

import os

def run(tokens, variables, functions, get_val, errorLine, lineNum, line):
    if len(tokens) < 4:
        errorLine(lineNum, line)
        return False

    try:
        var_value = get_val(tokens[1])          
        rounded_digit = int(get_val(tokens[2])) 

        rounded_value = round(var_value, rounded_digit)

        target = tokens[3]
        if target == "loud":
            print(f"{rounded_value:.{rounded_digit}f}")
        else:
            variables[target] = rounded_value

        return True

    except Exception as e:
        print(f"DEBUG: Error on line {lineNum}: {e}")
        errorLine(lineNum, line)