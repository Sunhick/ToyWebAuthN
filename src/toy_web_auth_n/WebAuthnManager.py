"""
WebAuthn Manager Module

This module provides the core WebAuthn functionality and Flask integration, including:
1. WebAuthn server configuration and initialization
2. Relying Party (RP) setup and management
3. Flask route handlers for WebAuthn operations
4. Session management and state handling

Key Components:
1. WebAuthnManager:
   - Configures the WebAuthn Relying Party
   - Manages allowed origins
   - Coordinates registration and authentication
   - Handles credential storage

2. WebAuthnApp:
   - Provides Flask application setup
   - Implements WebAuthn route handlers
   - Manages session state
   - Handles request/response processing

Dependencies:
    - flask: Web application framework
    - fido2: WebAuthn/FIDO2 implementation
    - pymongo: MongoDB database operations
    - WebAuthnAuthentication: Authentication handling
    - WebAuthnRegistration: Registration handling
"""

import os
import subprocess

from fido2.server import Fido2Server
from fido2.webauthn import (
    PublicKeyCredentialRpEntity,
    AttestationConveyancePreference,
)
from flask import Flask, request, render_template, session, redirect, url_for
from pymongo import MongoClient

from toy_web_auth_n.authentication.WebAuthnAuthentication import (
    WebAuthnAuthentication,
)
from toy_web_auth_n.config import LoggingConfig, MongoDBConfig
from toy_web_auth_n.registration.WebAuthnRegistration import WebAuthnRegistration

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


class WebAuthnManager:
    """
    Manages WebAuthn server configuration and coordinates registration and authentication.

    This class is responsible for:
    1. Setting up the WebAuthn Relying Party (RP)
    2. Configuring allowed origins
    3. Managing credential storage
    4. Coordinating registration and authentication processes

    Attributes:
        origins (list): List of allowed origins for WebAuthn operations
        rp (PublicKeyCredentialRpEntity): The Relying Party entity
        server (Fido2Server): The FIDO2 server instance
        credentials (dict): In-memory storage for credentials
        registration (WebAuthnRegistration): Registration handler
        authentication (WebAuthnAuthentication): Authentication handler
    """

    def __init__(self, db):
        """Initialize the WebAuthn manager with default configuration."""
        device_ip = get_device_ip()
        
        self.origins = [
            f"https://{device_ip}",
            f"https://{device_ip}:5000",
            "https://127.0.0.1",
            "https://[::1]",
        ]
        
        self.rp = PublicKeyCredentialRpEntity(id=device_ip, name="WebAuthN Demo")
        self.server = Fido2Server(
            self.rp,
            attestation=AttestationConveyancePreference.NONE,
            verify_origin=self.verify_origin,
        )
        self.db = db
        self.registration = WebAuthnRegistration(self.server, self.db)
        self.authentication = WebAuthnAuthentication(self.server, self.db)

    def verify_origin(self, origin):
        """
        Verify if the given origin is allowed.

        Args:
            origin (str): The origin to verify

        Returns:
            bool: True if origin is allowed, False otherwise
        """
        return origin in self.origins


class WebAuthnApp:
    """
    Flask application wrapper for WebAuthn functionality.

    This class provides:
    1. Flask application setup with proper template configuration
    2. Route handlers for WebAuthn operations
    3. Session management for registration and authentication states

    Attributes:
        app (Flask): The Flask application instance
        webauthn_manager (WebAuthnManager): The WebAuthn manager instance
    """

    def __init__(self):
        """Initialize the Flask application with WebAuthn support."""
        template_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'templates'
        )
        self.app = Flask(__name__, template_folder=template_dir)
        self.app.secret_key = os.urandom(32)

        # Initialize MongoDB configuration and connection
        mongodb_config = MongoDBConfig()
        client = MongoClient(mongodb_config.get_connection_url())
        db = client[mongodb_config.get_database_name()]

        self.webauthn_manager = WebAuthnManager(db)
        logger.info("WebAuthn manager initialized with MongoDB configuration")

        self.setup_routes()

    def setup_routes(self):
        """Set up Flask routes for WebAuthn operations."""

        @self.app.route('/')
        def index():
            """Render the main page with WebAuthn interface."""
            return render_template('index.html')

        @self.app.route('/register/begin', methods=['POST'])
        def register_begin():
            """
            Begin the registration process.

            Expects:
                JSON body with {"username": string}

            Returns:
                JSON object containing WebAuthn registration options
            """
            if request.json is None:
                raise ValueError("username not passed in")
            username = request.json['username']
            options, state = self.webauthn_manager.registration.begin(username)
            session['register_state'] = state
            return options

        @self.app.route('/register/complete', methods=['POST'])
        def register_complete():
            """
            Complete the registration process.

            Expects:
                JSON body with attestation response from authenticator

            Returns:
                JSON object with registration status
            """
            state = session.pop('register_state')
            return self.webauthn_manager.registration.complete(state, request.json)

        @self.app.route('/authenticate/begin', methods=['POST'])
        def authenticate_begin():
            """
            Begin the authentication process.

            Returns:
                JSON object containing WebAuthn authentication options
            """
            if request.json is None:
                raise ValueError("username not passed in")
            username = request.json['username']
            options, state = self.webauthn_manager.authentication.begin(username)
            session['auth_state'] = state
            session['username'] = username
            return options

        @self.app.route('/authenticate/complete', methods=['POST'])
        def authenticate_complete():
            """
            Complete the authentication process.

            Expects:
                JSON body with assertion response from authenticator

            Returns:
                JSON object with authentication status or redirect to success page
            """
            state = session.pop('auth_state')
            result = self.webauthn_manager.authentication.complete(
                state, request.json
            )
            
            # Check if authentication was successful
            import json as json_module
            result_data = json_module.loads(result)
            if result_data.get('status') == 'success':
                return json_module.dumps({'redirect': '/success'})
            else:
                return result

        @self.app.route('/success')
        def success():
            """Display success page after authentication."""
            username = session.get('username')
            if not username:
                return redirect(url_for('index'))
            return render_template('success.html', username=username)

        @self.app.route('/signout', methods=['POST'])
        def signout():
            """Sign out user and clear session."""
            session.clear()
            return '', 204
