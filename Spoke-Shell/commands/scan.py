import os
import ast
import sys
import importlib.util

def run(args):
    if "-h" in args or "--help" in args:
        print("Usage:")
        print("  scan               - List external imports in current folder")
        print("  scan output.txt    - Save results to output.txt")
        return

    output_to_file = len(args) > 0
    file_path = args[0] if output_to_file else None

    def find_imports_in_file(filepath):
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            try:
                tree = ast.parse(f.read(), filename=filepath)
            except SyntaxError:
                return set()

        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.add(name.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])
        return imports

    def is_builtin_or_stdlib(module_name):
        try:
            if module_name == '__main__':
                return True
            spec = importlib.util.find_spec(module_name)
            if spec is None:
                return False
            origin = spec.origin or ''
            return "site-packages" not in origin and "dist-packages" not in origin
        except (ModuleNotFoundError, ValueError, AttributeError):
            return False

    all_imports = set()
    for root, _, files in os.walk(os.getcwd()):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                all_imports.update(find_imports_in_file(path))

    external_modules = sorted([
        mod for mod in all_imports
        if not is_builtin_or_stdlib(mod) and mod not in sys.builtin_module_names
    ])

    if output_to_file:
        with open(file_path, 'w') as f:
            for mod in external_modules:
                f.write(f"{mod}\n")
    else:
        for mod in external_modules:
            print(f"{mod}")