def run(tokens, variables, functions, get_val, errorLine, lineNum, line):
    """
    Compare command: compare var1 var2 [list]
    Compares two variables and prints the result
    """
    if len(tokens) in (3, 4):
        if tokens[1] in variables and tokens[2] in variables:
            compare_1 = variables[tokens[1]]
            compare_2 = variables[tokens[2]]

            if len(tokens) == 3:
                if compare_1 == compare_2:
                    print("Equal")
                elif compare_1 > compare_2:
                    print("Greater Than")
                elif compare_1 < compare_2:
                    print("Less than")
            else:
                if compare_1 == compare_2:
                    print(tokens[1] + " is Equal to " + tokens[2])
                elif compare_1 > compare_2:
                    print(tokens[1] + " is Greater than " + tokens[2])
                elif compare_1 < compare_2:
                    print(tokens[1] + " is Less than " + tokens[2])
            return True
        else:
            print("Variables don't exist")
            return False
    else:
        print("Wrong Amount of Arguments")
        return False