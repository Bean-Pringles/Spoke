import os
import subprocess

def set_up_virtual_environment():
    permission = input("Permission to install a Python virtual environment in the browser app? This is required to run. (Y/n) ")

    if permission.lower() != "n":
        # Use current working directory (where script was run from)
        base_path = os.getcwd()

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

        # Check if ensurepip is available
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

        # Install packages
        try:
            subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
            subprocess.run([pip_path, "install", "PyQt5", "PyQtWebEngine"], check=True)
            print("PyQt5 and PyQtWebEngine installed.")
        except subprocess.CalledProcessError as e:
            print(f"Error installing packages: {e}")
    else:
        print("Virtual environment installation was skipped.")

# Run it
set_up_virtual_environment()