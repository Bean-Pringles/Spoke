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

    if len(tokens) < 2:
        return False  # syntax error

    libs_to_import = tokens[1:]

    manifest_url = "https://raw.githubusercontent.com/Bean-Pringles/Spoke/main/import"

    try:
        resp = requests.get(manifest_url)
        resp.raise_for_status()
        manifest = resp.text.splitlines()
    except Exception:
        return False  # network/manifest error

    # Parse manifest into { library_name: [urls] }
    libraries = {}
    current_lib = None
    current_urls = []

    for line in manifest:
        line = line.strip()
        if not line:
            continue
        if line.startswith("&& "):
            if current_lib:
                libraries[current_lib] = current_urls
            current_lib = line[3:].strip()
            current_urls = []
        else:
            current_urls.append(line)

    if current_lib:
        libraries[current_lib] = current_urls

    commands_dir = Path("commands")
    commands_dir.mkdir(exist_ok=True)

    if "all" in libs_to_import:
        libs_to_import = list(libraries.keys())

    # Collect missing files
    missing_files = []
    for lib in libs_to_import:
        if lib not in libraries:
            continue
        for url in libraries[lib]:
            filename = url.split("/")[-1]

            # Prevent double cmd_cmd_ bug
            if not filename.startswith("cmd_"):
                filename = f"cmd_{filename}"

            filepath = commands_dir / filename
            if not filepath.exists():
                missing_files.append((filename, url))

    if missing_files:
        # Bulk confirmation (defaults to YES)
        print("The following commands are missing and will be installed:")
        for filename, url in missing_files:
            print(f" - {filename} ({url})")
        confirm = input("Proceed with installation? [Y/n]: ").strip().lower()

        if confirm not in ("n", "no"):
            installed = []
            for filename, url in missing_files:
                try:
                    filepath = commands_dir / filename
                    r = requests.get(url)
                    r.raise_for_status()
                    filepath.write_text(r.text, encoding="utf-8")
                    installed.append(filename)
                except Exception:
                    print(f"Error installing {filename} from {url}")
                    return False  # only fail if a download fails
            if installed:
                print("Installed:", ", ".join(installed))
        else:
            print("Installation skipped.")

    return True  # always succeed unless a real error