# Script Developer: Gabriel Mihai Sandu
# GitHub Profile: https://github.com/Gabrieliam42

import os
import sys
import subprocess

def is_wsl():
    """Check if the script is running inside WSL by looking for 'microsoft' in /proc/version."""
    try:
        with open("/proc/version", "r") as f:
            return "microsoft" in f.read().lower()
    except FileNotFoundError:
        return False

def select_and_run_py():
    """List .py files in the current directory, let the user choose one, and execute it."""
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

def stay_open():
    """Keep the shell open after execution, similar to 'cmd /k'."""
    print("\nExecution finished.")
    os.system("bash -i")

def main():
    if not is_wsl():
        print("This script must be run inside WSL2. Exiting...")
        input("Press Enter to exit...")
        sys.exit(1)

    select_and_run_py()
    stay_open()

if __name__ == "__main__":
    main()
