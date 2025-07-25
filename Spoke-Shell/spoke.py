import re
import random
import time
import os
import sys

variables = {}
functions = {}  # Store function definitions
lineNum = 0 

if len(sys.argv) != 2:
    print("Usage: python spoke.py <filename>.spk")
    quit()

filename = sys.argv[1]

if not filename.endswith(".spk"):
    print("Error: Input file must have a .spk extension")
    quit()

def ifStatementConditional(first, second, op, lineNum, line):
    # Convert both values to comparable types
    def convert_val(val):
        if isinstance(val, str) and val.lstrip('-').replace('.', '').isdigit():
            if '.' in val:
                return float(val)
            return int(val)
        return val
    
    first = convert_val(first)
    second = convert_val(second)
    
    try:
        if op == "==":
            cond = first == second
        elif op == "!=":
            cond = first != second
        elif op == "<<":
            cond = first < second
        elif op == ">>":
            cond = first > second
        elif op in ["<=", "=<"]:
            cond = first <= second
        elif op in [">=", "=>"]:
            cond = first >= second
        else:
            print(f"DEBUG: Unknown operator '{op}' on line {lineNum}")
            print(f"DEBUG: Line content: {line}")
            return False
    except TypeError as e:
        # Handle type comparison errors (e.g., comparing string to number)
        print(f"DEBUG: TypeError in comparison on line {lineNum}: {e}")
        if op == "==":
            cond = False
        elif op == "!=":
            cond = True
        else:
            print(f"DEBUG: Cannot compare types for operator {op}")
            return False
    except Exception as e:
        print(f"DEBUG: Unexpected error in comparison on line {lineNum}: {e}")
        return False
    
    return cond

def errorLine(lineNum, line):
    print("Err on line " + str(lineNum))
    print("Line: " + line)
    quit()

def get_val(token):
    # Handle negative numbers
    if token.lstrip('-').replace('.', '').isdigit():
        if '.' in token:
            return float(token)
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
    found_opening = False
    
    # Find the opening brace
    while idx < len(lines):
        line = lines[idx].strip()
        if '{' in line:
            brace_count = 1
            found_opening = True
            idx += 1
            break
        idx += 1
    
    if not found_opening:
        return block_lines, idx
    
    # Collect lines until matching closing brace
    while idx < len(lines) and brace_count > 0:
        line = lines[idx].strip()
        
        # Count braces
        open_braces = line.count('{')
        close_braces = line.count('}')
        
        # Update brace count
        brace_count += open_braces - close_braces
        
        # Include this line in the block if it's not empty and we're still inside
        if line and brace_count > 0:
            block_lines.append(line)
        
        idx += 1
    
    return block_lines, idx

def parse_condition(tokens, lineNum, line):
    def eval_cond(lhs, op, rhs):
        return ifStatementConditional(get_val(lhs), get_val(rhs), op, lineNum, line)

    i = 0
    conditions = []
    operators = []

    if len(tokens) < 2:
        print(f"DEBUG: Not enough tokens for condition on line {lineNum}: {tokens}")
        errorLine(lineNum, line)

    while i < len(tokens):
        negate = False

        # Handle optional 'not'
        if i < len(tokens) and tokens[i] == 'not':
            negate = True
            i += 1

        if i + 2 >= len(tokens):
            print(f"DEBUG: Incomplete condition after 'not' on line {lineNum}")
            errorLine(lineNum, line)

        left = tokens[i]
        op = tokens[i + 1]
        right = tokens[i + 2]
        
        try:
            cond = eval_cond(left, op, right)
            if negate:
                cond = not cond
            conditions.append(cond)
        except Exception as e:
            print(f"DEBUG: Error evaluating condition {left} {op} {right} on line {lineNum}: {e}")
            conditions.append(False)
        
        i += 3

        # Logical operators
        if i < len(tokens) and tokens[i] in ("and", "or"):
            operators.append(tokens[i])
            i += 1

    # Apply logical operators with left-to-right precedence
    result = conditions[0] if conditions else False
    for j, op in enumerate(operators):
        if j + 1 < len(conditions):
            if op == "and":
                result = result and conditions[j + 1]
            elif op == "or":
                result = result or conditions[j + 1]

    return result

