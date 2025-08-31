import os

def run(tokens, variables, functions, get_val, errorLine, lineNum, line):
    """
    Handle read command
    tokens format: ['read', 'sample', 'txt'] or ['read', 'sample', 'txt', '1'] etc.
    """
    
    if len(tokens) < 3:
        return False
    
    # Skip the command token, work with args only
    args = tokens[1:]  # ['sample', 'txt'] or ['sample', 'txt', '1']
    
    # Reconstruct filename: args[0] + "." + args[1]
    if len(args) >= 2:
        fileName = args[0] + "." + args[1]
        remaining_args = args[2:]
    else:
        fileName = args[0]
        remaining_args = []
    
    # Check if file exists and read it
    try:
        with open(fileName, "r") as f:
            file_lines = f.readlines()
    except Exception as e:
        return False
    
    # Handle different cases
    if len(remaining_args) == 0:
        # read sample.txt - print entire file
        for line_content in file_lines:
            print(line_content.rstrip())
    
    elif len(remaining_args) == 1:
        arg = remaining_args[0]
        
        if arg.isdigit():
            # read sample.txt 1 - print specific line
            line_num = int(arg)
            if 1 <= line_num <= len(file_lines):
                print(file_lines[line_num - 1].rstrip())
            else:
                return False
        else:
            # read sample.txt variableName - store entire file
            content = "".join(file_lines).rstrip()
            variables[arg] = content
    
    elif len(remaining_args) == 2:
        # read sample.txt 1 variableName - store specific line
        line_arg = remaining_args[0]
        var_name = remaining_args[1]
        
        if line_arg.isdigit():
            line_num = int(line_arg)
            if 1 <= line_num <= len(file_lines):
                variables[var_name] = file_lines[line_num - 1].rstrip()
            else:
                return False
        else:
            return False
    else:
        return False
    
    return True