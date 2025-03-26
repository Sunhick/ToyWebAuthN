"""
WebAuthn Authentication Module

This module handles the WebAuthn authentication process, including:
1. Generating authentication challenges
2. Verifying authenticator responses
3. Managing credential state during authentication
4. Updating credential sign counts

The authentication flow consists of two main steps:
1. begin() - Initiates authentication by generating a challenge
2. complete() - Verifies the authenticator's response to the challenge

Dependencies:
    - fido2.webauthn: Core WebAuthn functionality
    - fido2.utils: Utility functions for WebAuthn operations
    - WebAuthnBase: Base class for WebAuthn operations
    - Credential: Credential data management
"""

import json
import logging
from fido2.webauthn import (
    CollectedClientData,
    AuthenticatorData
)
from fido2.utils import websafe_encode, websafe_decode

from toy_web_auth_n.common.WebAuthnBase import WebAuthnBase
from toy_web_auth_n.common.Credential import Credential

class WebAuthnAuthentication(WebAuthnBase):
    def begin(self, username):
        if not username:
            return json.dumps({'status': 'error', 'message': 'No username provided'}), 400

        credentials = list(self.db.credentials.find({'username': username}))
        if not credentials:
            return json.dumps({'status': 'error', 'message': 'No credentials registered'}), 400

        formatted_credentials = [
            {
                'type': 'public-key',
                'id': websafe_decode(cred['id']),
            }
            for cred in credentials
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

            credential_dict = self.db.credentials.find_one({'id': websafe_encode(credential_id)})
            if not credential_dict:
                raise ValueError("Credential not found")

            credential_dict['public_key'] = Credential.deserialize_public_key(credential_dict['public_key'])
            credential_dict['id'] = websafe_decode(credential_dict['id'])
            credential = Credential(credential_dict)

            self.server.authenticate_complete(
                state,
                [credential],
                credential_id,
                client_data,
                auth_data,
                signature
            )

            self.db.credentials.update_one(
                {'id': websafe_encode(credential_id)},
                {'$set': {'sign_count': auth_data.counter}}
            )

            logging.info(f"Updated sign count: {auth_data.counter}")

            return json.dumps({'status': 'success'})
        except Exception as e:
            logging.error(f"Error in authenticate_complete: {str(e)}", exc_info=True)
            return json.dumps({'status': 'error', 'message': str(e)}), 400
