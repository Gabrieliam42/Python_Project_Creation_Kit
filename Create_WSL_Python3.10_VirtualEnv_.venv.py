# Script Developer: Gabriel Mihai Sandu
# GitHub Profile: https://github.com/Gabrieliam42

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
    # Use the Linux native home directory
    home_dir = os.path.expanduser("~")
    venv_path = os.path.join(home_dir, ".venv")
    
    # Modified command to use /usr/bin/python3.10 with --system-site-packages
    command = f"/usr/bin/python3.10 -m venv --system-site-packages {venv_path}"
    
    try:
        print(f"Creating virtual environment at: {venv_path}")
        subprocess.run(command, shell=True, check=True)
        print("Virtual environment '.venv' created successfully.")
        
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
