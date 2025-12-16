# Script Developer: Gabriel Mihai Sandu
# GitHub Profile: https://github.com/Gabrieliam42

import os
import subprocess
import platform
import re


def parse_requirements(requirements_path):
    """Parse requirements.txt and return a dict of package names to their specs."""
    packages = {}
    if not os.path.exists(requirements_path):
        return packages

    with open(requirements_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            # Match package name and optional version spec
            match = re.match(r'^([a-zA-Z0-9_-]+)(.*)$', line)
            if match:
                pkg_name = match.group(1).lower()
                version_spec = match.group(2).strip()
                packages[pkg_name] = version_spec
    return packages


def extract_cuda_version(torch_spec):
    """Extract CUDA version from torch spec like '==2.9.0+cu130' -> 'cu130'."""
    match = re.search(r'\+?(cu\d+)', torch_spec)
    if match:
        return match.group(1)
    return None


def get_available_cuda_versions(package_name, cuda_version, pip_path=None):
    """Query pip index for available versions and filter for CUDA-compatible ones."""
    extra_index_url = f"https://download.pytorch.org/whl/{cuda_version}"

    try:
        # Run pip index versions command
        cmd = [
            pip_path or 'pip', 'index', 'versions', package_name,
            '--extra-index-url', extra_index_url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr

        # Extract versions from output - pip index versions shows "Available versions: x.x.x, y.y.y, ..."
        versions = []

        # Look for the "Available versions:" line
        for line in output.split('\n'):
            if 'Available versions:' in line or 'AVAILABLE VERSIONS' in line.upper():
                # Extract versions from the line
                version_part = line.split(':', 1)[-1].strip()
                raw_versions = [v.strip() for v in version_part.split(',')]
                versions.extend(raw_versions)
            # Also check for versions listed line by line
            elif '+' + cuda_version in line:
                # Extract version from line like "0.23.0+cu129"
                match = re.search(r'(\d+\.\d+\.\d+\+' + cuda_version + r')', line)
                if match:
                    versions.append(match.group(1))

        # Filter to only versions containing the CUDA suffix
        cuda_versions = []
        for v in versions:
            if '+' + cuda_version in v:
                cuda_versions.append(v)

        # Remove duplicates and sort by version (newest first)
        cuda_versions = list(dict.fromkeys(cuda_versions))  # Remove duplicates preserving order

        # Sort versions properly (newest first) - pip index usually returns newest first
        # but let's ensure proper sorting
        def version_key(v):
            # Extract numeric parts for sorting (e.g., "0.23.0+cu129" -> (0, 23, 0))
            base = v.split('+')[0]
            parts = base.split('.')
            return tuple(int(p) for p in parts if p.isdigit())

        cuda_versions.sort(key=version_key, reverse=True)

        print(f"  Found {len(cuda_versions)} CUDA-compatible versions for {package_name}: {cuda_versions[:5]}{'...' if len(cuda_versions) > 5 else ''}")
        return cuda_versions

    except subprocess.TimeoutExpired:
        print(f"  Timeout querying versions for {package_name}")
        return []
    except Exception as e:
        print(f"  Error querying versions for {package_name}: {e}")
        return []


def install_package_with_fallback(package_name, cuda_versions, cuda_version, pip_path=None):
    """Try to install a package starting from newest version, falling back to older versions."""
    if not cuda_versions:
        print(f"  No CUDA versions found for {package_name}, skipping...")
        return False

    extra_index_url = f"https://download.pytorch.org/whl/{cuda_version}"
    pip_cmd = pip_path or 'pip'

    for version in cuda_versions:
        print(f"  Attempting to install {package_name}=={version}...")
        cmd = [
            pip_cmd, 'install', f'{package_name}=={version}',
            '--extra-index-url', extra_index_url
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"  Successfully installed {package_name}=={version}")
            return True
        else:
            print(f"  Failed to install {package_name}=={version}, trying previous version...")
            # Optionally print error for debugging
            if 'No matching distribution' in result.stderr or 'No matching distribution' in result.stdout:
                continue
            elif 'error' in result.stderr.lower():
                print(f"    Error: {result.stderr[:200]}...")

    print(f"  Failed to install any version of {package_name}")
    return False


def extract_torch_base_version(torch_spec):
    """Extract base version from torch spec like '==2.9.0+cu130' -> '2.9.0'."""
    match = re.search(r'==?([0-9]+\.[0-9]+\.[0-9]+)', torch_spec)
    if match:
        return match.group(1)
    return None


def process_pytorch_requirements(requirements_path, pip_path):
    """Process requirements.txt and resolve PyTorch CUDA dependencies."""
    packages = parse_requirements(requirements_path)

    # Check if torch is specified with a CUDA version
    torch_spec = packages.get('torch', '')
    cuda_version = extract_cuda_version(torch_spec)

    if not cuda_version:
        print("No CUDA version detected in torch specification.")
        return None, None, {}

    print(f"Detected CUDA version: {cuda_version}")

    # Extract torch base version for reference
    torch_base_version = extract_torch_base_version(torch_spec)
    if torch_base_version:
        print(f"Detected torch base version: {torch_base_version}")

    # PyTorch related packages that need version resolution
    pytorch_companion_packages = ['torchvision', 'torchaudio']
    resolved_packages = {}

    for pkg in pytorch_companion_packages:
        if pkg in packages:
            pkg_spec = packages[pkg]
            # If the spec already has a CUDA suffix (e.g., +cu129), use it as-is
            if '+' in pkg_spec:
                resolved_packages[pkg] = pkg_spec
                print(f"  {pkg}: using specified version {pkg_spec}")
            else:
                # Let pip auto-resolve the compatible version from PyTorch index
                # by NOT specifying a version - pip will find the compatible one
                resolved_packages[pkg] = ""  # Empty = let pip resolve
                print(f"  {pkg}: will auto-resolve compatible version from PyTorch index")

    return cuda_version, torch_base_version, resolved_packages


def build_install_command(requirements_path, pip_path, cuda_version, resolved_packages):
    """Build the pip install command with proper handling of PyTorch packages."""
    packages = parse_requirements(requirements_path)

    # Separate PyTorch packages from others
    pytorch_pkg_names = {'torch', 'torchvision', 'torchaudio'}
    other_packages = []
    pytorch_packages = []

    for pkg, spec in packages.items():
        if pkg in pytorch_pkg_names:
            if pkg in resolved_packages:
                pytorch_packages.append(f"{pkg}{resolved_packages[pkg]}")
            else:
                pytorch_packages.append(f"{pkg}{spec}")
        else:
            other_packages.append(f"{pkg}{spec}")

    commands = []

    # Install PyTorch packages with extra-index-url
    if pytorch_packages and cuda_version:
        extra_index_url = f"https://download.pytorch.org/whl/{cuda_version}"
        pytorch_cmd = f'pip install {" ".join(pytorch_packages)} --extra-index-url {extra_index_url}'
        commands.append(pytorch_cmd)

    # Install other packages normally
    if other_packages:
        # Create a temp requirements file or install directly
        other_cmd = f'pip install {" ".join(other_packages)}'
        commands.append(other_cmd)

    return commands


def find_and_activate_venv():
    cwd = os.getcwd()
    requirements_path = os.path.join(cwd, 'requirements.txt')

    for root, dirs, files in os.walk(cwd):
        if 'Scripts' in dirs or 'bin' in dirs:
            scripts_path = os.path.join(root, 'Scripts' if platform.system() == 'Windows' else 'bin')
            required_files = {'activate.bat' if platform.system() == 'Windows' else 'activate'}

            if required_files.issubset(set(os.listdir(scripts_path))):
                print(f"Virtual environment found and activated at: {root}")

                # Determine pip path
                if platform.system() == 'Windows':
                    pip_path = os.path.join(scripts_path, 'pip.exe')
                    python_path = os.path.join(scripts_path, 'python.exe')
                else:
                    pip_path = os.path.join(scripts_path, 'pip')
                    python_path = os.path.join(scripts_path, 'python3')

                # Check for PyTorch CUDA requirements
                cuda_version, torch_base_version, resolved_packages = process_pytorch_requirements(requirements_path, pip_path)

                if cuda_version:
                    print(f"\nPyTorch CUDA installation detected ({cuda_version})")

                    # First, activate venv and upgrade pip
                    if platform.system() == 'Windows':
                        activate_and_upgrade = f'cmd /c ""{os.path.join(scripts_path, "activate.bat")}" && "{python_path}" -m pip install --upgrade pip"'
                    else:
                        activate_and_upgrade = f'source "{os.path.join(scripts_path, "activate")}" && "{python_path}" -m pip install --upgrade pip'

                    print("\nActivating venv and upgrading pip...")
                    subprocess.run(activate_and_upgrade, shell=True, executable='/bin/bash' if platform.system() != 'Windows' else None)

                    # Install torch first (with specified version from requirements)
                    packages = parse_requirements(requirements_path)
                    torch_spec = packages.get('torch', '')
                    if torch_spec:
                        extra_index_url = f"https://download.pytorch.org/whl/{cuda_version}"
                        print(f"\nInstalling torch{torch_spec}...")
                        torch_cmd = [pip_path, 'install', f'torch{torch_spec}', '--extra-index-url', extra_index_url]
                        subprocess.run(torch_cmd)

                    # Install torchvision and torchaudio with version fallback
                    pytorch_companion_packages = ['torchvision', 'torchaudio']
                    for pkg in pytorch_companion_packages:
                        if pkg in packages:
                            print(f"\nQuerying available versions for {pkg}...")
                            available_versions = get_available_cuda_versions(pkg, cuda_version, pip_path)
                            install_package_with_fallback(pkg, available_versions, cuda_version, pip_path)

                    # Install other non-PyTorch packages
                    pytorch_pkg_names = {'torch', 'torchvision', 'torchaudio'}
                    other_packages = []
                    for pkg, spec in packages.items():
                        if pkg not in pytorch_pkg_names:
                            other_packages.append(f"{pkg}{spec}")

                    if other_packages:
                        print(f"\nInstalling other packages: {other_packages}")
                        other_cmd = [pip_path, 'install'] + other_packages
                        subprocess.run(other_cmd)

                    print("\nInstallation complete!")
                else:
                    # No CUDA detected, use standard installation
                    if platform.system() == 'Windows':
                        activate_command = f'cmd /k ""{os.path.join(scripts_path, "activate.bat")}" && python.exe -m pip install --upgrade pip && pip install -r requirements.txt"'
                    else:
                        activate_command = f'source "{os.path.join(scripts_path, "activate")}" && python3 -m pip install --upgrade pip && pip install -r requirements.txt --upgrade'

                    print(f"\nExecuting installation...")
                    subprocess.run(activate_command, shell=True, executable='/bin/bash' if platform.system() != 'Windows' else None)

                return

    print("No virtual environment found.")


if __name__ == "__main__":
    find_and_activate_venv()
