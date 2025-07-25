# Development Setup

## Prerequisites
- Python 3.9-3.12
- Git
- GitHub CLI (optional, for issue integration)

## Local Development
```bash
# Clone and setup
git clone https://github.com/ryanmac/code-conductor.git
cd code-conductor

# Install with Poetry (recommended)
poetry install

# Or with pip
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run tests
poetry run pytest tests/ -v
# or
python -m pytest tests/ -v

# Run linting
poetry run flake8 .conductor/scripts/ setup.py
poetry run black --check .conductor/scripts/ setup.py
```

## CI/CD
The project uses GitHub Actions for continuous integration:
- **Linting**: flake8 and black formatting checks
- **Testing**: pytest on multiple Python versions (3.9, 3.10, 3.11, 3.12)
- **Security**: safety vulnerability scanning
- **Platforms**: Ubuntu and macOS

## Contributing

This is a template repository. To contribute:

1. Fork and improve
2. Test with your project type
3. Submit PRs with examples
4. Share your adaptations

### Development Guidelines
- Follow PEP 8 style guidelines
- Add tests for new functionality
- Update documentation for changes
- Ensure CI passes before submitting PRs