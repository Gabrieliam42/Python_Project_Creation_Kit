# Script Developer: Gabriel Mihai Sandu
# GitHub Profile: https://github.com/Gabrieliam42

import os
import sys
import subprocess
import platform
import ctypes
import shutil
import stat

def is_user_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv + ["--as-admin"]), None, 1
        )
        return True
    except:
        return False

def find_and_remove_venv():
    cwd = os.getcwd()
    for root, dirs, files in os.walk(cwd):
        if 'Scripts' in dirs or 'bin' in dirs:
            venv_root = root
            print(f"Virtual environment found at: {venv_root}")

            scripts_path = os.path.join(root, 'Scripts' if platform.system() == 'Windows' else 'bin')
            required_files = {'deactivate.bat' if platform.system() == 'Windows' else 'deactivate'}

            if required_files.issubset(set(os.listdir(scripts_path))):
                if platform.system() == 'Windows':
                    deactivate_command = f'"{os.path.join(scripts_path, "deactivate.bat")}"'
                else:
                    deactivate_command = f'source "{os.path.join(scripts_path, "deactivate")}"'

                subprocess.run(
                    deactivate_command,
                    shell=True,
                    executable='/bin/bash' if platform.system() != 'Windows' else None
                )

                def on_rm_error(func, path, exc_info):
                    os.chmod(path, stat.S_IWRITE)
                    func(path)

                try:
                    shutil.rmtree(venv_root, onerror=on_rm_error)
                    print(f"Deleted virtual environment folder: {venv_root}")
                except Exception as e:
                    print(f"Failed to delete virtual environment folder {venv_root}: {e}")

                return

    print("No virtual environment found.")

if __name__ == "__main__":
    if platform.system() == "Windows":
        if "--as-admin" not in sys.argv:
            if not is_user_admin():
                if run_as_admin():
                    sys.exit(0)
    find_and_remove_venv()
