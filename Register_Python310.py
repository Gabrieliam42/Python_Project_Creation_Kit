import os
import ctypes
import sys
import subprocess

def run_as_admin():
    try:
        if ctypes.windll.shell32.IsUserAnAdmin():
            print("Running as Admin.")
        else:
            script = os.path.abspath(sys.argv[0])
            params = " ".join(sys.argv[1:])
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, script, params, 1)
            sys.exit()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit()

def adjust_path():
    new_paths = [
        r'C:\Program Files\Python310\Scripts',
        r'C:\Program Files\Python310'
    ]

    current_path = subprocess.check_output(
        'powershell -Command "[System.Environment]::GetEnvironmentVariable(\'Path\',\'Machine\')"',
        shell=True
    ).decode().strip()
    path_parts = current_path.split(os.pathsep)

    path_parts = [p for p in path_parts if p.rstrip('\\') not in [np.rstrip('\\') for np in new_paths]]
    path_parts = new_paths + path_parts

    new_path = os.pathsep.join(path_parts)

    command = f'powershell -Command "[System.Environment]::SetEnvironmentVariable(\'Path\', \'{new_path}\', \'Machine\')"'
    subprocess.run(command, shell=True)

def main():
    try:
        run_as_admin()
        adjust_path()
        print("System PATH updated successfully.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
