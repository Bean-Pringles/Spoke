***Please Report Any Issues You Find In Anything, God Bless Open Source :D***
Spoke Overview
This scripting engine supports custom logic, variables, math operations, conditionals, functions, and utility commands like printing, input, time, and randomness.

How to run
To run Spoke, you must navigate to your spoke.py in the terminal and run:

python spoke.py exampleScript.spk*

*spk files are just txt files saved as spk, thought this would be fun.

Core Rules
All commands are line-based.

Variables must be declared using let before use.

Blocks must be enclosed in {} following an if, else if, or else statement.

Strings must be wrapped in either " or '.

Variable names should be alphanumeric and case-sensitive.

All errors halt execution.

Comments
Use either # or @ at the beggining of the line to comment it out
It can not be any where at the line except for the beggining

Variable Commands
let
Syntax:

let x = 5

let z = a + b

Stores a value or a math expression into a variable.

delete
Syntax:

delete x

Deletes a variable.

swap
Syntax:

swap x y

Swaps values between two variables.

toggle
Syntax:

toggle x

Toggles a boolean or binary value:

0 ⇄ 1

"true" ⇄ "false"

length
Syntax:

length varname loud

length varname loud resultvar

Measures string length of a variable. Optional output variable.

shuffle
Syntax:

shuffle varname

shuffle varname loud

shuffle varname loud resultvar

Randomizes characters in a string. Optionally prints or stores result.

Math Commands
math
Syntax:

math a + b

math a * b silent

math a / b loud resultvar

Performs arithmetic operations:

+, -, *, /, %

Comparison Commands
compare
Syntax:

compare x y

compare x y loud

Compares values:

Outputs: Equal, Greater Than, Less Than

Optional loud gives detailed messages.

Control Flow
if, else if, else
Syntax:

plaintext
Copy
Edit
if (x == y and not z >> 5) then {
    print (Match)
} else if (x != y) then {
    print (Mismatch)
} else {
    print (Fallback)
}
Supports:

Operators: ==, !=, <<, >>, <=, >=, =<, =>

Logic: and, or, not

function
Syntax:

plaintext
Copy
Edit
function greet(name) {
    print (Hello)
    print name
}
Call with:

plaintext
Copy
Edit
greet("Alice")
Functions support parameters and local variable scope.

Input/Output
print
Syntax:

print x (prints variable)

print ("Message" var "more") (prints message and values)

input
Syntax:

input name

input age Enter your age:

Prompts for user input.

pause
Syntax:

pause

pause silent

pause loud "Message"

Waits for user keypress, optionally with message.

Time & Random
time
Syntax:

time

time varname

Prints or stores current system time.

sleep
Syntax:

sleep 3

Pauses execution for given seconds.

countdown
Syntax:

countdown 5

countdown 3 Go!

Counts down with optional message.

random
Syntax:

random (1, 10) varname

random (1, 10) varname loud

Generates random integer in range.

System Control
clear
Syntax:

clear

Clears the screen (platform-dependent).

quit
Syntax:

quit loud

quit silent

Exits the program. Loud shows exit message.

Error Handling
errorLine(lineNum, line) is called when syntax is invalid.

Most commands check token count and variable existence.

Undefined variables, invalid arguments, or malformed expressions stop execution.

Best Practices
Always declare variables using let before use.

Wrap string literals in quotes ("Hello" or 'Hi').

Use print (message) for readable output.

Use silent/loud modifiers to control terminal output.

Avoid using the same name for function and variable.

***Written with ChatGBT (The readme, not the interpreter) because its 2:30 pm and I am done with this. Hopefully the IDE will come soon.***
