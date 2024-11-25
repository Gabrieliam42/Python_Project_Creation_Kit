import os
import shutil
import subprocess
import platform

def delete_older_directories(directory):
    # Delete the specified directory if it exists
    if os.path.exists(directory):
        shutil.rmtree(directory)
        print(f"Deleted directory: {directory}")
    else:
        print(f"Directory not found: {directory}")

def find_and_delete_dist_and_build(cwd):
    # Delete 'dist' and 'build' directories
    delete_older_directories(os.path.join(cwd, 'dist'))
    delete_older_directories(os.path.join(cwd, 'build'))

def find_and_activate_venv():
    # Get the current working directory
    cwd = os.getcwd()
    
    # Delete 'dist' and 'build' directories
    find_and_delete_dist_and_build(cwd)
    
    # Walk through the current directory and its subdirectories
    for root, dirs, files in os.walk(cwd):
        # Check if the directory contains a virtual environment
        if 'Scripts' in dirs or 'bin' in dirs:
            scripts_path = os.path.join(root, 'Scripts' if platform.system() == 'Windows' else 'bin')
            required_files = {'activate.bat' if platform.system() == 'Windows' else 'activate'}
            
            # Check if the required activation file is present in the Scripts/bin directory
            if required_files.issubset(set(os.listdir(scripts_path))):
                print(f"Virtual environment found and activated at: {root}")
                
                # Activate the virtual environment, upgrade pip, and check pip version
                if platform.system() == 'Windows':
                    activate_command = f'cmd /k ""{os.path.join(scripts_path, "activate.bat")}" && python.exe -m pip install --upgrade pip && pyinstaller -F -c main.py"'
                else:
                    activate_command = f'source "{os.path.join(scripts_path, "activate")}" && python3 -m pip install --upgrade pip && pyinstaller -F -c main.py'
                
                subprocess.run(activate_command, shell=True, executable='/bin/bash' if platform.system() != 'Windows' else None)
                return

    print("No virtual environment found.")

if __name__ == "__main__":
    find_and_activate_venv()
