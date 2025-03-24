import logging
import sys
import os
from pathlib import Path

from .WebAuthnManager import WebAuthnApp

class LoggerSetup:
    @staticmethod
    def setup():
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        fh = logging.FileHandler('webauthn.log')
        fh.setLevel(logging.DEBUG)

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)

def check_certificates():
    """Check if the required certificates exist."""
    cert_dir = os.path.expanduser("~/.toy-webauthn-certs")
    cert_path = os.path.join(cert_dir, "localhost.pem")
    key_path = os.path.join(cert_dir, "localhost-key.pem")

    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        print("Error: SSL certificates not found!")
        print(f"Expected certificate files in: {cert_dir}")
        print("Please run: toy-webauthn-generate-certs")
        print("Or install mkcert and run: mkcert -install && mkcert localhost")
        sys.exit(1)

    return cert_path, key_path

def main():
    LoggerSetup.setup()
    logging.info("Starting ToyWebAuthN server...")

    try:
        cert_path, key_path = check_certificates()
        logging.info(f"Using certificates from: {os.path.dirname(cert_path)}")

        app = WebAuthnApp()
        app.app.run(
            host='localhost',
            port=5000,
            ssl_context=(cert_path, key_path),
            debug=True
        )
    except Exception as e:
        logging.error(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
