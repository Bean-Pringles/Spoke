import os
import subprocess
import tempfile

try:
    from rich.syntax import Syntax
    from rich.console import Console
    console = Console()
    rich_available = True
except ImportError:
    rich_available = False
    console = None

from prompt_toolkit import prompt

def run(args):
    if not args:
        print("Usage: edit <python or spoke>")
        return

    language = args[0].lower()
    if language not in ["python", "spoke"]:
        print("Supported modes: python, spoke")
        return

    print(f"\n[Terminal Code Editor - {language.upper()} Mode]")
    print("Type your code below.")
    print("Commands: ':run' to execute, ':save filename' to save, ':open filename' to open, ':exit' to cancel.\n")

    lines = []
    shared_globals = {}
    line_number = 1

    while True:
        try:
            indent = "    " if lines and lines[-1].strip().endswith(":") else ""
            user_input = prompt(f"{line_number:03} >>> {indent}")
            line = indent + user_input if indent and not user_input.startswith(indent) else user_input
        except KeyboardInterrupt:
            print("\nExiting editor.")
            return
        except EOFError:
            print("\nExiting editor.")
            return

        stripped = line.strip()

        if stripped == ":exit":
            print("Editor closed without saving.")
            return

        elif stripped == ":run":
            code = "\n".join(lines)
            print("\n[Code Preview:]\n")
            if rich_available:
                syntax = Syntax(code, language, theme="monokai", line_numbers=True)
                console.print(syntax)
            else:
                print(code)

            print("\n[Running code...]\n")

            if language == "python":
                # Run Python code with exec()
                try:
                    exec(code, shared_globals)
                except Exception as e:
                    print(f"Error executing Python code: {e}")

            elif language == "spoke":
                # Run Spoke code via interpreter one folder up from this file
                current_dir = os.path.dirname(os.path.abspath(__file__))
                parent_dir = os.path.dirname(current_dir)
                spoke_interpreter_path = os.path.join(parent_dir, "spoke.py")

                with tempfile.NamedTemporaryFile(suffix=".spk", mode="w", encoding="utf-8", delete=False) as tmpfile:
                    tmpfile.write(code)
                    tmpfile_path = tmpfile.name

                try:
                    result = subprocess.run(
                        ["python", spoke_interpreter_path, tmpfile_path],
                        capture_output=True,
                        text=True
                    )
                    print(result.stdout)
                    if result.stderr:
                        print("Errors:\n", result.stderr)
                except Exception as e:
                    print(f"Error running Spoke interpreter: {e}")
                finally:
                    try:
                        os.unlink(tmpfile_path)
                    except Exception:
                        pass

            print("\n[Editor resumed. Continue typing or :exit]\n")
            continue

        elif stripped.startswith(":save "):
            filename = stripped[6:].strip()
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines))
                print(f"Saved to {filename}")
            except Exception as e:
                print(f"Save failed: {e}")
            continue

        elif stripped.startswith(":open "):
            filename = stripped[6:].strip()
            if os.path.isfile(filename):
                try:
                    with open(filename, "r", encoding="utf-8") as f:
                        file_lines = f.read().splitlines()
                    lines = file_lines
                    line_number = len(lines) + 1
                    print(f"Opened {filename}")
                    if rich_available:
                        syntax = Syntax("\n".join(lines), language, theme="monokai", line_numbers=True)
                        console.print(syntax)
                    else:
                        print("\n".join(lines))
                except Exception as e:
                    print(f"Open failed: {e}")
            else:
                print(f"File not found: {filename}")
            continue

        # Add code line
        lines.append(line)
        line_number += 1
