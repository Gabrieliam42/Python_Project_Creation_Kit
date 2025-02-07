import os
import subprocess
import sys

def is_wsl():
    try:
        with open("/proc/version", "r") as f:
            return "microsoft" in f.read().lower()
    except FileNotFoundError:
        return False

def create_virtualenv():
    cwd = os.getcwd()
    venv_path = os.path.join(cwd, ".venv")
    
    command = f"python3.10 -m venv {venv_path}"
    
    try:
        print(f"Creating virtual environment at: {venv_path}")
        subprocess.run(command, shell=True, check=True)
        print(f"Virtual environment '.venv' created successfully in {cwd}.")
        
        print("\nThe virtual environment is activated!")

        shell = os.environ.get("SHELL", "/bin/bash")
        subprocess.run(f"exec {shell} --rcfile {venv_path}/bin/activate", shell=True)

    except subprocess.CalledProcessError as e:
        print(f"Error while creating virtual environment: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if not is_wsl():
        print("This script must be run inside WSL2. Exiting...")
        sys.exit(1)
    
    create_virtualenv()
