import os
import sys
import ctypes
import tkinter as tk
from tkinter import filedialog
import subprocess
import platform

def get_current_directory():
    return os.getcwd()

def check_admin_privileges():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def run_as_admin(script, params):
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)

def select_python_file():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
    return file_path

def find_and_activate_venv():
    # Get the current working directory
    cwd = os.getcwd()
    
    # Walk through the current directory and its subdirectories
    for root, dirs, files in os.walk(cwd):
        # Check if the directory contains a virtual environment
        if 'Scripts' in dirs or 'bin' in dirs:
            scripts_path = os.path.join(root, 'Scripts' if platform.system() == 'Windows' else 'bin')
            required_files = {'activate.bat' if platform.system() == 'Windows' else 'activate'}
            
            # Check if the required activation file is present in the Scripts/bin directory
            if required_files.issubset(set(os.listdir(scripts_path))):
                print(f"Virtual environment found at: {root}")
                
                # Return the activation script path
                return os.path.join(scripts_path, 'activate.bat' if platform.system() == 'Windows' else 'activate')

    print("No virtual environment found.")
    return None

def run_python_file(file_path):
    subprocess.run(['python', file_path], stderr=subprocess.DEVNULL)

def main():
    cwd = get_current_directory()
    print(f"Current working directory: {cwd}")

    if not check_admin_privileges():
        print("Script is not running with admin privileges. Restarting with admin privileges...")
        run_as_admin(__file__, "")
        return

    py_files = []
    for root, dirs, files in os.walk(cwd):
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(root, file))

    if not py_files:
        print("No .py files found in the current directory or its subdirectories.")
        return

    selected_file = select_python_file()
    if not selected_file:
        print("No file selected.")
        return

    activate_script = find_and_activate_venv()
    if activate_script:
        activate_command = f'cmd /k ""{activate_script}" && python "{selected_file}""' if platform.system() == 'Windows' else f'source "{activate_script}" && python3 "{selected_file}"'
        subprocess.run(activate_command, shell=True, executable='/bin/bash' if platform.system() != 'Windows' else None)
    else:
        subprocess.run(f'cmd /k ""python "{selected_file}""', shell=True, stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    main()
