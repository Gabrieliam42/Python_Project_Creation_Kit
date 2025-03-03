# Script Developer: Gabriel Mihai Sandu
# GitHub Profile: https://github.com/Gabrieliam42

import os
import subprocess
import sys
import tempfile

def is_wsl():
    try:
        with open("/proc/version", "r") as f:
            return "microsoft" in f.read().lower()
    except FileNotFoundError:
        return False

def find_all_venvs():
    # Search for virtual environments in the user's WSL home directory
    home_dir = os.path.expanduser("~")
    venvs = []
    for root, dirs, files in os.walk(home_dir):
        if 'bin' in dirs:
            activate_path = os.path.join(root, 'bin', 'activate')
            if os.path.isfile(activate_path):
                venvs.append(root)
    return venvs

def select_virtualenv():
    venvs = find_all_venvs()
    if not venvs:
        print("No virtual environments found in your home directory.")
        input("Press Enter to exit...")
        sys.exit(1)

    print("Virtual environments found in your home directory:")
    for i, venv in enumerate(venvs, start=1):
        print(f"{i}. {venv}")

    try:
        choice = int(input("Select the number of the virtual environment you want to activate: "))
        if choice < 1 or choice > len(venvs):
            print("Invalid selection.")
            sys.exit(1)
    except ValueError:
        print("Please enter a valid number.")
        sys.exit(1)

    return venvs[choice - 1]

def drop_to_shell(venv_path):
    # Prepare a temporary rcfile that sources the venv activation script,
    # echoes a message, and sets the prompt to display the venv name.
    activate_script = os.path.join(venv_path, "bin", "activate")
    venv_name = os.path.basename(venv_path)
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
        tmp.write(f'source "{activate_script}"\n')
        tmp.write('echo "The virtual environment is activated!"\n')
        # Set PS1 to include the virtual environment name (e.g., "(.venv)")
        tmp.write(f'export PS1="({venv_name}) \\u@\\h:\\w\\$ "\n')
        tmp_path = tmp.name
    print("\nDropping to an interactive shell. Type 'exit' to close the shell.")
    os.system(f"bash --rcfile {tmp_path} -i")
    os.remove(tmp_path)

def main():
    if not is_wsl():
        print("This script must be run inside WSL2. Exiting...")
        sys.exit(1)
    
    # If not already in a virtual environment, let the user select one
    if sys.prefix == sys.base_prefix:
        selected_venv = select_virtualenv()
        venv_python = os.path.join(selected_venv, "bin", "python")
        if not os.path.exists(venv_python):
            print("Python interpreter not found in the selected virtual environment.")
            input("Press Enter to exit...")
            sys.exit(1)
        print("Re-launching the script with the virtual environment's interpreter...")
        os.execv(venv_python, [venv_python] + sys.argv)
    else:
        # We are already running inside a virtual environment.
        drop_to_shell(sys.prefix)

if __name__ == "__main__":
    main()
