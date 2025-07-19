import re

variables = {}
lineNum = 0

filename = "testCode.txt"  # Change to your file name

def errorLine(lineNum, line):
    print("Err on line " + str(lineNum))
    print("Line: " + line)
    quit()

def get_val(token):
    if token.isdigit():
        return int(token)
    elif token in variables:
        return variables[token]
    elif (token.startswith('"') and token.endswith('"')) or (token.startswith("'") and token.endswith("'")):
        return token[1:-1]  # Strip the quotes
    else:
        return token  # Unquoted literals (e.g., fallback)

def collect_block(lines, start_idx):
    """Collect lines between { and matching }"""
    block_lines = []
    brace_count = 0
    idx = start_idx
    
    # Find the opening brace
    while idx < len(lines):
        line = lines[idx].strip()
        if '{' in line:
            brace_count = 1
            idx += 1
            break
        idx += 1
    
    # Collect lines until matching closing brace
    while idx < len(lines) and brace_count > 0:
        line = lines[idx].strip()
        
        # Count braces in this line
        open_braces = line.count('{')
        close_braces = line.count('}')
        
        # If this line starts with a closing brace, we've found our block end
        if line.startswith('}'):
            # Don't include this line in the block content
            # But don't increment idx - let the caller handle this line
            break
        
        # Otherwise, include this line and update brace count
        block_lines.append(line)
        brace_count += open_braces - close_braces
        idx += 1
    
    return block_lines, idx

