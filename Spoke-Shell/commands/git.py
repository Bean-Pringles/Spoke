import os
import hashlib
import shutil
import json
import argparse
import sys
import zipfile
import tempfile
import urllib.request

# Constants
script_dir = os.path.dirname(os.path.abspath(__file__))
backup_root = os.path.join(script_dir, "backups")

def get_checksum(path):
    hasher = hashlib.sha1()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def get_project_name(path):
    return os.path.basename(os.path.abspath(path))

def get_checksum_file(project_name):
    return os.path.join(backup_root, project_name, ".checksums.json")

def load_checksums(project_name):
    checksum_file = get_checksum_file(project_name)
    if not os.path.exists(checksum_file):
        return {}
    with open(checksum_file, "r") as f:
        return json.load(f)

def save_checksums(project_name, checksums):
    project_backup_dir = os.path.join(backup_root, project_name)
    os.makedirs(project_backup_dir, exist_ok=True)
    with open(get_checksum_file(project_name), "w") as f:
        json.dump(checksums, f, indent=2)

def find_changed_files(base_dir, old_checksums):
    changed_files = []
    current_checksums = {}

    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.startswith(".") or backup_root in root:
                continue
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, base_dir)
            checksum = get_checksum(full_path)
            current_checksums[rel_path] = checksum
            if rel_path not in old_checksums or old_checksums[rel_path] != checksum:
                changed_files.append(rel_path)

    return changed_files, current_checksums

def backup_files(files, base_dir, version_dir):
    for file in files:
        src = os.path.join(base_dir, file)
        dst = os.path.join(version_dir, file)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        print(f"Backed up {file} -> {dst}")

def comment_save(comment, version_dir, version):
    os.makedirs(version_dir, exist_ok=True)
    comment_path = os.path.join(version_dir, "comment.txt")
    with open(comment_path, "w", encoding="utf-8") as f:
        f.write(f"Version: {version}\n")
        f.write(f"Comment: {comment}\n")

def update_current_folder(files, base_dir):
    project_name = get_project_name(base_dir)
    current_dir = os.path.join(backup_root, project_name, "current")
    for file in files:
        src = os.path.join(base_dir, file)
        dst = os.path.join(current_dir, file)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)

def clone_from_github(repo_url, dest_path):
    if not repo_url.endswith(".git"):
        print("Error: GitHub URL must end with '.git'")
        return

    # Convert GitHub repo URL to zip URL
    repo_url = repo_url.rstrip(".git")
    zip_url = repo_url.replace("github.com", "codeload.github.com") + "/zip/refs/heads/main"

    print(f"Downloading ZIP from: {zip_url}")
    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            zip_path = os.path.join(tmp_dir, "repo.zip")
            urllib.request.urlretrieve(zip_url, zip_path)

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(tmp_dir)

            # Find extracted folder (usually <repo>-main)
            extracted_name = os.listdir(tmp_dir)[1]  # skip repo.zip
            extracted_path = os.path.join(tmp_dir, extracted_name)

            # Copy to destination
            shutil.copytree(extracted_path, dest_path, dirs_exist_ok=True)
            print(f"Cloned into: {dest_path}")
    except Exception as e:
        print(f"Failed to clone: {e}")

def commit(base_dir, version, comment):
    project_name = get_project_name(base_dir)
    old_checksums = load_checksums(project_name)
    changed_files, new_checksums = find_changed_files(base_dir, old_checksums)

    if not changed_files:
        print("No changes detected. Nothing to commit.")
        return

    print(f"Committing version {version} with comment: {comment}")
    version_dir = os.path.join(backup_root, project_name, version)
    backup_files(changed_files, base_dir, version_dir)
    update_current_folder(changed_files, base_dir)
    save_checksums(project_name, new_checksums)
    comment_save(comment, version_dir, version)
    print(f"Commit complete: {len(changed_files)} file(s) backed up.")

def parse_version(version):
    return tuple(map(int, version.split(".")))

def get_sorted_version_folders(path):
    folders = [
        f for f in os.listdir(path)
        if os.path.isdir(os.path.join(path, f)) and all(part.isdigit() for part in f.split("."))
    ]
    return sorted(folders, key=parse_version)

def pull_current_version(project_path):
    project_name = get_project_name(project_path)
    pull_path = os.path.join(backup_root, project_name, "current")

    if not os.path.exists(pull_path):
        print(f"No current backup found for project '{project_name}'.")
        return

    # Clean the project folder (but not the backups folder)
    for item in os.listdir(project_path):
        item_path = os.path.join(project_path, item)
        if item == "backups":
            continue
        try:
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
        except Exception as e:
            print(f"Failed to delete {item_path}: {e}")

    # Copy files from current/ into project folder
    for root, _, files in os.walk(pull_path):
        rel_path = os.path.relpath(root, pull_path)
        dest_dir = os.path.join(project_path, rel_path)
        os.makedirs(dest_dir, exist_ok=True)
        for file in files:
            src_file = os.path.join(root, file)
            dst_file = os.path.join(dest_dir, file)
            shutil.copy2(src_file, dst_file)

    print(f"Pulled current version into: {project_path}")

