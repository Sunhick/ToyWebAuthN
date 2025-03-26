import os
import subprocess
import sys
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info
import subprocess
import os

def run_mkcert():
    """Generate certificates using mkcert"""
    print("Starting certificate generation...")
    try:
        # Run mkcert to create and install local CA
        print("Installing local CA with mkcert...")
        subprocess.run(["mkcert", "-install"], check=True)

        # Create directory for certificates if it doesn't exist
        cert_dir = os.path.join(os.path.expanduser("~"), ".toy-webauthn-certs")
        os.makedirs(cert_dir, exist_ok=True)
        print(f"Created certificate directory: {cert_dir}")

        # Generate certificates for localhost
        cert_path = os.path.join(cert_dir, "localhost.pem")
        key_path = os.path.join(cert_dir, "localhost-key.pem")
        print("Generating localhost certificates...")
        subprocess.run(["mkcert", "-cert-file", cert_path, "-key-file", key_path, "localhost"], check=True)

        print(f"Certificates successfully generated in {cert_dir}")
        print(f"Certificate file: {cert_path}")
        print(f"Key file: {key_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error running mkcert: {e}", file=sys.stderr)
        raise
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        raise

def generate_certs_command():
    """Command line interface for certificate generation"""
    try:
        run_mkcert()
    except Exception as e:
        print(f"Certificate generation failed: {e}", file=sys.stderr)
        sys.exit(1)

class PostDevelopCommand(develop):
    """Post-development command to install certificates."""
    def run(self):
        develop.run(self)
        print("Running post-develop certificate setup...")
        try:
            run_mkcert()
        except Exception as e:
            print(f"Warning: Certificate generation failed: {e}", file=sys.stderr)
            print("You can generate certificates later using: toy-webauthn-generate-certs")

class PostInstallCommand(install):
    """Post-installation command to install certificates."""
    def run(self):
        install.run(self)
        print("Running post-install certificate setup...")
        try:
            run_mkcert()
        except Exception as e:
            print(f"Warning: Certificate generation failed: {e}", file=sys.stderr)
            print("You can generate certificates later using: toy-webauthn-generate-certs")

def run_typescript_build():
    # Run npm install
    subprocess.check_call('npm install', shell=True)
    # Run TypeScript compilation, ignoring errors
    subprocess.call('npx tsc --noEmitOnError', shell=True)

class CustomInstallCommand(install):
    def run(self):
        run_typescript_build()
        install.run(self)

class CustomDevelopCommand(develop):
    def run(self):
        run_typescript_build()
        develop.run(self)

class CustomEggInfoCommand(egg_info):
    def run(self):
        run_typescript_build()
        egg_info.run(self)


# Read README.md content
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "A playful WebAuthn implementation in Flask"
    print("Warning: README.md not found, using default description")

setup(
    name="ToyWebAuthN",
    version="0.1.0",
    author="Sunil Murthy",
    author_email="sunhick@gmail.com",
    description="A playful WebAuthn implementation in Flask",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sunhick/ToyWebAuthN",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
    install_requires=[
        "Flask>=2.0.0",
        "fido2>=0.9.0",
        "python-dotenv>=0.17.0",
        "pymongo>=4.11.3",
        "cbor2>=5.6.5",
        "colorlog>=6.8.0",  # Added for colored logging
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "flake8>=3.9.0",
        ],
    },
    entry_points={
        'console_scripts': [
            'toy-webauthn=toy_web_auth_n.main:main',
            'toy-webauthn-generate-certs=setup:generate_certs_command',
        ],
    },
    cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
        'install': CustomInstallCommand,
        'develop': CustomDevelopCommand,
        'egg_info': CustomEggInfoCommand,
    },
)
