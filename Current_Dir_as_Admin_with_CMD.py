import os
import ctypes
import sys

def check_admin():
    # Check if the script is running with admin privileges
    admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return admin

def run_as_admin():
    # Run the script as admin
    if not check_admin():
        # Re-run the script with admin rights
        script = sys.argv[0]
        params = " ".join(sys.argv[1:])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, script, params, 1)

if __name__ == "__main__":
    run_as_admin()  # Try to run as admin
    if check_admin():
        # Do not change the directory

        # Open a new command prompt window and keep it open
        ctypes.windll.shell32.ShellExecuteW(None, "open", "cmd.exe", "/k", None, 1)
    else:
        print("Failed to acquire admin privileges.")
