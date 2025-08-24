import random

def run(tokens, variables, functions, get_val, errorLine, lineNum, line):
    """
    Shuffle command: shuffle varname loud/silent [output_var]
    Shuffles the characters of a variable's string representation
    """
    if len(tokens) in (2, 3, 4):
        if tokens[1] in variables:
            chars = list(str(variables[tokens[1]]))
            random.shuffle(chars)

            if len(tokens) == 2:
                tokens.append("silent")

            if tokens[2] == "loud":
                print(''.join(chars))
            elif tokens[2] != "silent":
                print("Invalid argument")
                return False

            if len(tokens) == 4:
                variables[tokens[3]] = ''.join(chars)
            return True
        else:
            print("Variable not found")
            return False
    else:
        print("Invalid argument(s)")
        return False