import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_FILE = os.path.join(BASE_DIR, "notes.txt")

def run(args):
    if not args:
        print("Usage: notes <add, done, list, clear>")
        return

    cmd = args[0]

    if cmd == "add":
        if len(args) < 2:
            print("Usage: notes add <note>")
            return
        note = " ".join(args[1:])
        with open(NOTES_FILE, "a", encoding="utf-8") as file:
            file.write(note + "\n")
        print(f"Added note: {note}")

    elif cmd == "list":
        if not os.path.exists(NOTES_FILE):
            print("No notes found.")
            return
        with open(NOTES_FILE, "r", encoding="utf-8") as file:
            lines = file.readlines()
            if not lines:
                print("No notes found.")
                return
            for i, line in enumerate(lines, 1):
                print(f"{i}. {line.strip()}")

    elif cmd == "done":
        if len(args) < 2:
            print("Usage: notes done <note number>")
            return
        try:
            num = int(args[1])
            with open(NOTES_FILE, "r", encoding="utf-8") as file:
                lines = file.readlines()
            if 1 <= num <= len(lines):
                removed = lines.pop(num - 1)
                with open(NOTES_FILE, "w", encoding="utf-8") as file:
                    file.writelines(lines)
                print(f"Marked done: {removed.strip()}")
            else:
                print("Invalid note number.")
        except ValueError:
            print("Please enter a valid note number.")
        except Exception as e:
            print(f"Error: {e}")

    elif cmd == "clear":
        try:
            open(NOTES_FILE, "w").close()
            print("Cleared all notes.")
        except IOError as e:
            print(f"Error clearing notes: {e}")

    else:
        print(f"Unknown command: {cmd}")