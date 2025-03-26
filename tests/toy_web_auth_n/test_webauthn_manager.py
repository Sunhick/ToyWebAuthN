"""
Tests for WebAuthnManager class.
"""
from unittest.mock import Mock, patch

import pytest

from toy_web_auth_n.WebAuthnManager import WebAuthnManager


class TestWebAuthnManager:
    def test_init_creates_valid_rp(self, webauthn_manager):
        """Test that initialization creates a valid Relying Party entity."""
        assert webauthn_manager.rp.id == "localhost"
        assert webauthn_manager.rp.name == "WebAuthN Demo"

    @pytest.mark.parametrize("origin", [
        "https://localhost",
        "https://localhost:5000",
        "https://127.0.0.1",
        "https://[::1]"
    ])
    def test_verify_origin_with_valid_origins(self, webauthn_manager, origin):
        """Test that valid origins are accepted."""
        assert webauthn_manager.verify_origin(origin) is True

    @pytest.mark.parametrize("origin", [
        "http://localhost",  # Wrong protocol
        "https://evil.com",  # Wrong domain
        "https://localhost:8080",  # Wrong port
        "https://127.0.0.2",  # Wrong IP
        "",  # Empty string
        None,  # None value
    ])
    def test_verify_origin_with_invalid_origins(self, webauthn_manager, origin):
        """Test that invalid origins are rejected."""
        assert webauthn_manager.verify_origin(origin) is False

    def test_init_with_custom_origins(self, mock_db):
        """Test initialization with custom origins."""
        custom_origins = ["https://custom.domain"]
        with patch.object(WebAuthnManager, 'origins', custom_origins):
            manager = WebAuthnManager(mock_db)
            assert manager.verify_origin("https://custom.domain") is True
            assert manager.verify_origin("https://localhost") is False

    def test_verify_origin_with_malformed_url(self, webauthn_manager):
        """Test origin verification with malformed URL."""
        malformed_origins = [
            "not-a-url",
            "ftp://localhost",
            "https:/localhost",
            "https://localhost/extra/path",
            "https://localhost?query=param",
            "https://localhost#fragment"
        ]
        for origin in malformed_origins:
            assert webauthn_manager.verify_origin(origin) is False
            assert webauthn_manager.verify_origin(origin) is False
