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
import subprocess

from fido2.cose import ES256, RS256
from fido2.utils import websafe_decode, websafe_encode
from fido2.webauthn import (
    AttestationObject,
    CollectedClientData,
    PublicKeyCredentialParameters,
    PublicKeyCredentialType,
    PublicKeyCredentialUserEntity,
    UserVerificationRequirement,
)

from toy_web_auth_n.common.Credential import Credential
from toy_web_auth_n.common.WebAuthnBase import WebAuthnBase


def get_device_ip():
    """Get the device's IP address using ifconfig."""
    try:
        result = subprocess.run(['ifconfig'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'inet ' in line and '127.0.0.1' not in line:
                return line.split()[1]
    except Exception:
        pass
    return 'localhost'  # fallback


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
        logger = logging.getLogger(__name__)
        logger.info(f"Beginning registration process for username: {username}")

        # Generate user ID and create user entity
        user_id = os.urandom(32)
        user = PublicKeyCredentialUserEntity(
            id=user_id,
            name=username,
            display_name=username,
        )
        logger.debug(f"Created user entity - ID: {websafe_encode(user_id)}, Name: {username}")

        # Check if user already exists
        existing_user = self.db.credentials.find_one({'username': username})
        if existing_user:
            logger.warning(f"User {username} already has registered credentials")
            logger.debug(f"Existing credentials: {existing_user}")

        # Begin registration with the server
        logger.debug("Initiating server registration process")
        options, state = self.server.register_begin(
            user,
            user_verification=UserVerificationRequirement.PREFERRED
        )
        logger.debug(f"Server registration state: {state}")

        # Create registration options
        challenge = os.urandom(32)
        logger.debug(f"Generated challenge: {websafe_encode(challenge)}")

        registration_options = {
            'challenge': websafe_encode(challenge),
            'rp': {
                'id': get_device_ip(),
                'name': self.server.rp.name
            },
            'user': {
                'id': websafe_encode(user.id),
                'name': user.name,
                'displayName': user.display_name
            },
            'pubKeyCredParams': [
                {'type': 'public-key', 'alg': ES256.ALGORITHM},
                {'type': 'public-key', 'alg': RS256.ALGORITHM}
            ],
            'authenticatorSelection': {
                'authenticatorAttachment': 'cross-platform',
                'userVerification': 'preferred',  # Enable user verification
                'requireResidentKey': False  # Optional: True for resident keys
            },
            'hints': ['security-key']
        }

        # Update with server options
        server_options = self._serialize_fido2_data(options)
        if isinstance(server_options, dict):
            logger.debug(f"Incorporating additional server options: {server_options}")
            registration_options.update(server_options)

        # Remove extensions if present
        registration_options.pop('extensions', None)

        logger.info("Registration options prepared successfully")
        logger.debug(f"Final registration options: {registration_options}")

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
        logger = logging.getLogger(__name__)
        logger.info("Beginning registration completion process")
        logger.debug(f"Registration state: {state}")
        logger.debug(f"Received data: {data}")

        try:
            # Parse client data and attestation object
            logger.debug("Parsing client data and attestation object")
            client_data = CollectedClientData(
                websafe_decode(data['response']['clientDataJSON'])
            )
            attestation_object = AttestationObject(
                websafe_decode(data['response']['attestationObject'])
            )

            # Log security-relevant information
            logger.info(f"Client data origin: {client_data.origin}")
            logger.info(f"Client data type: {client_data.type}")
            logger.debug(f"Client data challenge: {websafe_encode(client_data.challenge)}")
            logger.debug(f"Attestation format: {attestation_object.fmt}")
            logger.debug(f"Attestation statement: {attestation_object.att_stmt}")

            # Complete registration with server
            logger.debug("Completing server registration")
            auth_data = self.server.register_complete(
                state,
                data
            )

            # Extract credential information
            credential_id = auth_data.credential_data.credential_id # type: ignore
            public_key = auth_data.credential_data.public_key # type: ignore
            sign_count = getattr(auth_data, 'sign_count', 0)

            logger.debug(f"Credential ID: {websafe_encode(credential_id)}")
            logger.debug(f"Initial sign count: {sign_count}")
            logger.debug(f"Auth data flags: {auth_data.flags}")
            logger.info(f"User present: {auth_data.is_user_present()}")
            logger.info(f"User verified: {auth_data.is_user_verified()}")

            # Prepare credential dictionary
            credential_dict = {
                'type': 'public-key',
                'id': credential_id,
                'public_key': public_key,
                'sign_count': sign_count,
            }

            # Serialize public key for storage
            serialized_public_key = Credential.serialize_public_key(
                credential_dict['public_key']
            )
            logger.debug(f"Public key type: {type(credential_dict['public_key'])}")
            logger.debug(f"Serialized public key: {serialized_public_key}")

            # Prepare MongoDB document
            mongo_credential_dict = {
                'type': credential_dict['type'],
                'id': websafe_encode(credential_dict['id']),
                'public_key': serialized_public_key,
                'sign_count': credential_dict['sign_count'],
                'username': data['user']['name'],
                'userId': data['user']['id'],
                'displayName': data['user']['displayName'],
            }

            # Store credential in database
            logger.debug("Storing credential in database")
            self.db.credentials.insert_one(mongo_credential_dict)

            # Log successful registration
            logger.info("Successfully registered new credential:")
            logger.info(f"  Username: {data['user']['name']}")
            logger.info(f"  Credential ID: {websafe_encode(credential_dict['id'])}")
            logger.info(f"  Initial sign count: {credential_dict['sign_count']}")

            return json.dumps({
                'status': 'success',
                'credential_id': websafe_encode(credential_id),
                'user_id': mongo_credential_dict['id'],
                'username': mongo_credential_dict['username'],
            })

        except Exception as e:
            logger.error(
                f"Registration completion failed: {str(e)}",
                exc_info=True
            )
            logger.debug(f"Failed registration data: {data}")
            return json.dumps({
                'status': 'error',
                'message': str(e)
            }), 400
