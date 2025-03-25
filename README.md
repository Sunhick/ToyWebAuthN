# ToyWebAuthN

A demonstration implementation of WebAuthn in Python using Flask. This project provides a simple way to understand and experiment with WebAuthn authentication.

## Features

- WebAuthn Registration and Authentication
- HTTPS support with automatic certificate generation
- In-memory credential storage
- Simple web interface
- Comprehensive documentation

## Quick Start

1. Install mkcert:
```bash
# On macOS
brew install mkcert

# On Ubuntu/Debian
sudo apt install mkcert

# On Windows (using Chocolatey)
choco install mkcert
```

2. Install ToyWebAuthN:
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install the package
pip install -e .

# Generate SSL certificates
toy-webauthn-generate-certs
```

3. Start the server:
```bash
toy-webauthn
```

4. Open your browser and navigate to:
```
https://localhost:5000
```

## Documentation

For detailed documentation, see [docs/README.md](docs/README.md).

## Development

### Prerequisites

- Python 3.7 or higher
- mkcert
- virtualenv or venv

### Setup Development Environment

1. Clone the repository:
```bash
git clone [repository-url]
cd ToyWebAuthN
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

4. Generate certificates:
```bash
toy-webauthn-generate-certs
```

### Running Tests

```bash
pytest
```

## Security Notes

This is a demonstration implementation and should not be used in production without significant security enhancements:

1. The credential storage is in-memory only
2. No user verification is required
3. Limited origin validation
4. No rate limiting
5. No persistent storage

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Add your license information here]
