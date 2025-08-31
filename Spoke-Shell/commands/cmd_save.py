import os

# commands/cmd_save.py
def run(tokens, variables, functions, get_val, errorLine, lineNum, line):
    """
    Handle save command
    tokens format: ['save', 'exampleFile', 'txt', '"Hello"'] (includes command)
    """
    
    if len(tokens) < 3:
        return False
    
    # Skip the command token, work with args only
    args = tokens[1:]  # ['exampleFile', 'txt', '"Hello"']
    
    # --- Parentheses form: save filename.txt ("Hello world") ---
    if "(" in args and args[-1] == ")":
        paren_index = args.index("(")
        # Reconstruct filename from tokens before parentheses
        fileName = ".".join(args[:paren_index])
        
        content_tokens = args[paren_index + 1:-1]
        words = []
        for token in content_tokens:
            if (token.startswith('"') and token.endswith('"')) or (token.startswith("'") and token.endswith("'")):
                words.append(token[1:-1])
            elif token in variables:
                words.append(str(variables[token]))
            else:
                words.append(token)
        sentence = " ".join(words).replace('\\n', '\n')

    # --- Regular forms ---
    else:
        # Check if last token is quoted content
        last_token = args[-1]
        if (last_token.startswith('"') and last_token.endswith('"')) or \
           (last_token.startswith("'") and last_token.endswith("'")):
            # Quoted string form: args like ['exampleFile', 'txt', '"Hello"']
            fileName = ".".join(args[:-1])  # Join all but last token with dots
            sentence = last_token[1:-1].replace('\\n', '\n')  # Remove quotes and handle newlines
        
        # Check if last token is a variable
        elif last_token in variables:
            fileName = ".".join(args[:-1])
            sentence = str(variables[last_token])
        
        # Raw content form
        else:
            # Assume first token is base filename, rest is content
            fileName = args[0]
            sentence = " ".join(args[1:]).replace('\\n', '\n')

    # Write to file (always append)
    try:
        with open(fileName, "a") as f:
            f.write(sentence)
        return True
    except Exception as e:
        return False