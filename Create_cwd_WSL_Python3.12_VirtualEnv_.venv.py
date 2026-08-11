# Script Developer: Gabriel Mihai Sandu
# GitHub Profile: https://github.com/Gabrieliam42

import os
import shlex
import subprocess
import sys

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


def drop_to_bash_with_activation(activate_path):
    bash_command = (
        f'ACTIVATE_PATH={shlex.quote(activate_path)}; '
        'if [ ! -f "$ACTIVATE_PATH" ]; then '
        'echo "Activation script not found: $ACTIVATE_PATH"; '
        "exit 1; "
        "fi; "
        'source "$ACTIVATE_PATH"; '
        'venv_prompt_fix=\'if [ -n "$VIRTUAL_ENV" ]; then _venv_name="$(basename "$VIRTUAL_ENV")"; '
        'case "$PS1" in ("($_venv_name) "*) ;; (*) PS1="($_venv_name) $PS1" ;; esac; fi\'; '
        'if [ -n "${PROMPT_COMMAND:-}" ]; then '
        'export PROMPT_COMMAND="$venv_prompt_fix; $PROMPT_COMMAND"; '
        'else '
        'export PROMPT_COMMAND="$venv_prompt_fix"; '
        'fi; '
        'echo "Activated virtual environment from: $ACTIVATE_PATH"; '
        "exec bash -i"
    )
    result = subprocess.run(["bash", "-lc", bash_command])
    if result.returncode != 0:
        pause_and_exit("Failed to activate the virtual environment after creation.")


def create_virtualenv_wsl():
    venv_path = os.path.join(os.getcwd(), ".venv")
    try:
        print(f"Creating virtual environment at: {venv_path}")
        subprocess.run(["python3.12", "-m", "venv", ".venv"], check=True)
        print("Virtual environment '.venv' created successfully.")
    except subprocess.CalledProcessError as exc:
        pause_and_exit(f"Error while creating virtual environment: {exc}")

    activate_path = os.path.join(venv_path, "bin", "activate")
    drop_to_bash_with_activation(activate_path)


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


def convert_windows_cwd_to_wsl():
    windows_cwd = os.getcwd()
    result = subprocess.run(
        ["wsl", "-d", DISTRO_NAME, "-e", "wslpath", "-a", "-u", windows_cwd],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        error_text = result.stderr.strip() or "Unknown error while converting Windows path to WSL path."
        pause_and_exit(f"Failed to convert current directory to WSL path: {error_text}")

    wsl_cwd = result.stdout.strip()
    if not wsl_cwd:
        pause_and_exit("Failed to convert current directory to WSL path: empty result.")
    return wsl_cwd


def create_virtualenv_from_windows():
    ensure_wsl_available()
    wsl_cwd = convert_windows_cwd_to_wsl()

    bash_script = f"""
set -e
cd -- {shlex.quote(wsl_cwd)}
command -v python3.12 >/dev/null || {{ echo "python3.12 not found"; exit 1; }}
python3.12 -m venv .venv
activate_path=".venv/bin/activate"
if [ ! -f "$activate_path" ]; then
    echo "Activation script not found: $activate_path"
    exit 1
fi
source "$activate_path"
venv_prompt_fix='if [ -n "$VIRTUAL_ENV" ]; then _venv_name="$(basename "$VIRTUAL_ENV")"; case "$PS1" in ("($_venv_name) "*) ;; (*) PS1="($_venv_name) $PS1" ;; esac; fi'
if [ -n "${{PROMPT_COMMAND:-}}" ]; then
    export PROMPT_COMMAND="$venv_prompt_fix; $PROMPT_COMMAND"
else
    export PROMPT_COMMAND="$venv_prompt_fix"
fi
echo "Virtual environment '.venv' created and activated in: $(pwd)"
exec bash -i
"""
    result = subprocess.run(["wsl", "-d", DISTRO_NAME, "-e", "bash", "-lc", bash_script])
    if result.returncode != 0:
        pause_and_exit("Failed to create and activate virtual environment in WSL.")

if __name__ == "__main__":
    if is_wsl():
        create_virtualenv_wsl()
    else:
        create_virtualenv_from_windows()
