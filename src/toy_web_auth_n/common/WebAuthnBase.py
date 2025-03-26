"""
WebAuthn Base Module

This module provides the foundation for WebAuthn operations, including:
1. Common initialization for WebAuthn components
2. Shared utilities for data serialization
3. Base functionality for registration and authentication
4. Database connection management

Key Features:
- Standardized initialization for WebAuthn components
- FIDO2 server instance management
- MongoDB database integration
- Data serialization utilities for WebAuthn operations

Dependencies:
    - fido2.utils: Utility functions for WebAuthn operations
    - pymongo: MongoDB database operations
"""

from fido2.utils import websafe_encode


class WebAuthnBase:
    """
    Base class for WebAuthn operations providing common functionality.

    This class provides:
    1. Common initialization for WebAuthn components
    2. Shared utilities for data serialization
    3. Base functionality for registration and authentication

    Attributes:
        server (Fido2Server): The FIDO2 server instance
        db (pymongo.database.Database): MongoDB database connection
    """

    def __init__(self, server, db):
        """
        Initialize the WebAuthn base component.

        Args:
            server (Fido2Server): The FIDO2 server instance to use
            db (pymongo.database.Database): MongoDB database connection
        """
        self.server = server
        self.db = db

    def _serialize_fido2_data(self, data):
        """
        Serialize FIDO2 data structures for JSON transmission.

        This method handles:
        - Binary data conversion to base64URL
        - Complex object serialization
        - Nested data structures

        Args:
            data: The data to serialize (can be bytes, dict, list, or object)

        Returns:
            The serialized data suitable for JSON encoding
        """
        if isinstance(data, bytes):
            return websafe_encode(data)
        elif isinstance(data, dict):
            return {
                key: self._serialize_fido2_data(value)
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [self._serialize_fido2_data(item) for item in data]
        elif hasattr(data, '__dict__'):
            # Convert object to dictionary and serialize its contents
            return self._serialize_fido2_data(vars(data))
        return data
