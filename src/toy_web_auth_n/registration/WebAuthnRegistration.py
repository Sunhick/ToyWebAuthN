import json
import os
import logging
from fido2.webauthn import (
    PublicKeyCredentialUserEntity,
    AttestationObject,
    CollectedClientData
)
from fido2.utils import websafe_encode, websafe_decode

from ..common.WebAuthnBase import WebAuthnBase


class WebAuthnRegistration(WebAuthnBase):
    def begin(self, username):
        user_id = os.urandom(32)
        user = PublicKeyCredentialUserEntity(
            id=user_id,
            name=username,
            display_name=username,
        )

        options, state = self.server.register_begin(user)
        serialized_options = self._serialize_fido2_data(options)

        if 'challenge' not in serialized_options:
            serialized_options['challenge'] = websafe_encode(os.urandom(32))

        logging.info(f"Generated challenge: {state['challenge']}")

        serialized_options['pubKeyCredParams'] = [
            {'type': 'public-key', 'alg': -7},  # ES256
            {'type': 'public-key', 'alg': -257}  # RS256
        ]

        serialized_options['authenticatorSelection'] = {
            'authenticatorAttachment': 'cross-platform',
            'userVerification': 'discouraged'
        }

        serialized_options['rp'] = {'id': 'localhost', 'name': self.server.rp.name}

        serialized_options['user'] = {
            'id': websafe_encode(user.id),
            'name': user.name,
            'displayName': user.display_name
        }

        if 'extensions' in serialized_options:
            del serialized_options['extensions']

        return json.dumps({'publicKey': serialized_options}), state

    def complete(self, state, data):
        try:
            client_data = CollectedClientData(websafe_decode(data['response']['clientDataJSON']))
            attestation_object = AttestationObject(websafe_decode(data['response']['attestationObject']))

            logging.info(f"Received origin: {client_data.origin}")
            logging.debug(f"Attestation object: {attestation_object}")

            auth_data = self.server.register_complete(
                state,
                client_data,
                attestation_object
            )

            credential_id = auth_data.credential_data.credential_id
            public_key = auth_data.credential_data.public_key
            sign_count = getattr(auth_data, 'sign_count', 0)

            credential_dict = {
                'type': 'public-key',
                'id': credential_id,
                'public_key': public_key,
                'sign_count': sign_count,
            }

            self.credentials[websafe_encode(credential_id)] = credential_dict

            logging.info("Stored credential:")
            logging.info(f"  Type: {credential_dict['type']}")
            logging.info(f"  ID: {websafe_encode(credential_dict['id'])}")
            logging.info(f"  Public Key: {credential_dict['public_key']}")
            logging.info(f"  Sign Count: {credential_dict['sign_count']}")

            return json.dumps({
                'status': 'success',
                'credential_id': websafe_encode(credential_id)
            })

        except Exception as e:
            logging.error(f"Error in register_complete: {str(e)}", exc_info=True)
            return json.dumps({'status': 'error', 'message': str(e)}), 400
