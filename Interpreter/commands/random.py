import random

def run(tokens, variables, functions, get_val, errorLine, lineNum, line):
    """
    Random command: random ( low , high ) varname [loud/silent]
    """
    if len(tokens) < 6:
        return False
    
    if tokens[1] != "(" or tokens[3] != "," or tokens[5] != ")":
        return False
    
    try:
        lowest_random = int(get_val(tokens[2]))
        highest_random = int(get_val(tokens[4]))
        var_random = tokens[6]
        
        randomInt = random.randint(lowest_random, highest_random)
        variables[var_random] = randomInt
        
        # Default to silent if not specified
        if len(tokens) == 7:
            tokens.append("silent")
        
        if len(tokens) == 8 and tokens[7] == "loud":
            print(randomInt)
        
        return True
    except ValueError:
        print("Invalid random range values")
        return False
    except Exception as e:
        print(f"Random error: {e}")
        return False