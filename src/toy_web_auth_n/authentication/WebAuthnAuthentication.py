import json
import logging
from fido2.webauthn import (
    CollectedClientData,
    AuthenticatorData
)
from fido2.utils import websafe_encode, websafe_decode
from fido2.cose import ES256, RS256

from ..common.WebAuthnBase import WebAuthnBase
from ..common.Credential import Credential

class WebAuthnAuthentication(WebAuthnBase):
    def begin(self):
        if not self.credentials:
            return json.dumps({'status': 'error', 'message': 'No credentials registered'}), 400

        formatted_credentials = [
            {
                'type': 'public-key',
                'id': cred['id'],
            }
            for cred in self.credentials.values()
        ]

        options, state = self.server.authenticate_begin(formatted_credentials)

        logging.info(f"Generated challenge: {state['challenge']}")

        encoded_challenge = state['challenge']

        public_key_credential_request_options = {
            'challenge': encoded_challenge,
            'allowCredentials': [
                {
                    'type': 'public-key',
                    'id': websafe_encode(cred['id'])
                }
                for cred in formatted_credentials
            ],
            'timeout': getattr(options.public_key, 'timeout', 60000),
            'userVerification': getattr(options.public_key, 'user_verification', 'preferred'),
            'rpId': 'localhost'
        }

        logging.info(f"State stored in session: {state}")
        return json.dumps({'publicKey': public_key_credential_request_options}), state

    def complete(self, state, data):
        try:
            credential_id = websafe_decode(data['id'])
            client_data = CollectedClientData(websafe_decode(data['response']['clientDataJSON']))
            auth_data_raw = websafe_decode(data['response']['authenticatorData'])
            auth_data = AuthenticatorData(auth_data_raw)
            signature = websafe_decode(data['response']['signature'])

            logging.info(f"Received origin: {client_data.origin}")
            logging.info(f"Credential ID: {websafe_encode(credential_id)}")
            logging.debug(f"Client data: {client_data}")
            logging.debug(f"Auth data (raw): {auth_data_raw.hex()}")
            logging.info(f"Auth data rp_id_hash: {auth_data.rp_id_hash.hex()}")
            logging.info(f"Auth data flags: {auth_data.flags}")
            logging.info(f"Auth data counter: {auth_data.counter}")
            logging.info(f"User present: {auth_data.is_user_present()}")
            logging.info(f"User verified: {auth_data.is_user_verified()}")
            logging.info(f"Has extension data: {auth_data.has_extension_data()}")
            logging.debug(f"Signature: {signature.hex()}")

            received_challenge = websafe_encode(client_data.challenge)
            stored_challenge = state['challenge']
            logging.info(f"Received challenge: {received_challenge}")
            logging.info(f"Stored challenge: {stored_challenge}")
            logging.info(f"Challenges match: {received_challenge == stored_challenge}")

            credential_dict = self.credentials[websafe_encode(credential_id)]
            credential = Credential(credential_dict)

            self.server.authenticate_complete(
                state,
                [credential],
                credential_id,
                client_data,
                auth_data,
                signature
            )

            credential_dict['sign_count'] = auth_data.counter
            logging.info(f"Updated sign count: {auth_data.counter}")

            return json.dumps({'status': 'success'})
        except Exception as e:
            logging.error(f"Error in authenticate_complete: {str(e)}", exc_info=True)
            return json.dumps({'status': 'error', 'message': str(e)}), 400
