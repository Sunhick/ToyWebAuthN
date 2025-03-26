# ToyWebAuthN

A demonstration implementation of WebAuthn in Python using Flask. This project provides a simple way to understand and experiment with WebAuthn authentication.

## Features

- WebAuthn Registration and Authentication
- HTTPS support with automatic certificate generation
- MongoDB credential storage
- Simple web interface
- Comprehensive documentation
- PEP 8 compliant codebase
- Type hints and static type checking
- Automated testing with pytest

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

2. Install MongoDB:
```bash
# On macOS
brew tap mongodb/brew
brew install mongodb-community

# On Ubuntu/Debian
sudo apt install mongodb

# On Windows
# Download and install from https://www.mongodb.com/try/download/community
```

3. Install ToyWebAuthN:
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install the package
pip install -e .

# Generate SSL certificates
toy-webauthn-generate-certs
```

4. Start MongoDB:
```bash
# On macOS
brew services start mongodb-community

# On Ubuntu/Debian
sudo systemctl start mongodb

# On Windows
# MongoDB should run as a service after installation
```

5. Start the server:
```bash
toy-webauthn
```

6. Open your browser and navigate to:
```
https://localhost:5000
```

## Documentation

For detailed documentation, see [docs/README.md](docs/README.md).

## Development

### Prerequisites

- Python 3.8 or higher
- MongoDB 4.4 or higher
- mkcert
- virtualenv or venv
- VSCode (recommended)

### Development Tools

The project uses several tools to maintain code quality:

1. **Code Formatting**:
   - autopep8: PEP 8 code formatting
   - black (optional): Alternative formatter
   - isort: Import sorting

2. **Linting**:
   - flake8: PEP 8 style checking
   - pylint: Advanced Python linting

3. **Type Checking**:
   - mypy: Static type checking
   - Pylance (VSCode)

4. **Testing**:
   - pytest: Testing framework
   - pytest-cov: Coverage reporting

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
pip install -r requirements-dev.txt
pip install -e .
```

4. Install VSCode extensions:
   - Python (ms-python.python)
   - Pylance (ms-python.vscode-pylance)

5. Generate certificates:
```bash
toy-webauthn-generate-certs
```

### Code Style Guidelines

This project follows PEP 8 style guidelines with some additional requirements:

1. **Line Length**: Maximum 79 characters
2. **Indentation**: 4 spaces (no tabs)
3. **Imports**:
   - Grouped by: standard library, third-party, local
   - Alphabetically ordered within groups
   - One import per line
   - No wildcard imports

4. **Documentation**:
   - Docstrings for all modules, classes, and functions
   - Type hints in docstrings
   - Clear and concise comments

5. **Code Organization**:
   - One class per file (with exceptions)
   - Related functionality grouped in modules
   - Clear separation of concerns

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_specific.py
```

### Development Workflow

1. Create a new branch for your feature:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes:
   - Write tests first (TDD)
   - Implement your changes
   - Run tests and linting
   - Format code

3. Commit your changes:
```bash
git add .
git commit -m "feat: add your feature description"
```

4. Push and create a pull request:
```bash
git push origin feature/your-feature-name
```

## Security Notes

This is a demonstration implementation and should not be used in production without significant security enhancements:

1. Limited credential verification
2. Basic user verification
3. Limited origin validation
4. No rate limiting
5. Basic MongoDB security

## Architecture

The project follows a modular architecture:

1. **WebAuthnManager**: Core WebAuthn functionality
2. **WebAuthnApp**: Flask application wrapper
3. **Authentication**: Credential verification
4. **Registration**: User registration
5. **Common**: Shared utilities

## Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the code style guidelines
4. Write tests for your changes
5. Update documentation
6. Submit a pull request

## License

MIT License

## Acknowledgments

- [WebAuthn Specification](https://www.w3.org/TR/webauthn-2/)
- [python-fido2](https://github.com/Yubico/python-fido2)
- [Flask](https://flask.palletsprojects.com/)
- [MongoDB](https://www.mongodb.com/)
