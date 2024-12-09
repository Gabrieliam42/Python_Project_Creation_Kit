import os
import subprocess
import sys

def check_sudo():
    """Check if the script is running with sudo privileges."""
    if os.geteuid() != 0:
        print("This script must be run as root. Please re-run with 'sudo'.")
        sys.exit(1)

def create_virtualenv():
    """Create a Python 3.10 virtual environment in the current working directory."""
    cwd = os.getcwd()
    venv_path = os.path.join(cwd, ".venv")
    command = f"python3.10 -m venv {venv_path}"
    try:
        print(f"Creating virtual environment at: {venv_path}")
        subprocess.run(command, shell=True, check=True)
        print(f"Virtual environment '.venv' created successfully in {cwd}.")
    except subprocess.CalledProcessError as e:
        print(f"Error while creating virtual environment: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_sudo()
    create_virtualenv()
