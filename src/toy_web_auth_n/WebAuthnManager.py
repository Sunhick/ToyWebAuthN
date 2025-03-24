import os
from flask import Flask, request, render_template, session
from fido2.webauthn import (
    PublicKeyCredentialRpEntity
)
from fido2.server import Fido2Server

from .authentication.WebAuthnAuthentication import WebAuthnAuthentication
from .registration.WebAuthnRegistration import WebAuthnRegistration


class WebAuthnManager:
    def __init__(self):
        self.origins = [
            "https://localhost",
            "https://localhost:5000",
            "https://127.0.0.1",
            "https://[::1]"
        ]
        self.rp = PublicKeyCredentialRpEntity(self.origins[0], "localhost")
        self.server = Fido2Server(self.rp, attestation="none")
        self.server.allowed_origins = self.origins
        self.credentials = {}
        self.registration = WebAuthnRegistration(self.server, self.credentials)
        self.authentication = WebAuthnAuthentication(self.server, self.credentials)


class WebAuthnApp:
    def __init__(self):
        template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
        self.app = Flask(__name__, template_folder=template_dir)
        self.app.secret_key = os.urandom(32)
        self.webauthn_manager = WebAuthnManager()

        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/register/begin', methods=['POST'])
        def register_begin():
            username = request.json['username']
            options, state = self.webauthn_manager.registration.begin(username)
            session['register_state'] = state
            return options

        @self.app.route('/register/complete', methods=['POST'])
        def register_complete():
            state = session.pop('register_state')
            return self.webauthn_manager.registration.complete(state, request.json)

        @self.app.route('/authenticate/begin', methods=['POST'])
        def authenticate_begin():
            options, state = self.webauthn_manager.authentication.begin()
            session['auth_state'] = state
            return options

        @self.app.route('/authenticate/complete', methods=['POST'])
        def authenticate_complete():
            state = session.pop('auth_state')
            return self.webauthn_manager.authentication.complete(state, request.json)
