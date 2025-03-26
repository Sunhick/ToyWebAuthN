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
        credentials (dict): Shared credential storage
    """

    def __init__(self, server, db):
        """
        Initialize the WebAuthn base component.

        Args:
            server (Fido2Server): The FIDO2 server instance to use
            credentials (dict): Shared dictionary for credential storage
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
            return {key: self._serialize_fido2_data(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._serialize_fido2_data(item) for item in data]
        elif hasattr(data, '__dict__'):
            return self._serialize_fido2_data(data.__dict__)
        return str(data)
