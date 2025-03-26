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

from typing import Dict, Any
import cbor2
from fido2.cose import CoseKey


class Credential:
    """
    Represents a WebAuthn credential with serialization capabilities.

    This class manages credential data and provides methods for serializing and
    deserializing public keys using CBOR encoding.

    Attributes:
        credential_id (bytes): The unique identifier for this credential
        public_key (CoseKey): The public key associated with this credential
        sign_count (int): The number of times this credential has been used
    """

    def __init__(self, credential_dict: Dict[str, Any]) -> None:
        """
        Initialize a new credential from a dictionary.

        Args:
            credential_dict (dict): Dictionary containing credential data with keys:
                - id: The credential identifier
                - public_key: The public key data
                - sign_count: The number of times the credential has been used
        """
        self.credential_id: bytes = credential_dict['id']
        self.public_key: CoseKey = credential_dict['public_key']
        self.sign_count: int = credential_dict['sign_count']

    @staticmethod
    def deserialize_public_key(public_key_str: bytes) -> CoseKey:
        """
        Convert a CBOR-encoded public key string back to a CoseKey object.

        Args:
            public_key_str (bytes): CBOR-encoded public key data

        Returns:
            CoseKey: The deserialized public key object
        """
        p = cbor2.loads(public_key_str)
        return CoseKey.parse(p)

    @staticmethod
    def serialize_public_key(public_key: CoseKey) -> bytes:
        """
        Convert a CoseKey public key object to CBOR-encoded bytes.

        Args:
            public_key (CoseKey): The public key to serialize

        Returns:
            bytes: CBOR-encoded public key data
        """
        return cbor2.dumps(public_key)
