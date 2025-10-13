import os
import subprocess
import sys
from pathlib import Path

from toy_web_auth_n import WebAuthnApp
from toy_web_auth_n.config import LoggingConfig

# Set up logging configuration first
LoggingConfig.setup()

# Initialize logger
logger = LoggingConfig.get_logger(__name__)

def get_device_ip():
    """Get the device's IP address using ifconfig."""
    try:
        result = subprocess.run(['ifconfig'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'inet ' in line and '127.0.0.1' not in line:
                return line.split()[1]
    except Exception:
        pass
    return 'localhost'  # fallback

def check_certificates():
    """Check if the required certificates exist."""
    cert_dir = os.path.expanduser("~/.toy-webauthn-certs")
    device_ip = get_device_ip()
    cert_path = os.path.join(cert_dir, f"{device_ip}.pem")
    key_path = os.path.join(cert_dir, f"{device_ip}-key.pem")

    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        logger.error("SSL certificates not found!")
        logger.error(f"Expected certificate files in: {cert_dir}")
        logger.error("Please run: toy-webauthn-generate-certs")
        logger.error(f"Or install mkcert and run: mkcert -install && mkcert {device_ip}")
        sys.exit(1)

    return cert_path, key_path

def main():
    logger.info("Starting ToyWebAuthN server...")

    try:
        cert_path, key_path = check_certificates()
        logger.info(f"Using certificates from: {os.path.dirname(cert_path)}")

        port = 6000
        app = WebAuthnApp(port)
        logger.info("WebAuthn application initialized")
        logger.info("Starting Flask server...")
        app.app.run(
            host='0.0.0.0',
            port=port,
            ssl_context=(cert_path, key_path),
            debug=True
        )
    except Exception as e:
        logger.error(f"Error starting server: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
