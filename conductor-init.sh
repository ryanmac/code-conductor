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

# Check for Python 3.9-3.12
if ! command -v python3 >/dev/null 2>&1 || ! python3 -c "import sys; exit(0 if sys.version_info >= (3,9) and sys.version_info < (3,13) else 1)"; then
    echo -e "${RED}❌ Error: Python 3.9-3.12 is required. Please install Python 3.9, 3.10, 3.11, or 3.12.${NC}"
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

# **Improved: Check for pyenv and suggest version switch if Poetry fails later**
if command -v pyenv >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️ pyenv detected. Ensure your active Python version has Poetry installed if using it.${NC}"
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
    cp -r "$TEMP_DIR/examples" .conductor/ || {
        echo -e "${YELLOW}⚠️ Failed to copy examples directory (continuing anyway).${NC}"
    }
    echo -e "${GREEN}✅ Examples copied to .conductor/examples.${NC}"
fi

# Clean up temp dir
rm -rf "$TEMP_DIR"

echo -e "${GREEN}✅ Files extracted: .conductor/, setup.py, requirements.txt, pyproject.toml, VERSION${NC}"
echo ""

# Step 3: Install Dependencies
echo -e "${YELLOW}📦 Installing dependencies...${NC}"

# **Improved: Check if Poetry is functional before using it**
POETRY_AVAILABLE=false
if command -v poetry >/dev/null 2>&1 && poetry --version >/dev/null 2>&1; then
    POETRY_AVAILABLE=true
fi

# Prefer Poetry if available and functional, otherwise use pip + venv
if $POETRY_AVAILABLE; then
    echo "🎵 Poetry detected and functional. Using Poetry for installation."
    poetry install || {
        echo -e "${RED}❌ Poetry install failed. If using pyenv, try switching versions (e.g., pyenv shell 3.10.13) and re-run.${NC}"
        exit 1
    }
else
    echo "📦 Poetry not found or not functional. Using pip and virtual environment."
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
if $POETRY_AVAILABLE; then
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

# Step 5: Interactive Role Configuration
echo -e "${YELLOW}🎭 Configuring agent roles...${NC}"

# Read detected stacks from config
DETECTED_STACKS=""
if command -v python3 >/dev/null 2>&1; then
    DETECTED_STACKS=$(python3 -c "
import yaml
try:
    with open('.conductor/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        stacks = config.get('detected_stacks', [])
        if stacks:
            print(', '.join(stacks))
except:
    pass
" 2>/dev/null)
fi

if [ -n "$DETECTED_STACKS" ]; then
    echo -e "📊 Detected technology stacks: ${GREEN}$DETECTED_STACKS${NC}"
fi

# Get configured roles
CONFIGURED_ROLES=$(python3 -c "
import yaml
try:
    with open('.conductor/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        roles = config.get('roles', {}).get('specialized', [])
        print(' '.join(roles))
except:
    print('code-reviewer')
" 2>/dev/null)

echo -e "🎯 Configured specialized roles: ${GREEN}$CONFIGURED_ROLES${NC}"
echo ""

# Ask if user wants to adjust roles
read -p "Would you like to adjust the configured roles? [y/N]: " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Available specialized roles:"
    echo "  - code-reviewer (AI-powered PR reviews)"
    echo "  - frontend (React, Vue, Angular development)"
    echo "  - mobile (React Native, Flutter development)"
    echo "  - devops (CI/CD, deployments, infrastructure)"
    echo "  - security (Security audits, vulnerability scanning)"
    echo "  - ml-engineer (Machine learning tasks)"
    echo "  - ui-designer (Design systems, UI/UX)"
    echo "  - data (Data pipelines, analytics)"
    echo ""
    read -p "Enter roles to add (comma-separated, or press Enter to keep current): " ADDITIONAL_ROLES
    
    if [ -n "$ADDITIONAL_ROLES" ]; then
        # Update config.yaml with additional roles
        python3 -c "
import yaml
with open('.conductor/config.yaml', 'r') as f:
    config = yaml.safe_load(f)
current_roles = config.get('roles', {}).get('specialized', [])
new_roles = [r.strip() for r in '$ADDITIONAL_ROLES'.split(',') if r.strip()]
combined_roles = list(set(current_roles + new_roles))
config['roles']['specialized'] = combined_roles
with open('.conductor/config.yaml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False)
print(f'✅ Roles updated: {combined_roles}')
" || echo -e "${YELLOW}⚠️ Could not update roles automatically.${NC}"
    fi
fi

# Step 6: Seed Demo Tasks
echo ""
echo -e "${YELLOW}📝 Creating demo tasks...${NC}"

# Create a sample workflow-state.json with demo tasks if it doesn't have any
if [ -f ".conductor/workflow-state.json" ]; then
    python3 -c "
import json
from datetime import datetime

with open('.conductor/workflow-state.json', 'r') as f:
    state = json.load(f)

# Only add demo tasks if no tasks exist
if not state.get('available_tasks'):
    demo_tasks = [
        {
            'id': 'demo-1',
            'title': 'Add README documentation',
            'description': 'Create or update README.md with project overview, installation instructions, and usage examples',
            'priority': 'medium',
            'estimated_effort': 'small',
            'required_skills': [],
            'files_to_modify': ['README.md'],
            'created_at': datetime.utcnow().isoformat()
        },
        {
            'id': 'demo-2',
            'title': 'Set up CI/CD pipeline',
            'description': 'Create GitHub Actions workflow for automated testing and deployment',
            'priority': 'high',
            'estimated_effort': 'medium',
            'required_skills': ['devops'],
            'files_to_modify': ['.github/workflows/ci.yml'],
            'created_at': datetime.utcnow().isoformat()
        }
    ]
    state['available_tasks'] = demo_tasks
    
    with open('.conductor/workflow-state.json', 'w') as f:
        json.dump(state, f, indent=2)
    print('✅ Demo tasks created')
else:
    print('✅ Tasks already exist')
" || echo -e "${YELLOW}⚠️ Could not create demo tasks.${NC}"
fi

# Step 7: Launch Agent (Optional)
echo ""
read -p "Would you like to start a dev agent now? [Y/n]: " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    echo -e "${YELLOW}🤖 Starting dev agent...${NC}"
    bash .conductor/scripts/bootstrap.sh dev || {
        echo -e "${YELLOW}⚠️ Agent startup failed. You can try again later with: bash .conductor/scripts/bootstrap.sh dev${NC}"
    }
fi

# Note: No cleanup of setup.py, requirements.txt, etc. - leaving them in place for user reference and future use.

# Step 8: Next Steps
echo ""
echo -e "${GREEN}🎉 Installation Successful!${NC}"
echo "=========================================="
echo "Conductor-Score is now installed with:"
echo "  ✅ Auto-detected technology stack"
echo "  ✅ AI code-reviewer for all PRs"
echo "  ✅ Specialized roles configured"
echo "  ✅ Demo tasks ready to claim"
echo ""
echo "Quick Start Commands:"
echo "  📋 View tasks: cat .conductor/workflow-state.json | jq '.available_tasks'"
echo "  🤖 Start agent: bash .conductor/scripts/bootstrap.sh [role]"
echo "  📝 Create task: Use GitHub Issues with 'conductor:task' label"
echo "  🔧 Adjust config: edit .conductor/config.yaml"
echo ""
echo "Your first PR will automatically get AI code reviews!"
echo ""
echo "For full documentation: https://github.com/ryanmac/conductor-score"
echo -e "${GREEN}Happy orchestrating! 🎼${NC}"
