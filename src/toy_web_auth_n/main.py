import sys
import os
from pathlib import Path

from toy_web_auth_n import WebAuthnApp
from toy_web_auth_n.config import LoggingConfig

# Set up logging configuration first
LoggingConfig.setup()

# Initialize logger
logger = LoggingConfig.get_logger(__name__)

def check_certificates():
    """Check if the required certificates exist."""
    cert_dir = os.path.expanduser("~/.toy-webauthn-certs")
    cert_path = os.path.join(cert_dir, "localhost.pem")
    key_path = os.path.join(cert_dir, "localhost-key.pem")

    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        logger.error("SSL certificates not found!")
        logger.error(f"Expected certificate files in: {cert_dir}")
        logger.error("Please run: toy-webauthn-generate-certs")
        logger.error("Or install mkcert and run: mkcert -install && mkcert localhost")
        sys.exit(1)

    return cert_path, key_path

def main():
    logger.info("Starting ToyWebAuthN server...")

    try:
        cert_path, key_path = check_certificates()
        logger.info(f"Using certificates from: {os.path.dirname(cert_path)}")

        app = WebAuthnApp()
        logger.info("WebAuthn application initialized")
        logger.info("Starting Flask server...")
        app.app.run(
            host='localhost',
            port=5000,
            ssl_context=(cert_path, key_path),
            debug=True
        )
    except Exception as e:
        logger.error(f"Error starting server: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
