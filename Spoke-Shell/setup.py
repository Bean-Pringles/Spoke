import os
import subprocess
import sys
import winreg
from pathlib import Path

def set_up_virtual_environment():
    permission = input("Permission to install a Python virtual environment in the browser app? This is required to run. (Y/n) ")

    if permission.lower() != "n":
        base_path = os.path.dirname(os.path.abspath(__file__))
        target_path = os.path.abspath(os.path.join(base_path, "apps", "browser"))
        venv_path = os.path.join(target_path, "venv")

        pip_path = os.path.join(venv_path, "Scripts" if os.name == "nt" else "bin", "pip")
        python_path = os.path.join(venv_path, "Scripts" if os.name == "nt" else "bin", "python")

        if not os.path.exists(target_path):
            print(f"Error: The path {target_path} does not exist.")
            return

        if not os.path.exists(venv_path):
            try:
                os.chdir(target_path)
                subprocess.run(["python", "-m", "venv", "venv"], check=True)
                print("Virtual environment created successfully.")
            except Exception as e:
                print(f"Error creating virtual environment: {e}")
                return
        else:
            print(f"Virtual environment already exists at: {venv_path}")

        try:
            result = subprocess.run([python_path, "-m", "ensurepip", "--version"],
                                    capture_output=True, text=True)
            if result.returncode == 0:
                subprocess.run([python_path, "-m", "ensurepip", "--upgrade"], check=True)
                print("pip installed or upgraded in virtual environment.")
            else:
                print("ensurepip is not available in this Python environment.")
                return
        except Exception as e:
            print(f"Error running ensurepip: {e}")
            return

        try:
            subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
            subprocess.run([pip_path, "install", "PyQt5", "PyQtWebEngine"], check=True)
            print("PyQt5 and PyQtWebEngine installed.")
        except subprocess.CalledProcessError as e:
            print(f"Error installing packages: {e}")
    else:
        print("Virtual environment installation was skipped.")

def add_to_user_path(new_path: str):
    permission = input("Permission to add the shell command to path? This is optional. (Y/n) ")

    if permission.lower() == "n":
        return
    
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_READ) as key:
            try:
                current_path, _ = winreg.QueryValueEx(key, "Path")
            except FileNotFoundError:
                current_path = ""
    except Exception as e:
        print(f"Error reading PATH from registry: {e}")
        return

    paths = current_path.split(";") if current_path else []
    if new_path in paths:
        print(f"Path already contains: {new_path}")
        return

    paths.append(new_path)
    updated_path = ";".join(paths)
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, updated_path)
        print(f"Added to PATH: {new_path}")
        print("You must restart CMD/PowerShell for changes to take effect.")
    except Exception as e:
        print(f"Error updating PATH in registry: {e}")

def install_shell_command():
    script_dir = Path(__file__).parent.resolve()
    shell_script = script_dir / "shell.py"
    if not shell_script.exists():
        print(f"shell.py not found at {shell_script}")
        return

    user_bin = Path.home() / "bin"
    user_bin.mkdir(exist_ok=True)
    bat_path = user_bin / "shell.bat"

    try:
        with open(bat_path, "w") as f:
            f.write(f"""@echo off
python "{shell_script}" %*
""")
        print(f"Created launcher: {bat_path}")
    except Exception as e:
        print(f"Error creating .bat file: {e}")
        return

    add_to_user_path(str(user_bin))

# Run both setup steps
set_up_virtual_environment()
install_shell_command()