from fido2.utils import websafe_encode

class WebAuthnBase:
    def __init__(self, server, credentials):
        self.server = server
        self.credentials = credentials

    def _serialize_fido2_data(self, data):
        if isinstance(data, bytes):
            return websafe_encode(data)
        elif isinstance(data, dict):
            return {key: self._serialize_fido2_data(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._serialize_fido2_data(item) for item in data]
        elif hasattr(data, '__dict__'):
            return self._serialize_fido2_data(data.__dict__)
        return str(data)