def parse_if_else_chain(lines, start_idx, start_line_offset=0):
    """Parse and execute an entire if-else-if-else chain"""
    global lineNum
    
    current_idx = start_idx
    line_offset = start_line_offset + start_idx
    
    # Process the initial if statement
    line = lines[current_idx].strip()
    tokens = re.findall(r'"[^"]*"|\'[^\']*\'|-?\d+\.?\d*|<<|>>|<=|>=|==|!=|=<|=>|\w+|[=+*/()%<>{}:!@#$%^&-]', line)
    
    if not (tokens[0] == "if" and "then" in tokens):
        errorLine(line_offset + 1, line)
    
    # Parse initial if condition
    try:
        paren_start = tokens.index("(")
        paren_end = tokens.index(")")
        condition_tokens = tokens[paren_start + 1:paren_end]
        if_condition = parse_condition(condition_tokens, line_offset + 1, line)
    except (ValueError, Exception) as e:
        errorLine(line_offset + 1, line)
    
    # Skip to block content
    current_idx += 1
    
    # Collect all blocks and their conditions
    blocks = []  # List of (condition, block_lines) tuples
    
    # Collect the if block
    if_block_lines = []
    brace_count = 1
    
    while current_idx < len(lines) and brace_count > 0:
        block_line = lines[current_idx].strip()
        
        if block_line.startswith("} else") or (block_line == "}" and brace_count == 1):
            break
            
        brace_count += block_line.count('{') - block_line.count('}')
        
        if block_line and brace_count > 0:
            if_block_lines.append(block_line)
            
        current_idx += 1
    
    blocks.append((if_condition, if_block_lines))
    
    # Process else-if and else blocks
    while current_idx < len(lines):
        line = lines[current_idx].strip()
        
        if line.startswith("} else"):
            else_part = line[1:].strip()  # Remove }
            else_tokens = re.findall(r'"[^"]*"|\'[^\']*\'|-?\d+\.?\d*|<<|>>|<=|>=|==|!=|=<|=>|\w+|[=+*/()%<>{}:!@#$%^&-]', else_part)
            
            block_condition = False
            
            if len(else_tokens) > 1 and else_tokens[0] == "else" and else_tokens[1] == "if":
                # else if
                try:
                    paren_start = else_tokens.index("(")
                    paren_end = else_tokens.index(")")
                    condition_tokens = else_tokens[paren_start + 1:paren_end]
                    block_condition = parse_condition(condition_tokens, line_offset + current_idx + 1, line)
                except (ValueError, Exception):
                    errorLine(line_offset + current_idx + 1, line)
            elif len(else_tokens) >= 1 and else_tokens[0] == "else":
                # plain else
                block_condition = True
            
            # Move to block content
            current_idx += 1
            
            # Collect this block
            block_lines = []
            brace_count = 1
            
            while current_idx < len(lines) and brace_count > 0:
                block_line = lines[current_idx].strip()
                
                if block_line.startswith("} else") or (block_line == "}" and brace_count == 1):
                    break
                    
                brace_count += block_line.count('{') - block_line.count('}')
                
                if block_line and brace_count > 0:
                    block_lines.append(block_line)
                    
                current_idx += 1
            
            blocks.append((block_condition, block_lines))
            
        elif line == "}":
            current_idx += 1
            break
        else:
            current_idx += 1
    
    # Execute the first block whose condition is True
    for condition, block_lines in blocks:
        if condition:
            execute_lines(block_lines, line_offset)
            break  # Only execute the first matching block
    
    return current_idx

