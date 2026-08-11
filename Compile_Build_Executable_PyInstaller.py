# Script Developer: Gabriel Mihai Sandu
# GitHub Profile: https://github.com/Gabrieliam42

import os
import shutil
import subprocess
import platform
import textwrap
import ast
import re

def delete_directory(path):
    if os.path.exists(path):
        shutil.rmtree(path)
        print(f"Deleted directory: {path}")

def clean_build_dirs(cwd):
    delete_directory(os.path.join(cwd, "build"))
    delete_directory(os.path.join(cwd, "dist"))

    for f in os.listdir(cwd):
        if f.endswith(".spec"):
            try:
                os.remove(os.path.join(cwd, f))
                print(f"Deleted file: {f}")
            except Exception as e:
                print(f"Could not delete {f}: {e}")

def extract_imports_from_file(py_file):
    """Extract all imported modules from a Python file using AST parsing"""
    modules = set()

    try:
        # Try AST parsing first
        with open(py_file, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=py_file)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    modules.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    modules.add(node.module.split('.')[0])
    except Exception as e:
        # Fallback to regex if AST fails
        print(f"AST parsing failed, using regex fallback: {e}")
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            import_pattern = r'^(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))'
            for match in re.finditer(import_pattern, content, re.MULTILINE):
                module = match.group(1) or match.group(2)
                modules.add(module.split('.')[0])
        except Exception as e2:
            print(f"Regex parsing also failed: {e2}")

    return modules

def get_hidden_imports_for_modules(modules):
    """Map detected modules to their required hidden imports"""

    hidden_imports_map = {
        'pystray': ['pystray._win32', 'pystray._base', 'pystray._util'],
        'PIL': ['PIL._imaging', 'PIL.Image', 'PIL.ImageDraw', 'PIL.ImageFont', 'PIL.ImageTk'],
        'Pillow': ['PIL._imaging', 'PIL.Image', 'PIL.ImageDraw', 'PIL.ImageFont', 'PIL.ImageTk'],
        'tkinter': ['tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox', 'tkinter.scrolledtext'],
        'numpy': ['numpy.core._multiarray_umath', 'numpy.core._methods'],
        'pandas': ['pandas._libs', 'pandas._libs.tslibs'],
        'torch': ['torch._C', 'torch.nn', 'torch.optim'],
        'cv2': ['cv2.cv2'],
        'sklearn': ['sklearn.utils._cython_blas', 'sklearn.neighbors.typedefs', 'sklearn.neighbors.quad_tree', 'sklearn.tree._utils'],
        'sqlalchemy': ['sqlalchemy.ext.declarative', 'sqlalchemy.orm'],
        'requests': ['urllib3'],
        'matplotlib': ['matplotlib.backends.backend_tkagg', 'matplotlib.backends.backend_agg'],
        'scipy': ['scipy.special', 'scipy.linalg', 'scipy.sparse'],
        'win32api': ['win32con', 'win32gui', 'win32com', 'pywintypes'],
        'win32com': ['win32com.client', 'win32com.server'],
        'ctypes': ['ctypes.wintypes'],
    }

    hidden_imports = []
    for module in modules:
        if module in hidden_imports_map:
            hidden_imports.extend(hidden_imports_map[module])

    return list(set(hidden_imports))  # Remove duplicates

def write_custom_spec(py_file):
    base_name = os.path.splitext(os.path.basename(py_file))[0]

    # Auto-detect imports and get hidden imports
    detected_modules = extract_imports_from_file(py_file)
    hidden_imports = get_hidden_imports_for_modules(detected_modules)

    print(f"Detected modules: {', '.join(sorted(detected_modules))}")
    print(f"Adding hidden imports: {hidden_imports}")

    # Format hidden imports for spec file
    hidden_imports_str = str(hidden_imports)

    spec_content = textwrap.dedent(f"""
        # -*- mode: python ; coding: utf-8 -*-

        a = Analysis(
            ['{py_file}'],
            pathex=[],
            binaries=[],
            datas=[],
            hiddenimports={hidden_imports_str},
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

def copy_all_executables(cwd):
    dist_path = os.path.join(cwd, "dist")
    if not os.path.exists(dist_path):
        print("No dist directory found.")
        return

    copied = 0
    for root, _, files in os.walk(dist_path):
        for file in files:
            if file.lower().endswith(".exe"):
                src = os.path.join(root, file)
                dst = os.path.join(cwd, file)
                try:
                    shutil.copy2(src, dst)
                    copied += 1
                    print(f"Copied: {src} → {dst}")
                except Exception as e:
                    print(f"Failed to copy {src}: {e}")

    if copied == 0:
        print("No .exe files found in dist directory.")
    else:
        print(f"Copied {copied} .exe file(s) to CWD.")

def find_and_activate_venv():
    cwd = os.getcwd()
    print(f"Current working directory: {cwd}")

    clean_build_dirs(cwd)

    py_files = [f for f in os.listdir(cwd) if f.endswith(".py")]
    if not py_files:
        print("No .py files found in current directory.")
        return

    for root, dirs, _ in os.walk(cwd):
        scripts_dir = 'Scripts' if platform.system() == 'Windows' else 'bin'
        if scripts_dir in dirs:
            venv_path = os.path.join(root, scripts_dir)
            activator = 'activate.bat' if platform.system() == 'Windows' else 'activate'
            if activator in os.listdir(venv_path):
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

                copy_all_executables(cwd)
                print("All .py files compiled and copied successfully.")
                return

    print("No virtual environment found.")

if __name__ == "__main__":
    find_and_activate_venv()
