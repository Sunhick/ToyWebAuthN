"""
ToyWebAuthN - A playful WebAuthn implementation in Flask
"""

from toy_web_auth_n.authentication import WebAuthnAuthentication
from toy_web_auth_n.registration import WebAuthnRegistration
from toy_web_auth_n.common import WebAuthnBase, Credential
from toy_web_auth_n.WebAuthnManager import WebAuthnManager, WebAuthnApp

__version__ = "0.1.0"

__all__ = [
    'WebAuthnAuthentication',
    'WebAuthnRegistration',
    'WebAuthnBase',
    'Credential',
    'WebAuthnManager',
    'WebAuthnApp',
    '__version__'
]
