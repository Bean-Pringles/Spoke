def run(tokens, variables, functions, get_val, errorLine, lineNum, line):
    """
    Print command: print varname OR print ( text here )
    """
    if len(tokens) >= 3 and tokens[1] == "(" and tokens[-1] == ")":
        # Print literal text in parentheses
        sentence = ""
        for word in range(2, len(tokens) - 1):
            if word > 2:
                sentence += " "
            token = tokens[word]
            if (token.startswith('"') and token.endswith('"')) or (token.startswith("'") and token.endswith("'")):
                sentence += token[1:-1]  # Strip quotes
            else:
                sentence += token  # Keep as literal
        print(sentence)
        return True
    elif len(tokens) == 2:
        # Print variable value
        varname = tokens[1]
        if varname in variables:
            print(variables[varname])
            return True
        else:
            print(f"Variable '{varname}' not found")
            return False
    else:
        return False