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

from fido2.utils import websafe_encode, websafe_decode
from fido2.webauthn import (
    AuthenticatorData,
    CollectedClientData,
    UserVerificationRequirement,
)

from toy_web_auth_n.common.Credential import Credential
from toy_web_auth_n.common.WebAuthnBase import WebAuthnBase


class WebAuthnAuthentication(WebAuthnBase):
    """
    Handles WebAuthn authentication operations.

    This class manages the authentication process, including challenge generation,
    response verification, and credential state updates.
    """

    def begin(self, username):
        """
        Begin the authentication process for a user.

        Args:
            username (str): The username to authenticate

        Returns:
            tuple: (JSON options for the client, state for the server)
            The JSON options include challenge and allowed credentials.
            May also return a 400 error response if validation fails.
        """
        logger = logging.getLogger(__name__)
        logger.info(f"Beginning authentication process for username: {username}")

        # Validate username
        if not username:
            logger.error("Authentication attempt with empty username")
            return json.dumps({
                'status': 'error',
                'message': 'No username provided'
            }), 400

        # Find user's credentials
        logger.debug(f"Looking up credentials for user: {username}")
        credentials = list(self.db.credentials.find({'username': username}))
        if not credentials:
            logger.warning(f"No credentials found for user: {username}")
            return json.dumps({
                'status': 'error',
                'message': 'No credentials registered'
            }), 400

        logger.info(f"Found {len(credentials)} registered credential(s) for user: {username}")
        logger.debug(f"Registered credentials: {credentials}")

        # Format credentials for the authenticator
        formatted_credentials = [
            {
                'type': 'public-key',
                'id': websafe_decode(cred['id']),
            }
            for cred in credentials
        ]
        logger.debug(f"Formatted credentials for authenticator: {formatted_credentials}")

        # Begin authentication with server
        logger.debug("Initiating server authentication process")
        options, state = self.server.authenticate_begin(
            formatted_credentials,
            user_verification=UserVerificationRequirement.PREFERRED
        )

        # Log challenge and state information
        logger.info(f"Generated challenge: {state['challenge']}")
        logger.debug(f"Authentication state: {state}")

        encoded_challenge = state['challenge']

        # Prepare authentication options
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
            'userVerification': 'preferred',  # Enable user verification
            'rpId': 'localhost'
        }

        logger.debug(f"Authentication options: {public_key_credential_request_options}")
        logger.info("Authentication options prepared successfully")

        return json.dumps({
            'publicKey': public_key_credential_request_options
        }), state

    def complete(self, state, data):
        """
        Complete the authentication process by verifying the authenticator response.

        Args:
            state (dict): The server state from the begin() call
            data (dict): The authenticator's response data

        Returns:
            str: JSON response indicating success or failure
            May include a 400 status code if verification fails
        """
        logger = logging.getLogger(__name__)
        logger.info("Beginning authentication completion process")
        logger.debug(f"Authentication state: {state}")
        logger.debug(f"Received data: {data}")

        try:
            # Parse credential data
            credential_id = websafe_decode(data['id'])
            logger.debug(f"Processing credential ID: {websafe_encode(credential_id)}")

            # Parse client data
            logger.debug("Parsing client data")
            client_data = CollectedClientData(
                websafe_decode(data['response']['clientDataJSON'])
            )
            logger.debug(f"Client data type: {client_data.type}")
            logger.info(f"Client data origin: {client_data.origin}")

            # Parse authenticator data
            logger.debug("Parsing authenticator data")
            auth_data_raw = websafe_decode(data['response']['authenticatorData'])
            auth_data = AuthenticatorData(auth_data_raw)

            # Parse signature
            signature = websafe_decode(data['response']['signature'])
            logger.debug(f"Signature (hex): {signature.hex()}")

            # Log security-relevant information
            logger.info("Security verification details:")
            logger.info(f"  RP ID hash: {auth_data.rp_id_hash.hex()}")
            logger.info(f"  User present: {auth_data.is_user_present()}")
            logger.info(f"  User verified: {auth_data.is_user_verified()}")
            logger.info(f"  Has extension data: {auth_data.has_extension_data()}")
            logger.debug(f"  Auth data flags: {auth_data.flags}")
            logger.debug(f"  Counter value: {auth_data.counter}")

            # Verify challenge
            received_challenge = websafe_encode(client_data.challenge)
            stored_challenge = state['challenge']
            logger.debug("Challenge verification:")
            logger.debug(f"  Received: {received_challenge}")
            logger.debug(f"  Expected: {stored_challenge}")
            logger.info(f"  Match: {received_challenge == stored_challenge}")

            # Retrieve credential from database
            logger.debug("Looking up credential in database")
            credential_dict = self.db.credentials.find_one({
                'id': websafe_encode(credential_id)
            })
            if not credential_dict:
                logger.error(f"Credential not found: {websafe_encode(credential_id)}")
                raise ValueError("Credential not found")

            # Prepare credential for verification
            logger.debug("Preparing credential for verification")
            credential_dict['public_key'] = Credential.deserialize_public_key(
                credential_dict['public_key']
            )
            credential_dict['id'] = websafe_decode(credential_dict['id'])
            credential = Credential(credential_dict)
            logger.debug(f"Previous sign count: {credential.sign_count}")

            # Complete authentication with server
            logger.debug("Completing server authentication")
            self.server.authenticate_complete(
                state,
                [credential],
                data
            )

            # Verify user presence and verification
            if not auth_data.is_user_present() or not auth_data.is_user_verified():
                logger.warning("User verification requirements not met")
                logger.debug(f"User present: {auth_data.is_user_present()}")
                logger.debug(f"User verified: {auth_data.is_user_verified()}")
                raise ValueError("User verification required but not performed")

            # Update sign count
            logger.debug(f"Updating sign count from {credential.sign_count} to {auth_data.counter}")
            if auth_data.counter <= credential.sign_count:
                logger.warning(
                    f"Possible authenticator cloning detected! "
                    f"Counter not greater than previous value: "
                    f"{auth_data.counter} <= {credential.sign_count}"
                )

            self.db.credentials.update_one(
                {'id': websafe_encode(credential_id)},
                {'$set': {'sign_count': auth_data.counter}}
            )

            logger.info("Authentication completed successfully")
            logger.info(f"New sign count: {auth_data.counter}")

            return json.dumps({'status': 'success'})

        except Exception as e:
            logger.error(
                f"Authentication completion failed: {str(e)}",
                exc_info=True
            )
            logger.debug(f"Failed authentication data: {data}")
            return json.dumps({
                'status': 'error',
                'message': str(e)
            }), 400
