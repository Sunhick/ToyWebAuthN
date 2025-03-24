import os
import subprocess
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install

def run_mkcert():
    try:
        # Run mkcert to create and install local CA
        subprocess.run(["mkcert", "-install"], check=True)

        # Create directory for certificates if it doesn't exist
        cert_dir = os.path.join(os.path.expanduser("~"), ".toy-webauthn-certs")
        os.makedirs(cert_dir, exist_ok=True)

        # Generate certificates for localhost
        cert_path = os.path.join(cert_dir, "localhost.pem")
        key_path = os.path.join(cert_dir, "localhost-key.pem")
        subprocess.run(["mkcert", "-cert-file", cert_path, "-key-file", key_path, "localhost"], check=True)

        print(f"Certificates generated in {cert_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Error running mkcert: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

class PostDevelopCommand(develop):
    def run(self):
        run_mkcert()
        develop.run(self)

class PostInstallCommand(install):
    def run(self):
        run_mkcert()
        install.run(self)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

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
        ],
    },
    cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
    },
)
