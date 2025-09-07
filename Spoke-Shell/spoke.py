import re
import os
import sys
import importlib
import importlib.util
from pathlib import Path

variables = {}
functions = {}
lineNum = 0 

if len(sys.argv) != 2:
    print("Usage: python spoke.py <filename>.spk")
    quit()

filename = sys.argv[1]

if not filename.endswith(".spk"):
    print("Error: Input file must have a .spk extension")
    quit()

# Ensure commands directory exists
commands_dir = Path("commands")
commands_dir.mkdir(exist_ok=True)

def slicer(line):
    """Parse and slice the input line into command and arguments"""
    tokens = re.findall(r'"[^"]*"|\'[^\']*\'|\[[^\]]*\]|-?\d+\.?\d*|<<|>>|<=|>=|==|!=|=<|=>|\w+|[=+*/()%<>{}:!@#$%^&-]', line)
    if not tokens:
        return None, []
    
    command = tokens[0]
    args = tokens[1:]
    return command, args

commands_dir = Path("commands")

def load_command(command_name):
    """Dynamically load and execute a command from the commands folder"""
    command_path = commands_dir / f"cmd_{command_name}.py"
    
    if not command_path.exists():
        return None

    try:
        spec = importlib.util.spec_from_file_location(f"spoke_commands.{command_name}", command_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[f"spoke_commands.{command_name}"] = module
        spec.loader.exec_module(module)

        if hasattr(module, "run"):
            return module.run
        else:
            print(f"Error: cmd_{command_name}.py missing 'run' function")
            return None
    except Exception as e:
        print(f"Error loading command {command_name}: {e}")
        return None

def parse_list(list_str):
    """Parse a list string like '[1,2,3]' or '["a","b","c"]' into a Python list"""
    if not (list_str.startswith('[') and list_str.endswith(']')):
        return None
    
    content = list_str[1:-1].strip()
    if not content:
        return []
    
    # Split by commas, but respect quoted strings
    items = []
    current_item = ""
    in_quotes = False
    quote_char = None
    
    for char in content:
        if char in ('"', "'") and not in_quotes:
            in_quotes = True
            quote_char = char
            current_item += char
        elif char == quote_char and in_quotes:
            in_quotes = False
            quote_char = None
            current_item += char
        elif char == ',' and not in_quotes:
            items.append(current_item.strip())
            current_item = ""
        else:
            current_item += char
    
    if current_item.strip():
        items.append(current_item.strip())
    
    # Convert items to appropriate types
    result = []
    for item in items:
        item = item.strip()
        if not item:
            continue
        
        # String literal
        if (item.startswith('"') and item.endswith('"')) or (item.startswith("'") and item.endswith("'")):
            result.append(item[1:-1])
        # Number
        elif item.lstrip('-').replace('.', '').isdigit():
            if '.' in item:
                result.append(float(item))
            else:
                result.append(int(item))
        # Variable reference
        elif item in variables:
            result.append(variables[item])
        # Raw value
        else:
            result.append(item)
    
    return result

def list_to_string(lst):
    """Convert a Python list back to string representation"""
    if not isinstance(lst, list):
        return str(lst)
    
    items = []
    for item in lst:
        if isinstance(item, str):
            items.append(f'"{item}"')
        else:
            items.append(str(item))
    
    return '[' + ','.join(items) + ']'

def ifStatementConditional(first, second, op, lineNum, line):
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
            return False
    except TypeError as e:
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
    # Handle list literals
    if token.startswith('[') and token.endswith(']'):
        return parse_list(token)
    # Handle list indexing
    elif '[' in token and ']' in token and not token.startswith('['):
        # Variable with index like: mylist[0]
        parts = token.split('[', 1)
        var_name = parts[0]
        index_part = '[' + parts[1]
        
        if var_name in variables and isinstance(variables[var_name], list):
            try:
                index_str = index_part[1:-1]  # Remove [ and ]
                if index_str.lstrip('-').isdigit():
                    index = int(index_str)
                    if -len(variables[var_name]) <= index < len(variables[var_name]):
                        return variables[var_name][index]
                    else:
                        return None  # Index out of bounds
                elif index_str in variables:
                    index = variables[index_str]
                    if isinstance(index, int) and -len(variables[var_name]) <= index < len(variables[var_name]):
                        return variables[var_name][index]
                    else:
                        return None
            except (ValueError, IndexError):
                return None
        return token
    # Handle numbers
    elif token.lstrip('-').replace('.', '').isdigit():
        if '.' in token:
            return float(token)
        return int(token)
    # Handle variables
    elif token in variables:
        return variables[token]
    # Handle string literals
    elif (token.startswith('"') and token.endswith('"')) or (token.startswith("'") and token.endswith("'")):
        return token[1:-1]
    else:
        return token

def collect_block(lines, start_idx):
    """Collect lines between { and matching }"""
    block_lines = []
    brace_count = 0
    idx = start_idx
    found_opening = False
    
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
    
    while idx < len(lines) and brace_count > 0:
        line = lines[idx].strip()
        
        open_braces = line.count('{')
        close_braces = line.count('}')
        brace_count += open_braces - close_braces
        
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
        errorLine(lineNum, line)

    while i < len(tokens):
        negate = False

        if i < len(tokens) and tokens[i] == 'not':
            negate = True
            i += 1

        if i + 2 >= len(tokens):
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
            conditions.append(False)
        
        i += 3

        if i < len(tokens) and tokens[i] in ("and", "or"):
            operators.append(tokens[i])
            i += 1

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
    
    line = lines[current_idx].strip()
    tokens = re.findall(r'"[^"]*"|\'[^\']*\'|\[[^\]]*\]|-?\d+\.?\d*|<<|>>|<=|>=|==|!=|=<|=>|\w+|[=+*/()%<>{}:!@#$%^&-]', line)
    
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
    
    current_idx += 1
    
    # Collect all blocks and their conditions
    blocks = []
    executed_block = False
    
    # Collect the initial if block
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
    
    # Execute if block if condition is true
    if if_condition and not executed_block:
        execute_lines(if_block_lines, line_offset + 1)
        executed_block = True
    
    # Process else-if and else blocks
    while current_idx < len(lines) and not executed_block:
        line = lines[current_idx].strip()
        
        if line.startswith("} else"):
            else_part = line[1:].strip()
            else_tokens = re.findall(r'"[^"]*"|\'[^\']*\'|\[[^\]]*\]|-?\d+\.?\d*|<<|>>|<=|>=|==|!=|=<|=>|\w+|[=+*/()%<>{}:!@#$%^&-]', else_part)
            
            should_execute = False
            
            if len(else_tokens) > 1 and else_tokens[0] == "else" and else_tokens[1] == "if":
                # else if
                try:
                    paren_start = else_tokens.index("(")
                    paren_end = else_tokens.index(")")
                    condition_tokens = else_tokens[paren_start + 1:paren_end]
                    should_execute = parse_condition(condition_tokens, line_offset + current_idx + 1, line)
                except (ValueError, Exception):
                    errorLine(line_offset + current_idx + 1, line)
            elif len(else_tokens) >= 1 and else_tokens[0] == "else":
                # plain else - execute if no previous block executed
                should_execute = True
            
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
            
            # Execute this block if condition is true and no previous block executed
            if should_execute and not executed_block:
                execute_lines(block_lines, line_offset + current_idx - len(block_lines))
                executed_block = True
            
        elif line == "}":
            current_idx += 1
            break
        else:
            current_idx += 1
    
    # Skip any remaining else blocks if we already executed one
    while current_idx < len(lines):
        line = lines[current_idx].strip()
        if line == "}":
            current_idx += 1
            break
        elif line.startswith("} else"):
            # Skip this entire else block
            current_idx += 1
            brace_count = 1
            while current_idx < len(lines) and brace_count > 0:
                block_line = lines[current_idx].strip()
                if block_line.startswith("} else") or (block_line == "}" and brace_count == 1):
                    break
                brace_count += block_line.count('{') - block_line.count('}')
                current_idx += 1
        else:
            current_idx += 1
    
    return current_idx

def handle_list_operations(tokens, lineNum, line):
    """Handle built-in list operations"""
    command = tokens[0]
    
    # List creation: list mylist = [1,2,3]
    if command == "list" and len(tokens) >= 4 and tokens[2] == "=":
        list_name = tokens[1]
        list_value = get_val(tokens[3])
        if isinstance(list_value, list):
            variables[list_name] = list_value
            return True
        else:
            return False
    
    # List append: append mylist value
    elif command == "append" and len(tokens) >= 3:
        list_name = tokens[1]
        if list_name in variables and isinstance(variables[list_name], list):
            value = get_val(tokens[2])
            variables[list_name].append(value)
            return True
        return False
    
    # List prepend: prepend mylist value
    elif command == "prepend" and len(tokens) >= 3:
        list_name = tokens[1]
        if list_name in variables and isinstance(variables[list_name], list):
            value = get_val(tokens[2])
            variables[list_name].insert(0, value)
            return True
        return False
    
    # List remove by index: remove mylist 0
    elif command == "remove" and len(tokens) >= 3:
        list_name = tokens[1]
        if list_name in variables and isinstance(variables[list_name], list):
            try:
                index = get_val(tokens[2])
                if isinstance(index, int) and 0 <= index < len(variables[list_name]):
                    variables[list_name].pop(index)
                    return True
            except (ValueError, IndexError):
                pass
        return False
    
    # List insert: insert mylist index value
    elif command == "insert" and len(tokens) >= 4:
        list_name = tokens[1]
        if list_name in variables and isinstance(variables[list_name], list):
            try:
                index = get_val(tokens[2])
                value = get_val(tokens[3])
                if isinstance(index, int) and 0 <= index <= len(variables[list_name]):
                    variables[list_name].insert(index, value)
                    return True
            except (ValueError, IndexError):
                pass
        return False
    
    # List length: length mylist variable_name
    elif command == "length" and len(tokens) >= 3:
        list_name = tokens[1]
        result_var = tokens[2]
        if list_name in variables and isinstance(variables[list_name], list):
            variables[result_var] = len(variables[list_name])
            return True
        return False
    
    # List clear: clear mylist
    elif command == "clear" and len(tokens) >= 2:
        list_name = tokens[1]
        if list_name in variables and isinstance(variables[list_name], list):
            variables[list_name].clear()
            return True
        return False
    
    # List contains: contains mylist value result_var
    elif command == "contains" and len(tokens) >= 4:
        list_name = tokens[1]
        value = get_val(tokens[2])
        result_var = tokens[3]
        if list_name in variables and isinstance(variables[list_name], list):
            variables[result_var] = value in variables[list_name]
            return True
        return False
    
    # List index of: indexof mylist value result_var
    elif command == "indexof" and len(tokens) >= 4:
        list_name = tokens[1]
        value = get_val(tokens[2])
        result_var = tokens[3]
        if list_name in variables and isinstance(variables[list_name], list):
            try:
                variables[result_var] = variables[list_name].index(value)
            except ValueError:
                variables[result_var] = -1
            return True
        return False
    
    # List reverse: reverse mylist
    elif command == "reverse" and len(tokens) >= 2:
        list_name = tokens[1]
        if list_name in variables and isinstance(variables[list_name], list):
            variables[list_name].reverse()
            return True
        return False
    
    # List sort: sort mylist
    elif command == "sort" and len(tokens) >= 2:
        list_name = tokens[1]
        if list_name in variables and isinstance(variables[list_name], list):
            try:
                variables[list_name].sort()
                return True
            except TypeError:
                # Can't sort mixed types
                return False
        return False
    
    return False

def execute_lines(lines, start_line_offset=0):
    global lineNum
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        actual_line_num = start_line_offset + i + 1
        
        if line.startswith("#") or line.startswith("@") or not line:
            i += 1
            continue
        
        if line.startswith("} else"):
            i += 1
            continue
        
        command, args = slicer(line)
        if not command:
            i += 1
            continue
        
        tokens = [command] + args
        lineNum = actual_line_num
        
        try:
            # Handle built-in control structures first
            if command == "function" and len(tokens) >= 4 and tokens[2] == "(" and ")" in tokens and "{" in line:
                func_name = tokens[1]
                
                paren_start = tokens.index("(")
                paren_end = tokens.index(")")
                params = []
                for j in range(paren_start + 1, paren_end):
                    if tokens[j] != ",":
                        params.append(tokens[j])
                
                func_body, new_i = collect_block(lines, i)
                functions[func_name] = {'params': params, 'body': func_body}
                i = new_i
            
            elif command in functions:
                # Function call
                if len(tokens) >= 3 and tokens[1] == "(":
                    try:
                        paren_end = tokens.index(")")
                        args = []
                        for j in range(2, paren_end):
                            if tokens[j] != ",":
                                args.append(get_val(tokens[j]))
                        
                        if len(args) != len(functions[command]['params']):
                            errorLine(lineNum, line)
                        
                        saved_vars = variables.copy()
                        
                        for param, arg in zip(functions[command]['params'], args):
                            variables[param] = arg
                        
                        execute_lines(functions[command]['body'], start_line_offset)
                        
                        for var in list(variables.keys()):
                            if var in functions[command]['params']:
                                if var in saved_vars:
                                    variables[var] = saved_vars[var]
                                else:
                                    del variables[var]
                    except ValueError:
                        errorLine(lineNum, line)
                else:
                    errorLine(lineNum, line)
                i += 1
            
            elif command == "if" and "then" in tokens and "{" in line:
                i = parse_if_else_chain(lines, i, start_line_offset)
            
            elif line == "}" or line.startswith("} else"):
                i += 1
            
            else:
                # Try to load and execute modular command
                command_func = load_command(command)
                if command_func:
                    try:
                        success = command_func(tokens, variables, functions, get_val, errorLine, lineNum, line)
                        if not success:
                            errorLine(lineNum, line)
                    except Exception as e:
                        print(f"Error executing command {command}: {e}")
                        errorLine(lineNum, line)
                else:
                    print(f"DEBUG: Unknown command '{command}' on line {lineNum}")
                    errorLine(lineNum, line)
                i += 1
        
        except Exception as e:
            print(f"DEBUG: Unexpected error on line {lineNum}: {e}")
            errorLine(lineNum, line)

# Main execution
with open(filename, "r") as file:
    lines = [line.rstrip('\n\r') for line in file.readlines()]
    execute_lines(lines)