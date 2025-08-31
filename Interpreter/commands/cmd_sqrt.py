# sqrt exampleVar exampleVar2
# sqrt exampleVar loud
import cmath

def run(tokens, variables, functions, get_val, errorLine, lineNum, line):
    if len(tokens) < 2 or len(tokens) > 3:
        return False

    try:
        # Get the actual value using get_val
        number = get_val(tokens[1])
        
        # Convert to number if it's a string
        if isinstance(number, str):
            if number.lstrip('-').replace('.', '').isdigit():
                number = float(number) if '.' in number else int(number)
            else:
                return False
        
        # Calculate square root
        square_root = cmath.sqrt(number)
        
        # Handle real numbers (remove tiny imaginary parts due to floating point)
        if isinstance(square_root, complex) and abs(square_root.imag) < 1e-10:
            square_root = square_root.real
            
        # Handle output based on number of arguments
        if len(tokens) == 2:
            # sqrt exampleVar - just calculate, don't output
            return True
        elif len(tokens) == 3:
            if tokens[2] == "loud":
                # sqrt exampleVar loud - print the result
                print(square_root)
            else:
                # sqrt exampleVar resultVar - store in variable
                variables[tokens[2]] = square_root
        
        return True

    except Exception as e:
        return False