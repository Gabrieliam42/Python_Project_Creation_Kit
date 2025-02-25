# Script Developer: Gabriel Mihai Sandu
# GitHub Profile: https://github.com/Gabrieliam42

import os
import sys
import ctypes
import tkinter as tk
from tkinter import filedialog
import subprocess

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
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
    return file_path

def convert_path_to_wsl_format(path):
    drive, rest = os.path.splitdrive(path)
    if drive:
        drive_letter = drive[0].lower()
        rest = rest.replace('\\', '/')
        return f"/mnt/{drive_letter}{rest}"
    return path

def run_python_file(file_path):
    wsl_path = convert_path_to_wsl_format(file_path)
    subprocess.run(['wsl', 'python3', wsl_path], stderr=subprocess.STDOUT, stdout=sys.stdout)

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
    run_python_file(selected_file)

if __name__ == "__main__":
    main()
