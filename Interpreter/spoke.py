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
    tokens = re.findall(r'"[^"]*"|\'[^\']*\'|-?\d+\.?\d*|<<|>>|<=|>=|==|!=|=<|=>|\w+|[=+*/()%<>{}:!@#$%^&-]', line)
    if not tokens:
        return None, []
    
    command = tokens[0]
    args = tokens[1:]
    return command, args

commands_dir = Path("commands")

def load_command(command_name):
    """Dynamically load and execute a command from the commands folder"""
    command_path = commands_dir / f"{command_name}.py"
    
    if not command_path.exists():
        return None

    try:
        # Load by file path, not by package name (avoids stdlib conflicts)
        spec = importlib.util.spec_from_file_location(f"spoke_commands.{command_name}", command_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[f"spoke_commands.{command_name}"] = module
        spec.loader.exec_module(module)

        if hasattr(module, "run"):
            return module.run
        else:
            print(f"Error: {command_name}.py missing 'run' function")
            return None
    except Exception as e:
        print(f"Error loading command {command_name}: {e}")
        return None

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
    if token.lstrip('-').replace('.', '').isdigit():
        if '.' in token:
            return float(token)
        return int(token)
    elif token in variables:
        return variables[token]
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
            else_tokens = re.findall(r'"[^"]*"|\'[^\']*\'|-?\d+\.?\d*|<<|>>|<=|>=|==|!=|=<|=>|\w+|[=+*/()%<>{}:!@#$%^&-]', else_part)
            
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