# ToyWebAuthN Documentation

ToyWebAuthN is a demonstration implementation of WebAuthn in Python using Flask. It provides a simple way to understand and experiment with WebAuthn authentication.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Architecture](#architecture)
4. [API Reference](#api-reference)
5. [Development Guide](#development-guide)
6. [Security Considerations](#security-considerations)

## Installation

### Prerequisites

- Python 3.7 or higher
- mkcert (for SSL certificates)

### Install mkcert

```bash
# On macOS
brew install mkcert

# On Ubuntu/Debian
sudo apt install mkcert

# On Windows (using Chocolatey)
choco install mkcert
```

### Install ToyWebAuthN

```bash
# Clone the repository
git clone [repository-url]
cd ToyWebAuthN

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install the package in development mode
pip install -e .

# Generate SSL certificates
toy-webauthn-generate-certs
```

## Quick Start

1. Start the server:
```bash
toy-webauthn
```

2. Open your browser and navigate to:
```
https://localhost:5000
```

3. Click "Register" to register a new credential
4. Click "Authenticate" to verify the credential

## Architecture

ToyWebAuthN follows a modular architecture with clear separation of concerns:

### Core Components

1. **WebAuthnManager** (`WebAuthnManager.py`)
   - Manages WebAuthn server configuration
   - Handles credential storage
   - Coordinates registration and authentication

2. **WebAuthnRegistration** (`registration/WebAuthNRegistration.py`)
   - Handles credential registration process
   - Manages attestation verification
   - Stores new credentials

3. **WebAuthnAuthentication** (`authentication/WebAuthnAuthentication.py`)
   - Handles authentication process
   - Verifies assertions
   - Manages credential counters

4. **WebAuthnBase** (`common/WebAuthnBase.py`)
   - Base class with shared functionality
   - Handles FIDO2 data serialization

### Flow Diagrams

#### Registration Flow
```
User -> Browser -> /register/begin -> Server
Server -> Browser -> WebAuthn API -> Authenticator
Authenticator -> Browser -> /register/complete -> Server
Server -> Browser -> User
```

#### Authentication Flow
```
User -> Browser -> /authenticate/begin -> Server
Server -> Browser -> WebAuthn API -> Authenticator
Authenticator -> Browser -> /authenticate/complete -> Server
Server -> Browser -> User
```

## API Reference

### Registration Endpoints

#### POST /register/begin
Initiates the registration process.

Request:
```json
{
    "username": "string"
}
```

Response:
```json
{
    "publicKey": {
        "challenge": "base64url-encoded-challenge",
        "rp": {
            "name": "localhost",
            "id": "localhost"
        },
        "user": {
            "id": "base64url-encoded-userid",
            "name": "username",
            "displayName": "username"
        },
        "pubKeyCredParams": [
            {
                "type": "public-key",
                "alg": -7
            },
            {
                "type": "public-key",
                "alg": -257
            }
        ]
    }
}
```

#### POST /register/complete
Completes the registration process.

Request:
```json
{
    "id": "credential-id",
    "rawId": "base64url-encoded-raw-id",
    "response": {
        "attestationObject": "base64url-encoded-attestation",
        "clientDataJSON": "base64url-encoded-client-data"
    },
    "type": "public-key"
}
```

Response:
```json
{
    "status": "success",
    "credential_id": "base64url-encoded-credential-id"
}
```

### Authentication Endpoints

#### POST /authenticate/begin
Initiates the authentication process.

Response:
```json
{
    "publicKey": {
        "challenge": "base64url-encoded-challenge",
        "allowCredentials": [
            {
                "type": "public-key",
                "id": "base64url-encoded-credential-id"
            }
        ],
        "timeout": 60000,
        "userVerification": "preferred",
        "rpId": "localhost"
    }
}
```

#### POST /authenticate/complete
Completes the authentication process.

Request:
```json
{
    "id": "credential-id",
    "rawId": "base64url-encoded-raw-id",
    "response": {
        "authenticatorData": "base64url-encoded-auth-data",
        "clientDataJSON": "base64url-encoded-client-data",
        "signature": "base64url-encoded-signature",
        "userHandle": "base64url-encoded-user-handle"
    },
    "type": "public-key"
}
```

Response:
```json
{
    "status": "success"
}
```

## Development Guide

### Project Structure
```
ToyWebAuthN/
├── src/
│   └── toy_web_auth_n/
│       ├── authentication/
│       │   └── WebAuthnAuthentication.py
│       ├── common/
│       │   └── WebAuthnBase.py
│       ├── registration/
│       │   └── WebAuthNRegistration.py
│       ├── static/
│       │   ├── css/
│       │   └── js/
│       ├── templates/
│       │   └── index.html
│       ├── WebAuthnManager.py
│       └── main.py
├── tests/
├── docs/
├── setup.py
└── README.md
```

### Adding New Features

1. Create a new module in the appropriate directory
2. Inherit from WebAuthnBase if needed
3. Add routes in WebAuthnManager.py
4. Update documentation
5. Add tests

### Running Tests

```bash
pip install -e ".[dev]"
pytest
```

## Security Considerations

1. **SSL Certificates**
   - Always use HTTPS in production
   - Keep private keys secure
   - Regularly rotate certificates

2. **Credential Storage**
   - Current implementation uses in-memory storage
   - Production systems should use secure persistent storage
   - Encrypt sensitive data at rest

3. **User Verification**
   - Current implementation uses "discouraged" setting
   - Production systems should require user verification
   - Consider biometric requirements

4. **Origin Validation**
   - Verify correct origins
   - Prevent cross-site attacks
   - Use secure cookie settings

5. **Rate Limiting**
   - Implement rate limiting for registration
   - Protect against brute force attacks
   - Monitor for suspicious activity

## License

[Add your license information here]
