"""
WebAuthn Registration Module

This module handles the WebAuthn registration process, including:
1. Creating new user credentials
2. Managing attestation data
3. Storing registered credentials
4. Handling registration state

The registration flow consists of two main steps:
1. begin() - Initiates registration by creating a new user entity and challenge
2. complete() - Processes the authenticator's response and stores the credential

Key Features:
- Generates random user IDs for new registrations
- Supports multiple credential algorithms (ES256, RS256)
- Configures authenticator selection criteria
- Manages credential storage in MongoDB

Dependencies:
    - fido2.webauthn: Core WebAuthn functionality
    - fido2.utils: Utility functions for WebAuthn operations
    - WebAuthnBase: Base class for WebAuthn operations
    - Credential: Credential data management
"""

import json
import logging
import os

from fido2.utils import websafe_encode, websafe_decode
from fido2.webauthn import (
    AttestationObject,
    CollectedClientData,
    PublicKeyCredentialUserEntity,
    UserVerificationRequirement,
)

from toy_web_auth_n.common.Credential import Credential
from toy_web_auth_n.common.WebAuthnBase import WebAuthnBase


class WebAuthnRegistration(WebAuthnBase):
    """
    Handles WebAuthn registration operations.

    This class manages the registration process, including user entity creation,
    challenge generation, and credential storage.
    """

    def begin(self, username):
        """
        Begin the registration process for a new user.

        Args:
            username (str): The username to register

        Returns:
            tuple: (JSON options for the client, state for the server)
            The JSON options include challenge and registration parameters.
        """
        user_id = os.urandom(32)
        user = PublicKeyCredentialUserEntity(
            id=user_id,
            name=username,
            display_name=username,
        )
        logging.info(f"username: {username} userId: {user_id}")

        options, state = self.server.register_begin(
            user,
            user_verification=UserVerificationRequirement.PREFERRED
        )

        # Create a base dictionary for options
        registration_options = {
            'challenge': websafe_encode(os.urandom(32)),
            'rp': {
                'id': 'localhost',
                'name': self.server.rp.name
            },
            'user': {
                'id': websafe_encode(user.id),
                'name': user.name,
                'displayName': user.display_name
            },
            'pubKeyCredParams': [
                {'type': 'public-key', 'alg': -7},  # ES256
                {'type': 'public-key', 'alg': -257}  # RS256
            ],
            'authenticatorSelection': {
                'authenticatorAttachment': 'cross-platform',
                'userVerification': 'preferred',  # Enable user verification
                'requireResidentKey': False  # Optional: True for resident keys
            }
        }

        # Update with any additional options from the server
        server_options = self._serialize_fido2_data(options)
        if isinstance(server_options, dict):
            registration_options.update(server_options)

        # Remove extensions if present
        registration_options.pop('extensions', None)

        return json.dumps({'publicKey': registration_options}), state

    def complete(self, state, data):
        """
        Complete the registration process by processing the authenticator response.

        Args:
            state (dict): The server state from the begin() call
            data (dict): The authenticator's response data

        Returns:
            str: JSON response indicating success or failure
            May include a 400 status code if verification fails
        """
        try:
            client_data = CollectedClientData(
                websafe_decode(data['response']['clientDataJSON'])
            )
            attestation_object = AttestationObject(
                websafe_decode(data['response']['attestationObject'])
            )

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

            serialized_public_key = Credential.serialize_public_key(
                credential_dict['public_key']
            )
            logging.info(f"raw public key: {credential_dict['public_key']}")
            logging.info(f"type public key: {type(credential_dict['public_key'])}")
            logging.info(f"serialized key: {serialized_public_key}")

            mongo_credential_dict = {
                'type': credential_dict['type'],
                'id': websafe_encode(credential_dict['id']),
                'public_key': serialized_public_key,
                'sign_count': credential_dict['sign_count'],
                'username': data['user']['name'],
                'userId': data['user']['id'],
                'displayName': data['user']['displayName'],
            }
            self.db.credentials.insert_one(mongo_credential_dict)

            logging.info("Stored credential:")
            logging.info(f"  Type: {credential_dict['type']}")
            logging.info(f"  ID: {websafe_encode(credential_dict['id'])}")
            logging.info(f"  Public Key: {credential_dict['public_key']}")
            logging.info(f"  Sign Count: {credential_dict['sign_count']}")

            return json.dumps({
                'status': 'success',
                'credential_id': websafe_encode(credential_id),
                'user_id': mongo_credential_dict['id'],
                'username': mongo_credential_dict['username'],
            })

        except Exception as e:
            logging.error(
                f"Error in register_complete: {str(e)}",
                exc_info=True
            )
            return json.dumps({
                'status': 'error',
                'message': str(e)
            }), 400
