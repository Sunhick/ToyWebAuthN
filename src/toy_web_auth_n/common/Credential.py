"""
Credential Data Management Module

This module provides functionality for managing WebAuthn credential data, including:
1. Credential object representation
2. Public key serialization and deserialization
3. Credential data structure standardization

Key Features:
- CBOR encoding/decoding for public keys
- Credential attribute management
- Support for COSE key formats

Dependencies:
    - cbor2: CBOR encoding/decoding
    - fido2.cose: COSE key operations
"""

import cbor2
from fido2.cose import CoseKey


class Credential:
    def __init__(self, credential_dict):
        self.credential_id = credential_dict['id']
        self.public_key = credential_dict['public_key']
        self.sign_count = credential_dict['sign_count']

    @staticmethod
    def deserialize_public_key(public_key_str):
        p = cbor2.loads(public_key_str)
        return CoseKey.parse(p)

    @staticmethod
    def serialize_public_key(public_key):
        return cbor2.dumps(public_key)
