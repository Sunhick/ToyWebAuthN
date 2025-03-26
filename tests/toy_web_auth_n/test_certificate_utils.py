"""
Tests for certificate utility functions.
"""
import os
import pytest
from unittest.mock import patch

from toy_web_auth_n.main import check_certificates


class TestCertificateUtils:
    def test_check_certificates_existing(self, temp_cert_dir):
        """Test certificate check with valid certificates."""
        # Create mock certificate files
        cert_path = temp_cert_dir / "localhost.pem"
        key_path = temp_cert_dir / "localhost-key.pem"
        cert_path.touch()
        key_path.touch()

        with patch('os.path.expanduser', return_value=str(temp_cert_dir)):
            result_cert, result_key = check_certificates()
            assert os.path.exists(result_cert)
            assert os.path.exists(result_key)

    def test_check_certificates_missing(self, temp_cert_dir):
        """Test error handling for missing certificates."""
        with patch('os.path.expanduser', return_value=str(temp_cert_dir)):
            with pytest.raises(SystemExit) as exc_info:
                check_certificates()
            assert exc_info.value.code == 1

    def test_check_certificates_missing_cert(self, temp_cert_dir):
        """Test error handling when only key file exists."""
        key_path = temp_cert_dir / "localhost-key.pem"
        key_path.touch()

        with patch('os.path.expanduser', return_value=str(temp_cert_dir)):
            with pytest.raises(SystemExit) as exc_info:
                check_certificates()
            assert exc_info.value.code == 1

    def test_check_certificates_missing_key(self, temp_cert_dir):
        """Test error handling when only cert file exists."""
        cert_path = temp_cert_dir / "localhost.pem"
        cert_path.touch()

        with patch('os.path.expanduser', return_value=str(temp_cert_dir)):
            with pytest.raises(SystemExit) as exc_info:
                check_certificates()
            assert exc_info.value.code == 1

    def test_check_certificates_invalid_path(self):
        """Test error handling for invalid certificate paths."""
        with patch('os.path.expanduser', return_value="/nonexistent/path"):
            with pytest.raises(SystemExit) as exc_info:
                check_certificates()
            assert exc_info.value.code == 1
