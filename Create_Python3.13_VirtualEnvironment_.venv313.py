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

def get_python_versions(base_path):
    python_versions = []
    for folder in os.listdir(base_path):
        match = re.match(r'^Python(\d{3})$', folder)
        if match and match.group(1) != '313':
            python_versions.append(folder)
    return python_versions

def update_environment_variable(variable_name, new_value, scope):
    try:
        with winreg.OpenKey(scope, r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 0, winreg.KEY_ALL_ACCESS) as key:
            value, regtype = winreg.QueryValueEx(key, variable_name)
            value_list = value.split(os.pathsep)
            # Remove any existing instances of the new value
            value_list = [v for v in value_list if v != new_value]
            # Add the new value to the top
            value_list.insert(0, new_value)
            new_value_str = os.pathsep.join(value_list)
            winreg.SetValueEx(key, variable_name, 0, regtype, new_value_str)
            print(f"Updated {variable_name} in system variables.")
    except FileNotFoundError:
        print(f"{variable_name} not found in system variables.")

def create_virtual_environment(directory):
    print(f"Creating a virtual environment in {directory}...")
    subprocess.run(["python", "-m", "venv", ".venv313"], cwd=directory, shell=True)
    print("Virtual environment created.")

def find_and_activate_venv():
    cwd = os.getcwd()
    for root, dirs, files in os.walk(cwd):
        if 'Scripts' in dirs or 'bin' in dirs:
            scripts_path = os.path.join(root, 'Scripts' if platform.system() == 'Windows' else 'bin')
            required_files = {'activate.bat' if platform.system() == 'Windows' else 'activate'}
            if required_files.issubset(set(os.listdir(scripts_path))):
                print(f"Virtual environment found and activated at: {root}")
                if platform.system() == 'Windows':
                    activate_command = f'cmd /k ""{os.path.join(scripts_path, "activate.bat")}" && python.exe -m pip install --upgrade pip"'
                else:
                    activate_command = f'source "{os.path.join(scripts_path, "activate")}" && python3 -m pip install --upgrade pip'
                subprocess.run(activate_command, shell=True, executable='/bin/bash' if platform.system() != 'Windows' else None)
                return
    print("No virtual environment found.")

if __name__ == "__main__":
    if not is_admin():
        print("Requesting administrative privileges...")
        run_as_admin()
        sys.exit()
    
    base_path = r"C:\Program Files"
    new_path = r"C:\Program Files\Python313"
    new_path_scripts = os.path.join(new_path, 'Scripts')
    
    update_environment_variable('Path', new_path_scripts, winreg.HKEY_LOCAL_MACHINE)
    update_environment_variable('Path', new_path, winreg.HKEY_LOCAL_MACHINE)
    
    print("All changes to the System and User Variables have been made!")
    create_virtual_environment(os.getcwd())
    find_and_activate_venv()
    
    if platform.system() == 'Windows':
        subprocess.run(['cmd', '/k', 'echo Virtual environment setup complete.'], shell=True)
