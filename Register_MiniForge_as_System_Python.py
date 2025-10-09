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
            value_list = [
                v for v in value_list
                if os.path.normcase(os.path.normpath(v.rstrip('\\'))) != os.path.normcase(os.path.normpath(new_value.rstrip('\\')))
            ]
            value_list.insert(0, new_value)
            new_value_str = os.pathsep.join(value_list)
            winreg.SetValueEx(key, variable_name, 0, regtype, new_value_str)
            print(f"Updated {variable_name} in system variables with: {new_value}")
    except PermissionError:
        print("Permission denied while updating registry. Run as administrator.")

def get_miniforge_versions(base_path):
    forge_versions = []
    for folder in os.listdir(base_path):
        if folder.lower().startswith("miniforge") and folder != "miniforge3":
            forge_versions.append(folder)
    return forge_versions

if __name__ == "__main__":
    if not is_admin():
        print("Requesting administrative privileges...")
        run_as_admin()
        sys.exit()

    base_path = r"C:\ProgramData"
    new_path_no_sep = os.path.normpath(os.path.join(r"C:\ProgramData", "miniforge3"))
    new_path = new_path_no_sep + os.sep
    new_path_scripts = os.path.normpath(os.path.join(new_path_no_sep, "Scripts")) + os.sep

    update_environment_variable('Path', new_path_scripts, winreg.HKEY_LOCAL_MACHINE)
    update_environment_variable('Path', new_path, winreg.HKEY_LOCAL_MACHINE)

    other_forge_versions = get_miniforge_versions(base_path)
    print("Detected other Miniforge versions (excluding miniforge3):", other_forge_versions)

    print("Miniforge3 has been registered as the system Python environment.")

    if platform.system() == 'Windows':
        subprocess.run(['cmd', '/k', 'echo Miniforge system registration complete.'], shell=True)
