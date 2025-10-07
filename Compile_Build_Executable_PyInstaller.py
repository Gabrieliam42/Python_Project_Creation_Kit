# Script Developer: Gabriel Mihai Sandu
# GitHub Profile: https://github.com/Gabrieliam42

import os
import shutil
import subprocess
import platform
import sys
import textwrap

def delete_directory(path):
    if os.path.exists(path):
        shutil.rmtree(path)
        print(f"Deleted directory: {path}")

def clean_build_dirs(cwd):
    delete_directory(os.path.join(cwd, "build"))
    delete_directory(os.path.join(cwd, "dist"))

    spec_files = [f for f in os.listdir(cwd) if f.endswith(".spec")]
    for spec_file in spec_files:
        try:
            os.remove(os.path.join(cwd, spec_file))
            print(f"Deleted file: {spec_file}")
        except Exception as e:
            print(f"Could not delete {spec_file}: {e}")

def write_custom_spec(py_file):
    base_name = os.path.splitext(os.path.basename(py_file))[0]
    spec_content = textwrap.dedent(f"""
        # -*- mode: python ; coding: utf-8 -*-

        a = Analysis(
            ['{py_file}'],
            pathex=[],
            binaries=[],
            datas=[],
            hiddenimports=[],
            hookspath=[],
            hooksconfig={{}},
            runtime_hooks=[],
            excludes=['pyinstaller', 'pyinstaller-hooks-contrib'],
            noarchive=False,
            optimize=0,
        )

        pyz = PYZ(a.pure)

        exe = EXE(
            pyz,
            a.scripts,
            a.binaries,
            a.datas,
            [],
            name='{base_name}',
            debug=False,
            bootloader_ignore_signals=False,
            strip=False,
            upx=True,
            upx_exclude=[],
            runtime_tmpdir=None,
            console=True,
            disable_windowed_traceback=False,
            argv_emulation=False,
            target_arch=None,
            codesign_identity=None,
            entitlements_file=None,
        )
    """).strip()

    spec_path = f"{base_name}.spec"
    with open(spec_path, "w", encoding="utf-8") as f:
        f.write(spec_content)
    return spec_path

def find_and_activate_venv():
    cwd = os.getcwd()
    print(f"Current working directory: {cwd}")

    clean_build_dirs(cwd)

    py_files = [f for f in os.listdir(cwd) if f.endswith(".py")]
    if not py_files:
        print("No .py files found in current directory.")
        return

    for root, dirs, files in os.walk(cwd):
        if 'Scripts' in dirs or 'bin' in dirs:
            venv_path = os.path.join(root, 'Scripts' if platform.system() == 'Windows' else 'bin')
            required_files = {'activate.bat' if platform.system() == 'Windows' else 'activate'}
            if required_files.issubset(set(os.listdir(venv_path))):
                print(f"Virtual environment found and activated at: {root}")

                pyinstaller_path = os.path.join(venv_path, "pyinstaller.exe") if platform.system() == 'Windows' else "pyinstaller"
                python_path = os.path.join(venv_path, "python.exe") if platform.system() == 'Windows' else "python3"

                subprocess.run([python_path, "-m", "pip", "install", "--upgrade", "pip"], check=False)

                for py_file in py_files:
                    base_name = os.path.splitext(py_file)[0]
                    print(f"Building {base_name}.exe from {py_file}")

                    spec_path = write_custom_spec(py_file)

                    build_cmd = [pyinstaller_path, spec_path] if platform.system() == 'Windows' else ["bash", "-c", f"pyinstaller {spec_path}"]
                    subprocess.run(build_cmd, shell=False)

                    print(f"Completed: {base_name}.exe")

                print("All .py files compiled successfully.")
                return

    print("No virtual environment found.")

if __name__ == "__main__":
    find_and_activate_venv()
