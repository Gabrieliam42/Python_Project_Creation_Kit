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

def ensure_virtualenv():
    if sys.prefix != sys.base_prefix:
        return
    activate_path = find_activate()
    if activate_path:
        print(f"Found activation script at: {activate_path}")
        venv_python = os.path.join(os.path.dirname(activate_path), "python")
        if not os.path.exists(venv_python):
            print("Python interpreter not found in the virtual environment.")
            input("Press Enter to exit...")
            sys.exit(1)
        print("Re-launching the script with the virtual environment's interpreter...")
        subprocess.run([venv_python] + sys.argv)
        input("Press Enter to exit...")
        sys.exit(0)
    else:
        print("No virtual environment activation script found in the current directory or its subdirectories.")
        input("Press Enter to exit...")
        sys.exit(1)

def select_and_run_py():
    py_files = [f for f in os.listdir('.') if f.endswith('.py') and os.path.isfile(f)]
    if not py_files:
        print("No Python files found in the current directory.")
        return

    print("Python files in the current directory:")
    for i, filename in enumerate(py_files, start=1):
        print(f"{i}. {filename}")

    try:
        choice = int(input("Select the number of the .py file you want to run: "))
        if choice < 1 or choice > len(py_files):
            print("Invalid selection.")
            return
    except ValueError:
        print("Please enter a valid number.")
        return

    selected_file = py_files[choice - 1]
    command = [sys.executable, selected_file]
    
    print(f"Executing command: {' '.join(command)}")
    subprocess.run(command)

if __name__ == "__main__":
    if not is_wsl():
        print("This script must be run inside WSL2. Exiting...")
        input("Press Enter to exit...")
        sys.exit(1)
    
    ensure_virtualenv()
    
    select_and_run_py()
