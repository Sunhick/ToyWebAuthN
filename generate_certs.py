#!/usr/bin/env python3
import os
import subprocess
import sys

def check_mkcert():
    """Check if mkcert is installed and available in PATH"""
    try:
        result = subprocess.run(["mkcert", "--version"],
                              check=False,  # Don't raise exception
                              capture_output=True,
                              text=True)
        if result.returncode != 0:
            print(f"Error running mkcert --version: {result.stderr}", file=sys.stderr)
            return False
        return True
    except FileNotFoundError:
        print("Error: mkcert command not found in PATH", file=sys.stderr)
        return False

def run_mkcert():
    """Generate certificates using mkcert"""
    print("Starting certificate generation...")
    print(f"Current PATH: {os.environ.get('PATH', '')}")

    if not check_mkcert():
        print("\nTo install mkcert:", file=sys.stderr)
        print("  On macOS: brew install mkcert", file=sys.stderr)
        print("  On Linux: sudo apt install mkcert", file=sys.stderr)
        print("  Or download from: https://github.com/FiloSottile/mkcert/releases", file=sys.stderr)
        sys.exit(1)

    try:
        # Run mkcert to create and install local CA
        print("Installing local CA with mkcert...")
        result = subprocess.run(["mkcert", "-install"],
                              check=False,
                              capture_output=True,
                              text=True)
        if result.returncode != 0:
            print(f"Error installing CA: {result.stderr}", file=sys.stderr)
            sys.exit(1)

        # Create directory for certificates if it doesn't exist
        cert_dir = os.path.join(os.path.expanduser("~"), ".toy-webauthn-certs")
        os.makedirs(cert_dir, exist_ok=True)
        print(f"Created certificate directory: {cert_dir}")

        # Generate certificates for localhost
        cert_path = os.path.join(cert_dir, "localhost.pem")
        key_path = os.path.join(cert_dir, "localhost-key.pem")
        print("Generating localhost certificates...")
        result = subprocess.run(
            ["mkcert", "-cert-file", cert_path, "-key-file", key_path, "localhost"],
            check=False,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"Error generating certificates: {result.stderr}", file=sys.stderr)
            sys.exit(1)

        print(f"Certificates successfully generated in {cert_dir}")
        print(f"Certificate file: {cert_path}")
        print(f"Key file: {key_path}")
        return True
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_mkcert()
