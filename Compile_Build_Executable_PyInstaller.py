# Script Developer: Gabriel Mihai Sandu
# GitHub Profile: https://github.com/Gabrieliam42

import os
import shutil
import subprocess
import platform

def delete_older_directories(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
        print(f"Deleted directory: {directory}")
    else:
        print(f"Directory not found: {directory}")

def find_and_delete_dist_and_build(cwd):
    delete_older_directories(os.path.join(cwd, 'dist'))
    delete_older_directories(os.path.join(cwd, 'build'))

def find_and_activate_venv():
    cwd = os.getcwd()
    
    find_and_delete_dist_and_build(cwd)
    
    for root, dirs, files in os.walk(cwd):
        if 'Scripts' in dirs or 'bin' in dirs:
            scripts_path = os.path.join(root, 'Scripts' if platform.system() == 'Windows' else 'bin')
            required_files = {'activate.bat' if platform.system() == 'Windows' else 'activate'}
            
            if required_files.issubset(set(os.listdir(scripts_path))):
                print(f"Virtual environment found and activated at: {root}")
                
                if platform.system() == 'Windows':
                    activate_command = f'cmd /k ""{os.path.join(scripts_path, "activate.bat")}" && python.exe -m pip install --upgrade pip && pyinstaller -F -c main.py"'
                else:
                    activate_command = f'source "{os.path.join(scripts_path, "activate")}" && python3 -m pip install --upgrade pip && pyinstaller -F -c main.py'
                
                subprocess.run(activate_command, shell=True, executable='/bin/bash' if platform.system() != 'Windows' else None)
                return

    print("No virtual environment found.")

if __name__ == "__main__":
    find_and_activate_venv()
