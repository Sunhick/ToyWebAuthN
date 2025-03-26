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
