import time

def run(tokens, variables, functions, get_val, errorLine, lineNum, line):
    """
    Countdown command: countdown seconds [message]
    Counts down from the specified number and optionally prints a message
    """
    if len(tokens) in (2, 3):
        try:
            count_countdown = int(get_val(tokens[1]))
            for count_repeats in range(count_countdown):
                print(count_countdown - count_repeats)
                time.sleep(1)
                
            if len(tokens) == 3:
                print(tokens[2])
            return True
        except ValueError:
            print("Invalid countdown value")
            return False
    else:
        return False