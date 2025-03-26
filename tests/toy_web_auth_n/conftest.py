"""
Pytest fixtures for ToyWebAuthN tests.
"""
import os
from unittest.mock import Mock, patch

import pytest
from flask import Flask
from pymongo import MongoClient

from toy_web_auth_n.WebAuthnManager import WebAuthnManager, WebAuthnApp


@pytest.fixture
def mock_db():
    """Provide a mock MongoDB database."""
    db = Mock()
    # Add any necessary mock collections or methods
    db.credentials = Mock()
    db.credentials.find_one = Mock(return_value=None)
    db.credentials.insert_one = Mock()
    return db


@pytest.fixture
def mock_fido2_server():
    """Provide a mock FIDO2 server."""
    server = Mock()
    server.register_begin = Mock(return_value=({"publicKey": {}}, "state"))
    server.register_complete = Mock(return_value=True)
    server.authenticate_begin = Mock(return_value=({"publicKey": {}}, "state"))
    server.authenticate_complete = Mock(return_value=True)
    return server


@pytest.fixture
def mock_session(monkeypatch):
    """Provide a mock Flask session."""
    session_data = {}

    def mock_get(key, default=None):
        return session_data.get(key, default)

    def mock_pop(key, default=None):
        return session_data.pop(key, default)

    def mock_set(key, value):
        session_data[key] = value

    monkeypatch.setattr("flask.session.get", mock_get)
    monkeypatch.setattr("flask.session.pop", mock_pop)
    monkeypatch.setattr("flask.session.__setitem__", mock_set)

    return session_data


@pytest.fixture
def sample_credential():
    """Provide sample WebAuthn credential data."""
    return {
        "id": "credential123",
        "publicKey": "sample_public_key",
        "signCount": 0,
        "transports": ["usb", "nfc"],
        "attestation": "none",
        "username": "testuser"
    }


@pytest.fixture
def webauthn_manager(mock_db):
    """Provide an initialized WebAuthnManager instance."""
    with patch('fido2.server.Fido2Server') as mock_server:
        manager = WebAuthnManager(mock_db)
        manager.server = mock_server.return_value
        return manager


@pytest.fixture
def webauthn_app(mock_db):
    """Provide an initialized WebAuthnApp instance."""
    with patch('pymongo.MongoClient') as mock_client:
        mock_client.return_value = Mock()
        mock_client.return_value.__getitem__.return_value = mock_db

        app = WebAuthnApp()
        app.app.config['TESTING'] = True
        app.app.config['SECRET_KEY'] = 'test_secret_key'
        return app


@pytest.fixture
def test_client(webauthn_app):
    """Provide a Flask test client."""
    return webauthn_app.app.test_client()


@pytest.fixture
def temp_cert_dir(tmp_path):
    """Create a temporary certificate directory."""
    cert_dir = tmp_path / ".toy-webauthn-certs"
    cert_dir.mkdir()
    return cert_dir
