#!/bin/bash

# conductor-init.sh - Universal Installer for Conductor-Score
# Usage: bash <(curl -fsSL https://raw.githubusercontent.com/ryanmac/conductor-score/main/conductor-init.sh)
# Installs Conductor-Score into the current Git repository without full cloning.

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Conductor-Score Universal Installer${NC}"
echo "=========================================="
echo "This script will install Conductor-Score into your current Git repository."
echo "It will download necessary files and run the setup automatically."
echo ""

# Step 1: Prerequisite Checks
echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"

# Check if in a Git repository
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo -e "${RED}❌ Error: Not in a Git repository. Please run this from the root of a Git repo.${NC}"
    exit 1
fi

# Check for Git
if ! command -v git >/dev/null 2>&1; then
    echo -e "${RED}❌ Error: Git is not installed. Please install Git and try again.${NC}"
    exit 1
fi

# Check for Python 3.9+
if ! command -v python3 >/dev/null 2>&1 || ! python3 -c "import sys; exit(0 if sys.version_info >= (3,9) else 1)"; then
    echo -e "${RED}❌ Error: Python 3.9+ is required. Please install Python 3.9 or higher.${NC}"
    exit 1
fi

# Check for curl
if ! command -v curl >/dev/null 2>&1; then
    echo -e "${RED}❌ Error: curl is not installed. Please install curl and try again.${NC}"
    exit 1
fi

# Check for tar (needed for extraction)
if ! command -v tar >/dev/null 2>&1; then
    echo -e "${RED}❌ Error: tar is not installed. Please install tar and try again.${NC}"
    exit 1
fi

# Check for existing installation
if [ -d ".conductor" ]; then
    echo -e "${YELLOW}⚠️ Existing .conductor directory found.${NC}"
    read -p "Do you want to overwrite and reinstall? [y/N]: " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}❌ Installation cancelled.${NC}"
        exit 0
    fi
    rm -rf .conductor
fi

echo -e "${GREEN}✅ All prerequisites met.${NC}"
echo ""

# Step 2: Download and Extract Essential Files from Tarball
echo -e "${YELLOW}📥 Downloading and extracting from GitHub tarball...${NC}"
REPO_TARBALL_URL="https://github.com/ryanmac/conductor-score/archive/refs/heads/main.tar.gz"
TEMP_DIR="/tmp/conductor-score-init"

# Create temp dir
mkdir -p "$TEMP_DIR"

# Download and extract tarball to temp dir
curl -fsSL "$REPO_TARBALL_URL" | tar -xz -C "$TEMP_DIR" --strip-components=1 || {
    echo -e "${RED}❌ Failed to download or extract tarball. Check your network or URL.${NC}"
    rm -rf "$TEMP_DIR"
    exit 1
}

# Copy essential files and directories
cp -r "$TEMP_DIR/.conductor" . || {
    echo -e "${RED}❌ Failed to copy .conductor directory.${NC}"
    rm -rf "$TEMP_DIR"
    exit 1
}
cp "$TEMP_DIR/setup.py" . || {
    echo -e "${RED}❌ Failed to copy setup.py.${NC}"
    rm -rf "$TEMP_DIR"
    exit 1
}
cp "$TEMP_DIR/requirements.txt" . || {
    echo -e "${RED}❌ Failed to copy requirements.txt.${NC}"
    rm -rf "$TEMP_DIR"
    exit 1
}
cp "$TEMP_DIR/pyproject.toml" . || {
    echo -e "${RED}❌ Failed to copy pyproject.toml.${NC}"
    rm -rf "$TEMP_DIR"
    exit 1
}
cp "$TEMP_DIR/VERSION" . || {
    echo -e "${RED}❌ Failed to copy VERSION.${NC}"
    rm -rf "$TEMP_DIR"
    exit 1
}

# Optionally copy examples (prompt user)
read -p "Do you want to copy example configurations (recommended for new users)? [Y/n]: " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    cp -r "$TEMP_DIR/examples" . || {
        echo -e "${YELLOW}⚠️ Failed to copy examples directory (continuing anyway).${NC}"
    }
    echo -e "${GREEN}✅ Examples copied.${NC}"
fi

# Clean up temp dir
rm -rf "$TEMP_DIR"

echo -e "${GREEN}✅ Files extracted: .conductor/, setup.py, requirements.txt, pyproject.toml, VERSION${NC}"
echo ""

# Step 3: Install Dependencies
echo -e "${YELLOW}📦 Installing dependencies...${NC}"

# Prefer Poetry if available, otherwise use pip + venv
if command -v poetry >/dev/null 2>&1; then
    echo "🎵 Poetry detected. Using Poetry for installation."
    poetry install || {
        echo -e "${RED}❌ Poetry install failed.${NC}"
        exit 1
    }
else
    echo "📦 Poetry not found. Using pip and virtual environment."
    python3 -m venv .venv || {
        echo -e "${RED}❌ Failed to create virtual environment.${NC}"
        exit 1
    }
    source .venv/bin/activate
    pip install --upgrade pip || {
        echo -e "${RED}❌ Failed to upgrade pip.${NC}"
        exit 1
    }
    pip install -r requirements.txt || {
        echo -e "${RED}❌ Pip install failed.${NC}"
        exit 1
    }
fi

echo -e "${GREEN}✅ Dependencies installed.${NC}"
echo ""

# Step 4: Run Setup
echo -e "${YELLOW}🔧 Running automatic setup...${NC}"

# Run setup.py with --auto flag
if command -v poetry >/dev/null 2>&1; then
    poetry run python setup.py --auto || {
        echo -e "${RED}❌ Setup failed.${NC}"
        exit 1
    }
else
    python setup.py --auto || {
        echo -e "${RED}❌ Setup failed.${NC}"
        exit 1
    }
fi

echo -e "${GREEN}✅ Setup complete.${NC}"
echo ""

# Note: No cleanup of setup.py, requirements.txt, etc. - leaving them in place for user reference and future use.

# Step 5: Next Steps
echo -e "${GREEN}🎉 Installation Successful!${NC}"
echo "=========================================="
echo "Conductor-Score is now installed in your repository."
echo ""
echo "Next steps:"
echo "1. Review .conductor/config.yaml and customize if needed."
echo "2. Create a task: Use GitHub Issues with 'conductor:task' label."
echo "3. Launch an agent: bash .conductor/scripts/bootstrap.sh dev"
echo "4. For full documentation, see the original repo: https://github.com/ryanmac/conductor-score"
echo ""
echo "If you encounter issues, check the troubleshooting guide in the repo."
echo -e "${GREEN}Happy orchestrating! 🎼${NC}"