def execute_lines(lines, start_line_offset=0):
    global lineNum
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        actual_line_num = start_line_offset + i + 1
        
        # Skip comments, empty lines, and standalone closing braces that aren't part of if-else
        if line.startswith("#") or line.startswith("@") or not line:
            i += 1
            continue
        
        # Skip } else lines as they're handled by the if-else chain parser
        if line.startswith("} else"):
            i += 1
            continue
        
        tokens = re.findall(r'"[^"]*"|\'[^\']*\'|-?\d+\.?\d*|<<|>>|<=|>=|==|!=|=<|=>|\w+|[=+*/()%<>{}:!@#$%^&-]', line)
        if not tokens:
            i += 1
            continue
        
        cmd = tokens[0]
        
        try:
            if cmd == "function" and len(tokens) >= 4 and tokens[2] == "(" and ")" in tokens and "{" in line:
                lineNum = actual_line_num
                func_name = tokens[1]
                
                # Extract parameters between ( and )
                paren_start = tokens.index("(")
                paren_end = tokens.index(")")
                params = []
                for j in range(paren_start + 1, paren_end):
                    if tokens[j] != ",":
                        params.append(tokens[j])
                
                # Collect function body
                func_body, new_i = collect_block(lines, i)
                
                # Store function definition
                functions[func_name] = {
                    'params': params,
                    'body': func_body
                }
                
                i = new_i
            
            elif cmd in functions:
                # Function call
                lineNum = actual_line_num
                func_name = cmd
                
                if len(tokens) >= 3 and tokens[1] == "(":
                    # Extract arguments
                    try:
                        paren_end = tokens.index(")")
                        args = []
                        for j in range(2, paren_end):
                            if tokens[j] != ",":
                                args.append(get_val(tokens[j]))
                        
                        # Check parameter count
                        if len(args) != len(functions[func_name]['params']):
                            errorLine(lineNum, line)
                        
                        # Save current variables (simple scope handling)
                        saved_vars = variables.copy()
                        
                        # Set up parameters as local variables
                        for param, arg in zip(functions[func_name]['params'], args):
                            variables[param] = arg
                        
                        # Execute function body
                        execute_lines(functions[func_name]['body'], start_line_offset)
                        
                        # Restore variables - keep global vars that were modified, remove local-only vars
                        for var in list(variables.keys()):
                            if var in functions[func_name]['params']:
                                # This was a parameter - remove it unless it existed globally
                                if var in saved_vars:
                                    variables[var] = saved_vars[var]
                                else:
                                    del variables[var]
                    except ValueError:
                        errorLine(lineNum, line)
                else:
                    errorLine(lineNum, line)
                i += 1
            
            #clear
            elif cmd == "clear":
                if os.name == 'nt':  # For Windows
                    os.system('cls')
                else:  # For Linux/macOS
                    os.system('clear')
                i += 1
            
            #pause silent
            elif cmd == "pause":
                if len(tokens) == 1:
                    tokens.append("silent")

                if len(tokens) in  (2, 3):
                    if tokens[1] == "loud":
                        if len(tokens) == 3:
                            input(tokens[2])
                        else:
                            input("Press Enter to continue")
                    elif tokens[1] == "silent":
                        input('')
                    else:
                        print("Invaild arguement")
                        errorLine(lineNum, line)  
                else:
                    print("Invaild arguement(s)")
                    errorLine(lineNum, line)  
                i += 1
                    
            #time abc
            elif cmd == "time":
                if len(tokens) == 1:
                    print(time.strftime("%Y-%m-%d %H:%M:%S"))
                elif len(tokens) == 2:
                    variables[tokens[1]] = time.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    print("Invaild arguement(s)")
                    errorLine(lineNum, line)  
                i += 1

            #length abc loud def
            elif cmd == "length":
                if len(tokens) in (3, 4):
                    length = len(str(variables[tokens[1]]))
                    
                    if tokens[2] == "loud":
                        print(length)
                    
                    if len(tokens) == 4:
                        variables[tokens[3]] = length

                else:
                    print("Invaild arguement(s)")
                    errorLine(lineNum, line)
                i += 1

                #shuffle abc loud def
            elif cmd == "shuffle":
                if len(tokens) in (4, 3, 2):
                    chars = list(str(variables[tokens[1]]))
                    random.shuffle(chars)

                    if len(tokens) == 2:
                        tokens.append("silent")

                    if tokens[2] == "loud":
                        print(''.join(chars))  # join list back to string for printing

                    if len(tokens) == 4:
                        variables[tokens[3]] = ''.join(chars)  # store as a string

                else:
                    print("Invalid argument(s)")
                    errorLine(lineNum, line)
                i += 1

            #toggle abc
            elif cmd == "toggle":
                if len(tokens) == 2:
                    if tokens[1] in variables:
                        if variables[tokens[1]] in (0, 1):
                            if variables[tokens[1]] == 0:
                                variables[tokens[1]] = 1
                            elif variables[tokens[1]] == 1:
                                variables[tokens[1]] = 0
                            else:
                                print("Varible cannot be toggled")
                                errorLine(lineNum, line)
                        elif variables[tokens[1]] in ("true", "false"):
                            if variables[tokens[1]] == "false":
                               variables[tokens[1]] = "true"
                            elif variables[tokens[1]] == "true":
                                variables[tokens[1]] = "false"
                            else:
                                print("Varible cannot be toggled")
                                errorLine(lineNum, line)
                        else:
                            print("Varible cannot be toggled")
                            errorLine(lineNum, line)
                    else:
                        print("Varible not found")
                        errorLine(lineNum, line)
                else:
                    errorLine(lineNum, line)
                i += 1

            # swap abc def
            elif cmd == "swap":
                if len(tokens) == 3:
                    if tokens[1] in variables and tokens[2] in variables:
                        swap_1 = variables[tokens[1]]
                        swap_2 = variables[tokens[2]]
                        variables[tokens[1]] = swap_2
                        variables[tokens[2]] = swap_1
                        
                    else:
                        print("Varibles dont exist")
                        errorLine(lineNum, line)
                else:
                    print("Wrong Amout of Arguements")
                    errorLine(lineNum, line)
                i += 1

            # compare abc adf list
            elif cmd == "compare":
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
                            
                    else:
                        print("Varibles dont exist")
                        errorLine(lineNum, line)
                else:
                    print("Wrong Amount of Arguements")
                    errorLine(lineNum, line)
                i += 1

            # sleep 45 
            elif cmd == "sleep":
                if len(tokens) == 2:
                    time.sleep(int(tokens[1]))
                else:
                    errorLine(lineNum, line)
                i += 1

            elif cmd == "delete":
                var_delete = tokens[1]
                if var_delete in variables:
                    del variables[var_delete]
                else:
                    print("Varible not found")
                    errorLine(line, lineNum)
                i += 1

            # countdown 6 Finish 
            elif cmd == "countdown":
                if len(tokens) in (2, 3):
                    count_countdown = int(tokens[1])
                    for count_repeats in range(count_countdown):
                        print (count_countdown - count_repeats)
                        time.sleep(1)
                        
                    if len(tokens) == 3:
                        print(tokens[2])
                i += 1

            elif cmd == "let":
                lineNum = actual_line_num
                if len(tokens) == 4 and tokens[2] == '=':
                    varname = tokens[1]
                    value = get_val(tokens[3])
                    variables[varname] = value
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
                else:
                    errorLine(lineNum, line)
                i += 1
            
            elif cmd == "print":
                lineNum = actual_line_num
                if len(tokens) >= 3 and tokens[1] == "(" and tokens[-1] == ")":
                    sentence = ""
                    for word in range(2, len(tokens) - 1):
                        if word > 2:  # Add space between words
                            sentence += " "
                        token = tokens[word]
                        # Don't process variables in parentheses - treat as literals
                        if (token.startswith('"') and token.endswith('"')) or (token.startswith("'") and token.endswith("'")):
                            sentence += token[1:-1]  # Strip quotes
                        else:
                            sentence += token  # Keep as literal
                    print(sentence)
                elif len(tokens) == 2:
                    varname = tokens[1]
                    if varname in variables:
                        print(variables[varname])
                    else:
                        errorLine(lineNum, line)
                else:
                    errorLine(lineNum, line)
                i += 1
            
            
            # random (1, 5) abc
            elif cmd == "random":
                # lowest
                lowest_random = int(tokens[2])
                # highest
                highest_random = int(tokens[3])
                # var
                var_random = tokens[5]

                randomInt = random.randint(lowest_random, highest_random)
                variables[var_random] = randomInt
                
                if len(tokens) == 6:
                    tokens.append("silent")

                if tokens[6] == "loud":
                    print (randomInt)

                i += 1
            
            elif cmd == "quit":
                if len(tokens) == 2:
                    if tokens[1] == "loud":
                        print("Quitting...")
                        print("Quit Succsessful")
                    elif tokens[1] != "silent":
                        print("Unknown Quit Arguement, Fatal Error")

                quit()
                i += 1 # :D Its a format
            
            elif cmd == "input":
                lineNum = actual_line_num
                if len(tokens) == 2:
                    inputVar = tokens[1]
                    user_input = input("? ")
                elif len(tokens) >= 3:
                    inputVar = tokens[1]
                    prompt = "".join(tokens[2:])
                    user_input = input(prompt + " ")
                else:
                    errorLine(lineNum, line)

                try:
                    variables[inputVar] = int(user_input)
                except ValueError:
                    variables[inputVar] = user_input
                i += 1
            
            elif cmd == "if" and "then" in tokens and "{" in line:
                # Use the if-else chain parser
                i = parse_if_else_chain(lines, i, start_line_offset)
            
            # math a  / b silent abc
            elif cmd == "math" and len(tokens) >= 3 and len(tokens) <= 6:
                lineNum = actual_line_num
                if len(tokens) == 4:
                    tokens.append('loud')
                
                if tokens[4] == "silent" or tokens[4] == "loud":                
                    left_token_math = tokens[1]
                    op_math = tokens[2]
                    right_token_math = tokens[3]
                    output_mode = tokens[4]

                    left_val_math = get_val(left_token_math)
                    right_val_math = get_val(right_token_math)

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
                
                    if len(tokens) == 6:
                        inputVar_math = tokens[5]
                        variables[inputVar_math] = result_math

                else:
                    errorLine(lineNum, line)
            
            elif line == "}" or line.startswith("} else"):
                # Skip these as they're handled by the if-else parser
                i += 1

            else:
                lineNum = actual_line_num
                print(f"DEBUG: Unknown command '{cmd}' on line {lineNum}")
                print(f"DEBUG: Full line: {line}")
                print(f"DEBUG: Tokens: {tokens}")
                errorLine(lineNum, line)
        
        except Exception as e:
            print(f"DEBUG: Unexpected error on line {lineNum}: {e}")
            print(f"DEBUG: Line: {line}")
            errorLine(lineNum, line)

# Main execution
with open(filename, "r") as file:
    lines = [line.rstrip('\n\r') for line in file.readlines()]  # Strip newlines but keep content
    execute_lines(lines)