def pull_restore_version(project_path, version):
    project_name = get_project_name(project_path)
    project_versions_path = os.path.join(backup_root, project_name)

    if not os.path.exists(project_versions_path):
        print(f"No versions found for project '{project_name}'.")
        return

    sorted_versions = get_sorted_version_folders(project_versions_path)
    target_version = parse_version(version)

    # Filter versions up to and including the target
    versions_to_apply = [
        v for v in sorted_versions if parse_version(v) <= target_version
    ]

    if not versions_to_apply:
        print(f"No applicable versions found up to '{version}'.")
        return

    print(f"Restoring full project state from versions up to: {version}")
    
    # Clean the current project folder
    for item in os.listdir(project_path):
        item_path = os.path.join(project_path, item)
        if item == "backups":
            continue
        try:
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
        except Exception as e:
            print(f"Failed to delete {item_path}: {e}")

    # Dict to track latest version and source path for each file
    restored_files = {}  # rel_path -> (version, full_file_path)

    for ver in versions_to_apply:
        version_dir = os.path.join(project_versions_path, ver)
        for root, _, files in os.walk(version_dir):
            rel_path = os.path.relpath(root, version_dir)
            for file in files:
                if file == "comment.txt":
                    continue
                file_rel = os.path.normpath(os.path.join(rel_path, file))
                full_path = os.path.join(root, file)
                # Always take latest version in list
                restored_files[file_rel] = (ver, full_path)

    # Apply latest version of each file
    for rel_path, (ver, src_file) in restored_files.items():
        dst_file = os.path.join(project_path, rel_path)
        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
        shutil.copy2(src_file, dst_file)

    print(f"\n Restored {len(restored_files)} file(s):\n")
    for rel_path, (ver, _) in sorted(restored_files.items()):
        print(f"  - {rel_path} (from version {ver})")

    print(f"\nProject restored to full state as of version {version}.")

def clone_repo(source_path, dest_path):
    source_path = os.path.abspath(source_path)
    dest_path = os.path.abspath(dest_path)

    if not os.path.exists(source_path):
        print(f"Source path does not exist: {source_path}")
        return

    print(f"Cloning from local path: {source_path} -> {dest_path}")
    shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
    print(f"Cloned project into: {dest_path}")

def run(args_list=None):
    valid_commands = ["push", "version", "pull", "restore", "clone"]

    if args_list is None:
        args_list = sys.argv[1:]

    if not args_list or args_list[0] not in valid_commands:
        print(f"Invalid command: '{args_list[0]}'" if args_list else "No command provided.")
        print("Available commands: push, version, pull, restore, clone")
        return

    parser = argparse.ArgumentParser(description="BeanGit: simple versioned backup tool")
    parser.add_argument("command", choices=valid_commands, help="Command to run")
    parser.add_argument("version_or_comment", nargs="?", help="Version string or version command")
    parser.add_argument("comment", nargs="*", help="Commit comment (for push only)")
    parser.add_argument("-p", "--path", default=os.getcwd(), help="Path to project folder (default: current directory)")
    args = parser.parse_args(args_list)

    project_path = os.path.abspath(args.path)
    project_name = get_project_name(project_path)

    if args.command == "push":
        if not args.version_or_comment or not args.comment:
            print("Error: push requires a version and comment.")
            return
        version = args.version_or_comment
        comment = " ".join(args.comment)
        commit(project_path, version, comment)

    elif args.command == "version":
        version_path = os.path.join(backup_root, project_name)
        if not os.path.exists(version_path):
            print(f"No versions found for {project_name}")
            return
        versions = get_sorted_version_folders(version_path)
        if versions:
            print("Available versions (oldest → newest):")
            for v in versions:
                print("  -", v)
            print("Latest version:", versions[-1])
        else:
            print("No valid versions found.")

    elif args.command == "pull":
        pull_current_version(project_path)

    elif args.command == "restore":
        if not args.version_or_comment:
            print("Error: restore requires a version number.")
            return
        pull_restore_version(project_path, args.version_or_comment)

    elif args.command == "clone":
        if not args.version_or_comment:
            print("Error: clone requires source URL or path.")
            return
        source = args.version_or_comment
        destination = args.path
        if source.startswith("http"):
            clone_from_github(source, destination)
        else:
            clone_repo(source, destination)
