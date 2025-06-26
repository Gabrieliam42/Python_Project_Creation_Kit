# Script Developer: Gabriel Mihai Sandu
# GitHub Profile: https://github.com/Gabrieliam42

import os
import subprocess
import platform
import winreg
import ctypes
import sys
import re

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    params = " ".join([f'"{arg}"' for arg in sys.argv])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)

def update_environment_variable(variable_name, new_value, scope):
    try:
        with winreg.OpenKey(scope, r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 0, winreg.KEY_ALL_ACCESS) as key:
            try:
                value, regtype = winreg.QueryValueEx(key, variable_name)
                value_list = value.split(os.pathsep)
            except FileNotFoundError:
                value_list = []
                regtype = winreg.REG_EXPAND_SZ

            # Remove existing instances with or without trailing slashes
            value_list = [v for v in value_list if v.rstrip('\\') != new_value.rstrip('\\')]

            # Add new value to the beginning
            value_list.insert(0, new_value)
            new_value_str = os.pathsep.join(value_list)
            winreg.SetValueEx(key, variable_name, 0, regtype, new_value_str)
            print(f"Updated {variable_name} in system variables with: {new_value}")
    except PermissionError:
        print("Permission denied while updating registry. Run as administrator.")

def get_anaconda_versions(base_path):
    anaconda_versions = []
    for folder in os.listdir(base_path):
        if folder.lower().startswith("anaconda") and folder != "anaconda3":
            anaconda_versions.append(folder)
    return anaconda_versions

if __name__ == "__main__":
    if not is_admin():
        print("Requesting administrative privileges...")
        run_as_admin()
        sys.exit()

    base_path = r"C:\ProgramData"
    new_path = r"C:\ProgramData\anaconda3"
    new_path_scripts = os.path.join(new_path, 'Scripts')

    update_environment_variable('Path', new_path_scripts, winreg.HKEY_LOCAL_MACHINE)
    update_environment_variable('Path', new_path, winreg.HKEY_LOCAL_MACHINE)

    # Detect other Anaconda installations (excluding anaconda3)
    other_anacondas = get_anaconda_versions(base_path)
    print("Detected other Anaconda versions (excluding anaconda3):", other_anacondas)

    print("Anaconda3 has been registered as the system Python environment.")

    if platform.system() == 'Windows':
        subprocess.run(['cmd', '/k', 'echo Anaconda system registration complete.'], shell=True)
