class Credential:
    def __init__(self, credential_dict):
        self.credential_id = credential_dict['id']
        self.public_key = credential_dict['public_key']
        self.sign_count = credential_dict['sign_count']
