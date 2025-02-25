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

def find_activate():
    cwd = os.getcwd()
    for root, dirs, files in os.walk(cwd):
        if 'bin' in dirs:
            activate_path = os.path.join(root, 'bin', 'activate')
            if os.path.isfile(activate_path):
                return activate_path
    return None

def activate_virtualenv():
    activate_path = find_activate()
    if activate_path:
        print(f"Found activation script at: {activate_path}")
        shell = os.environ.get("SHELL", "/bin/bash")
        subprocess.run(f"exec {shell} --rcfile {activate_path}", shell=True)
    else:
        print("No virtual environment activation script found in the current directory or its subdirectories.")
        sys.exit(1)

if __name__ == "__main__":
    if not is_wsl():
        print("This script must be run inside WSL2. Exiting...")
        sys.exit(1)
    
    activate_virtualenv()
