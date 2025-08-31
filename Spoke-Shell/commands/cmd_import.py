import requests
from pathlib import Path
import os

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

    def convert_to_raw_url(url):
        """Convert GitHub URLs to raw content URLs"""
        if "github.com" in url and "/blob/" in url:
            # Convert github.com/user/repo/blob/branch/file to raw.githubusercontent.com/user/repo/branch/file
            parts = url.replace("https://github.com/", "").split("/")
            if len(parts) >= 4 and parts[2] == "blob":
                user = parts[0]
                repo = parts[1]
                branch = parts[3]
                file_path = "/".join(parts[4:])
                return f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{file_path}"
        return url  # Return original URL if not a GitHub blob URL

    # Collect missing files
    missing_files = []
    for lib in libs_to_import:
        if lib not in libraries:
            continue
        for url in libraries[lib]:
            # Convert to raw URL if it's a GitHub blob URL
            raw_url = convert_to_raw_url(url)
            filename = raw_url.split("/")[-1]

            # Prevent double cmd_cmd_ bug
            if not filename.startswith("cmd_"):
                filename = f"cmd_{filename}"

            filepath = commands_dir / filename
            if not filepath.exists():
                missing_files.append((filename, raw_url))

    if missing_files:
        # Bulk confirmation (defaults to YES)
        print("The following commands are missing and will be installed:")
        for filename, url in missing_files:
            print(f" - {filename}")
        confirm = input("Proceed with installation? [Y/n]: ").strip().lower()

        if confirm not in ("n", "no"):
            installed = []
            for filename, url in missing_files:
                try:
                    filepath = commands_dir / filename
                    r = requests.get(url)
                    r.raise_for_status()
                    
                    # Verify we got actual Python code, not HTML
                    content = r.text
                    if content.strip().startswith("<!DOCTYPE html") or content.strip().startswith("<html"):
                        print(f"Error: {filename} - Got HTML instead of Python code from {url}")
                        continue
                    
                    filepath.write_text(content, encoding="utf-8")
                    installed.append(filename)
                except Exception as e:
                    print(f"Error installing {filename} from {url}: {e}")
                    continue  # Continue with other files instead of failing completely
            
            if installed:
                print("Installed:", ", ".join(installed))
        else:
            print("Installation skipped.")

    if os.name == 'nt':  # For Windows
        _ = os.system('cls')
    else:  # For Linux and macOS
        _ = os.system('clear')
    
    return True  # always succeed unless a real error