def execute_lines(lines, start_line_offset=0):
    global lineNum
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        actual_line_num = start_line_offset + i + 1
        
        if line.startswith("#") or line.startswith("@") or not line:
            i += 1
            continue
        
        tokens = re.findall(r'"[^"]*"|\'[^\']*\'|<<|>>|<=|>=|==|!=|=<|=>|\w+|[=+*/()%<>{}-]', line)
        if not tokens:
            i += 1
            continue
        
        cmd = tokens[0]
        
        if cmd == "let":
            lineNum = actual_line_num
            if len(tokens) == 4 and tokens[2] == '=':
                varname = tokens[1]
                value = get_val(tokens[3])
                variables[varname] = value
                print(f"{varname} = {value}")
            elif len(tokens) >= 6:
                varname = tokens[1]
                left_val = get_val(tokens[3])
                right_val = get_val(tokens[5])
                op = tokens[4]

                if op == '+':
                    result = left_val + right_val
                elif op == '-':
                    result = left_val - right_val
                elif op == '*':
                    result = left_val * right_val
                elif op == '/':
                    result = left_val / right_val
                elif op == '%':
                    result = left_val % right_val
                else:
                    errorLine(lineNum, line)

                variables[varname] = result
                #Debugging :D
                #print(f"{varname} = {result}")
            else:
                errorLine(lineNum, line)
            i += 1
        
        elif cmd == "print":
            lineNum = actual_line_num
            if len(tokens) >= 3 and tokens[1] == "(" and tokens[-1] == ")":
                sentence = ""
                for word in range(len(tokens) - 3):
                    sentence += " " + tokens[word + 2]
                print(sentence.strip())
            elif len(tokens) == 2:
                varname = tokens[1]
                if varname in variables:
                    print(variables[varname])
                else:
                    errorLine(lineNum, line)
            else:
                errorLine(lineNum, line)
            i += 1
        
        elif cmd == "input":
            lineNum = actual_line_num
            if len(tokens) == 2:
                inputVar = tokens[1]
                user_input = input("? ")
            elif len(tokens) == 3:
                inputVar = tokens[1]
                prompt = tokens[2]
                user_input = input(prompt + " ")
            else:
                errorLine(lineNum, line)

            try:
                variables[inputVar] = int(user_input)
            except ValueError:
                variables[inputVar] = user_input
            i += 1
        
        elif cmd == "if" and "then" in tokens and "{" in tokens:
            lineNum = actual_line_num
            # Parse if condition
            try:
                start = tokens.index("(")
                first = get_val(tokens[start + 1])
                op = tokens[start + 2]
                second = get_val(tokens[start + 3])
            except:
                errorLine(lineNum, line)

            # Evaluate condition
            if op == "==":
                cond = first == second
            elif op == "!=":
                cond = first != second
            elif op == "<<":
                cond = first < second
            elif op == ">>":
                cond = first > second
            elif op in ["<=", "=>"]:
                cond = first <= second
            elif op in [">=", "=<"]:
                cond = first >= second
            else:
                errorLine(lineNum, line)

            # Collect the if block  
            if_block_lines, new_i = collect_block(lines, i)
            
            if cond:
                execute_lines(if_block_lines, start_line_offset + i)
                executed_any = True
            else:
                executed_any = False
            
            # Set i to where collect_block left off
            i = new_i
            
            # Process else blocks
            if executed_any:
                # If the if block was executed, skip ALL else blocks
                while i < len(lines):
                    current_line = lines[i].strip()
                    
                    # Skip any closing brace lines that aren't else blocks
                    if current_line == "}":
                        i += 1
                        continue
                    
                    # Check if this is an else block
                    is_else_block = (current_line.startswith("else") or 
                                   (current_line.startswith("}") and "else" in current_line))
                    
                    if not is_else_block:
                        break
                    
                    # Skip this else block entirely
                    _, i = collect_block(lines, i)
            else:
                # If the if block was NOT executed, process else blocks
                while i < len(lines):
                    current_line = lines[i].strip()
                    
                    # Skip any closing brace lines that aren't else blocks
                    if current_line == "}":
                        i += 1
                        continue
                    
                    # Check if this is an else block
                    is_else_block = (current_line.startswith("else") or 
                                   (current_line.startswith("}") and "else" in current_line))
                    
                    if not is_else_block:
                        break
                    
                    lineNum = start_line_offset + i + 1
                    else_tokens = re.findall(r'<<|>>|<=|>=|==|!=|=<|=>|\w+|[=+*/()<>{}-]', current_line)
                    
                    try:
                        paren_idx = else_tokens.index("(")
                        if paren_idx + 1 < len(else_tokens) and else_tokens[paren_idx + 1] == ')':
                            # Unconditional else
                            else_cond = True
                        else:
                            first = get_val(else_tokens[paren_idx + 1])
                            op = else_tokens[paren_idx + 2]
                            second = get_val(else_tokens[paren_idx + 3])
                            
                            if op == "==":
                                else_cond = first == second
                            elif op == "!=":
                                else_cond = first != second
                            elif op == "<<":
                                else_cond = first < second
                            elif op == ">>":
                                else_cond = first > second
                            elif op in ["<=", "=>"]:
                                else_cond = first <= second
                            elif op in [">=", "=<"]:
                                else_cond = first >= second
                            else:
                                errorLine(lineNum, current_line)
                    except:
                        errorLine(lineNum, current_line)
                    
                    # Collect the else block
                    else_block_lines, i = collect_block(lines, i)
                    
                    # Execute if this condition is true
                    if else_cond:
                        execute_lines(else_block_lines, start_line_offset + i)
                        executed_any = True
                        # Once we execute an else block, skip any remaining ones
                        while i < len(lines):
                            skip_line = lines[i].strip()
                            
                            # Skip any closing brace lines
                            if skip_line == "}":
                                i += 1
                                continue
                                
                            skip_else_block = (skip_line.startswith("else") or 
                                             (skip_line.startswith("}") and "else" in skip_line))
                            if not skip_else_block:
                                break
                            _, i = collect_block(lines, i)
                        break
            
        elif cmd == "math":
            if len(tokens) == 4:
                tokens.append('silent')
            
            if tokens[4] == "silent" or tokens[4] == "loud":                
                left_val_math = int(tokens[1])
                right_val_math = int(tokens[3])
                op_math = tokens[2]
                result_math = 0
            
                if op_math == '+':
                    result_math = left_val_math + right_val_math
                elif op_math == '-':
                    result_math = left_val_math - right_val_math
                elif op_math == '*':
                    result_math = left_val_math * right_val_math
                elif op_math == '/':
                    result_math = left_val_math / right_val_math
                elif op_math == '%':
                    result_math = left_val_math % right_val_math
                else:
                    print("Invalid operator")
                    errorLine(lineNum, line)
            
                if tokens[4] == "loud":
                    print(result_math)
                i += 1 
            else:
                errorLine(lineNum, line)

        else:
            lineNum = actual_line_num
            errorLine(lineNum, line)

# Main execution
with open(filename, "r") as file:
    lines = file.readlines()
    execute_lines(lines)