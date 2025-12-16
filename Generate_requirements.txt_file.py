# Script Developer: Gabriel Mihai Sandu
# GitHub Profile: https://github.com/Gabrieliam42

import os
import subprocess
import platform

# Packages that come pre-installed with Python and should be excluded
STDLIB_PACKAGES = {
    'pip',
    'setuptools',
    'wheel',
    'distribute',
    'pkg-resources',
    'pkg_resources',
}

# PyTorch-related packages that need special index URL (in order: torch must come first)
PYTORCH_PACKAGES_ORDERED = ['torch', 'torchvision', 'torchaudio']
PYTORCH_PACKAGES = set(PYTORCH_PACKAGES_ORDERED)

def find_venv_scripts_path():
    cwd = os.getcwd()
    for root, dirs, files in os.walk(cwd):
        if 'Scripts' in dirs or 'bin' in dirs:
            scripts_path = os.path.join(root, 'Scripts' if platform.system() == 'Windows' else 'bin')
            activate_file = 'activate.bat' if platform.system() == 'Windows' else 'activate'
            if activate_file in os.listdir(scripts_path):
                return scripts_path
    return None

def extract_cuda_version(version_string):
    """Extract CUDA version from torch version string like '2.9.0+cu129' -> 'cu129'"""
    if '+cu' in version_string:
        # Extract the cu### part
        cuda_part = version_string.split('+')[1]
        return cuda_part
    return None

def generate_requirements(scripts_path):
    try:
        if platform.system() == 'Windows':
            python_exe = os.path.join(scripts_path, 'python.exe')
        else:
            python_exe = os.path.join(scripts_path, 'python')

        subprocess.run([python_exe, "-m", "pip", "install", "--upgrade", "pip"], check=True)

        # Get all installed packages using pip freeze
        freeze_result = subprocess.run(
            [python_exe, "-m", "pip", "freeze"],
            capture_output=True,
            text=True,
            check=True
        )

        # Get full version info using pip show for PyTorch packages
        def get_package_version(pkg_name):
            result = subprocess.run(
                [python_exe, "-m", "pip", "show", pkg_name],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if line.startswith('Version:'):
                        return line.split(':', 1)[1].strip()
            return None

        # Filter out stdlib/pre-installed packages and detect PyTorch
        filtered_lines = []
        pytorch_lines = []
        cuda_version = None

        # First, check for PyTorch packages
        # Use ordered list to ensure torch comes before torchvision/torchaudio
        for pytorch_pkg in PYTORCH_PACKAGES_ORDERED:
            version = get_package_version(pytorch_pkg)
            if version:
                full_line = f"{pytorch_pkg}=={version}"
                pytorch_lines.append(full_line)
                # Try to extract CUDA version from torch specifically
                if pytorch_pkg == 'torch':
                    cuda_version = extract_cuda_version(version)

        # Process all packages from pip freeze
        for line in freeze_result.stdout.splitlines():
            if line.strip():
                package_name = line.split('==')[0].split('[')[0].lower().replace('-', '_')

                if package_name in {p.lower().replace('-', '_') for p in STDLIB_PACKAGES}:
                    continue

                # Skip PyTorch packages (already handled above)
                if package_name in PYTORCH_PACKAGES:
                    continue

                filtered_lines.append(line)

        with open("requirements.txt", "w", encoding="utf-8") as f:
            # If PyTorch packages with CUDA are found, add the extra index URL first
            if pytorch_lines and cuda_version:
                f.write("--trusted-host download.pytorch.org\n")
                f.write(f"--extra-index-url https://download.pytorch.org/whl/{cuda_version}\n")

            # Write PyTorch packages first (if any)
            for line in pytorch_lines:
                f.write(line + '\n')

            # Write other packages
            for line in filtered_lines:
                f.write(line + '\n')

        print(f"requirements.txt generated successfully at {os.getcwd()}")
        print(f"Included {len(filtered_lines) + len(pytorch_lines)} top-level package(s), excluded dependencies")
        if cuda_version:
            print(f"Detected PyTorch with CUDA {cuda_version}")
    except subprocess.CalledProcessError as e:
        print("Error generating requirements.txt:", e)

def main():
    scripts_path = find_venv_scripts_path()
    if not scripts_path:
        print("No virtual environment found in current directory or subdirectories.")
        return
    print(f"Virtual environment found at: {scripts_path}")
    generate_requirements(scripts_path)

if __name__ == "__main__":
    main()
