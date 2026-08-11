# Script Developer: Gabriel Mihai Sandu
# GitHub Profile: https://github.com/Gabrieliam42

import os
import subprocess
import sys
import tempfile

DISTRO_NAME = "Ubuntu"


def is_wsl():
    try:
        with open("/proc/version", "r") as f:
            return "microsoft" in f.read().lower()
    except FileNotFoundError:
        return False


def pause_and_exit(message, code=1):
    print(message)
    try:
        input("Press Enter to exit...")
    except EOFError:
        pass
    sys.exit(code)


def find_all_venvs():
    # Search for virtual environments in the user's WSL home directory
    home_dir = os.path.expanduser("~")
    venvs = []
    for root, dirs, files in os.walk(home_dir):
        dirs.sort()
        if "bin" in dirs:
            activate_path = os.path.join(root, "bin", "activate")
            if os.path.isfile(activate_path):
                venvs.append(root)
    return sorted(venvs)


def select_virtualenv(venvs):
    if not venvs:
        pause_and_exit("No virtual environments found in your home directory.")

    print("Virtual environments found in your home directory:")
    for i, venv in enumerate(venvs, start=1):
        print(f"{i}. {venv}")

    while True:
        choice_text = input("Select the number of the virtual environment you want to activate: ").strip()
        if choice_text.isdigit():
            choice = int(choice_text)
            if 1 <= choice <= len(venvs):
                return venvs[choice - 1]
        print(f"Invalid selection. Enter a number between 1 and {len(venvs)}.")


def drop_to_shell(venv_path):
    # Prepare a temporary rcfile that sources the venv activation script,
    # echoes a message, and ensures the prompt keeps the venv prefix.
    activate_script = os.path.join(venv_path, "bin", "activate")
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
        tmp.write(f'source "{activate_script}"\n')
        tmp.write('echo "The virtual environment is activated!"\n')
        tmp.write('venv_prompt_fix=\'if [ -n "$VIRTUAL_ENV" ]; then _venv_name="$(basename "$VIRTUAL_ENV")"; case "$PS1" in ("($_venv_name) "*) ;; (*) PS1="($_venv_name) $PS1" ;; esac; fi\'\n')
        tmp.write('if [ -n "${PROMPT_COMMAND:-}" ]; then\n')
        tmp.write('    export PROMPT_COMMAND="$venv_prompt_fix; $PROMPT_COMMAND"\n')
        tmp.write('else\n')
        tmp.write('    export PROMPT_COMMAND="$venv_prompt_fix"\n')
        tmp.write('fi\n')
        tmp_path = tmp.name
    print("\nDropping to an interactive shell. Type 'exit' to close the shell.")
    subprocess.run(["bash", "--rcfile", tmp_path, "-i"])
    os.remove(tmp_path)


def activate_virtualenv_wsl():
    # If not already in a virtual environment, let the user select one
    if sys.prefix == sys.base_prefix:
        venvs = find_all_venvs()
        selected_venv = select_virtualenv(venvs)
        venv_python = os.path.join(selected_venv, "bin", "python")
        if not os.path.exists(venv_python):
            pause_and_exit("Python interpreter not found in the selected virtual environment.")
        print("Re-launching the script with the virtual environment's interpreter...")
        os.execv(venv_python, [venv_python] + sys.argv)
    else:
        # We are already running inside a virtual environment.
        drop_to_shell(sys.prefix)


def ensure_wsl_available():
    try:
        subprocess.run(
            ["wsl", "-d", DISTRO_NAME, "-e", "bash", "-lc", "exit 0"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
    except FileNotFoundError:
        pause_and_exit("WSL command not found. Ensure WSL is installed and available in PATH.")
    except subprocess.CalledProcessError as exc:
        error_text = (exc.stderr or "").strip()
        if error_text:
            pause_and_exit(
                f"Unable to run 'wsl -d {DISTRO_NAME}'. Ensure the distro exists and WSL is working.\n{error_text}"
            )
        pause_and_exit(f"Unable to run 'wsl -d {DISTRO_NAME}'. Ensure the distro exists and WSL is working.")


def activate_virtualenv_from_windows():
    ensure_wsl_available()

    bash_script = """
set -e
mapfile -t venv_paths < <(find "$HOME" -type f -path "*/bin/activate" -printf "%h\\n" | sed 's#/bin$##' | sort -u)
if [ "${#venv_paths[@]}" -eq 0 ]; then
    echo "No virtual environments found in your home directory."
    exit 1
fi
echo "Virtual environments found in your home directory:"
for i in "${!venv_paths[@]}"; do
    printf "%d. %s\\n" "$((i + 1))" "${venv_paths[$i]}"
done
while true; do
    read -rp "Select the number of the virtual environment you want to activate: " choice
    if [[ "$choice" =~ ^[0-9]+$ ]] && (( choice >= 1 && choice <= ${#venv_paths[@]} )); then
        break
    fi
    echo "Invalid selection. Enter a number between 1 and ${#venv_paths[@]}."
done
selected_venv="${venv_paths[$((choice - 1))]}"
activate_script="$selected_venv/bin/activate"
if [ ! -f "$activate_script" ]; then
    echo "Activation script not found for selected virtual environment: $selected_venv"
    exit 1
fi
source "$activate_script"
echo "The virtual environment is activated!"
venv_prompt_fix='if [ -n "$VIRTUAL_ENV" ]; then _venv_name="$(basename "$VIRTUAL_ENV")"; case "$PS1" in ("($_venv_name) "*) ;; (*) PS1="($_venv_name) $PS1" ;; esac; fi'
if [ -n "${PROMPT_COMMAND:-}" ]; then
    export PROMPT_COMMAND="$venv_prompt_fix; $PROMPT_COMMAND"
else
    export PROMPT_COMMAND="$venv_prompt_fix"
fi
exec bash -i
"""

    result = subprocess.run(["wsl", "-d", DISTRO_NAME, "-e", "bash", "-lc", bash_script])
    if result.returncode != 0:
        pause_and_exit("Failed to start WSL shell and activate virtual environment.")


def main():
    if is_wsl():
        activate_virtualenv_wsl()
    else:
        activate_virtualenv_from_windows()

if __name__ == "__main__":
    main()
