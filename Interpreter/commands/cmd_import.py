import requests
from pathlib import Path

def run(tokens, variables, functions, get_val, errorLine, lineNum, line):
    """
    Command: import
    Usage: import <lib1> <lib2> ...
           import all
    Downloads missing .py files for listed libraries from GitHub manifest
    into the commands folder. Skips files that already exist.
    """

    # must have at least "import X"
    if len(tokens) < 2:
        return False

    libs_to_import = tokens[1:]

    # GitHub raw URL to the import manifest
    manifest_url = "https://raw.githubusercontent.com/Bean-Pringles/Spoke/main/import"

    try:
        resp = requests.get(manifest_url)
        resp.raise_for_status()
        manifest = resp.text.splitlines()
    except Exception:
        # fail silently if manifest can't be read
        return False

    # Parse manifest into library → file URLs
    libraries = {}
    current_lib = None
    current_urls = []

    for line in manifest:
        line = line.strip()
        if not line:
            continue
        if line.startswith("&& "):  # start of a new library section
            if current_lib:
                libraries[current_lib] = current_urls
            current_lib = line[3:].strip()
            current_urls = []
        else:
            current_urls.append(line)

    if current_lib:
        libraries[current_lib] = current_urls

    # Ensure commands directory exists
    commands_dir = Path("commands")
    commands_dir.mkdir(exist_ok=True)

    # Special case: import all → load every library
    if "all" in libs_to_import:
        libs_to_import = list(libraries.keys())

    # Download all requested libraries
    for lib in libs_to_import:
        if lib not in libraries:
            continue
        for url in libraries[lib]:
            try:
                filename = url.split("/")[-1]
                filepath = commands_dir / filename
                #Skip if already exists
                if filepath.exists():
                    continue
                r = requests.get(url)
                r.raise_for_status()
                filepath.write_text(r.text, encoding="utf-8")
            except Exception:
                # fail silently if one file doesn't load
                pass

    return True