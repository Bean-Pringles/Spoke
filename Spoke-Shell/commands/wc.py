import os
import collections

def run(args):
    if not args:
        print("Usage: wc <file>")
        return

    fileName = args[0]

    try:
        with open(fileName, 'r') as file:
            content = file.read()

        # Word count
        word_count = collections.Counter(content.split())
        wordCount = sum(word_count.values())
        print(f"Words: {wordCount}")

        # Byte count
        file_size_bytes = os.path.getsize(fileName)
        print(f"Bytes: {file_size_bytes}")

        # Line count
        num_lines = content.count('\n') + (1 if content and not content.endswith('\n') else 0)
        print(f"Lines: {num_lines}")

    except FileNotFoundError:
        print("File not found")
    except OSError as e:
        print(f"An error occurred: {e}")
