import os
import ctypes
import subprocess

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def take_ownership(path):
    try:
        # Use icacls to take ownership of the path
        subprocess.check_call(['icacls', path, '/setowner', 'Administrators'], shell=True)
        print(f"Ownership of {path} has been transferred to Administrators.")
    except Exception as e:
        print(f"Failed to take ownership of {path}: {str(e)}")

if is_admin():
    source_path = os.getcwd()  # Get the current working directory as the source path

    # Ensure the path exists and is a directory
    if os.path.exists(source_path) and os.path.isdir(source_path):
        take_ownership(source_path)
    else:
        print(f"The specified path '{source_path}' does not exist or is not a directory.")
else:
    print("This script needs to be run with administrator privileges.")
