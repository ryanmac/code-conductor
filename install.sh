#!/bin/bash

# Conductor-Score Install Script
# One-command setup for conductor-score

set -e

echo "🚀 Setting up Conductor-Score..."

# Check if we're in the right directory
if [ ! -f "setup.py" ]; then
    echo "❌ Error: setup.py not found. Please run this script from the conductor-score directory."
    exit 1
fi

# Function to install with pip/venv
install_with_pip() {
    echo "📦 Installing with pip and virtual environment..."

    # Create virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv .venv
    fi

    # Activate virtual environment
    source .venv/bin/activate

    # Upgrade pip
    pip install --upgrade pip

    # Install dependencies
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        echo "⚠️  No requirements.txt found, installing minimal dependencies..."
        pip install pyyaml requests
    fi

    echo "✅ Dependencies installed with pip"
}

# Function to install with Poetry
install_with_poetry() {
    echo "📦 Installing with Poetry..."

    # Install dependencies
    poetry install

    echo "✅ Dependencies installed with Poetry"
}

# Check if Poetry is available
if command -v poetry &> /dev/null && poetry --version &> /dev/null; then
    echo "🎵 Poetry detected, using Poetry for dependency management..."
    install_with_poetry

    # Run setup with Poetry
    echo "🔧 Running setup..."
    poetry run python setup.py "$@"

    echo ""
    echo "🎉 Setup complete!"
    echo "To activate the environment and run scripts:"
    echo "  poetry shell"
    echo "  python .conductor/scripts/your-script.py"

else
    echo "📦 Poetry not found, using pip and virtual environment..."
    install_with_pip

    # Run setup with pip
    echo "🔧 Running setup..."
    source .venv/bin/activate
    python setup.py "$@"

    echo ""
    echo "🎉 Setup complete!"
    echo "To activate the environment and run scripts:"
    echo "  source .venv/bin/activate"
    echo "  python .conductor/scripts/your-script.py"
fi

echo ""
echo "📚 Next steps:"
echo "  1. Check the README.md for usage instructions"
echo "  2. Run 'python setup.py --help' for setup options"
echo "  3. Explore the .conductor/examples/ directory for templates"
