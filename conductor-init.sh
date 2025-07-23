#!/bin/bash

# conductor-init.sh - Universal Installer for Code Conductor
# Usage: bash <(curl -fsSL https://raw.githubusercontent.com/ryanmac/code-conductor/main/conductor-init.sh)
# Installs Code Conductor into the current Git repository without full cloning.

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Code Conductor Universal Installer${NC}"
echo "=========================================="
echo "This script will install Code Conductor into your current Git repository."
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
REPO_TARBALL_URL="https://github.com/ryanmac/code-conductor/archive/refs/heads/main.tar.gz"
TEMP_DIR="/tmp/code-conductor-init"

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

# Step 3: Install Dependencies (improved: suppress verbosity)
echo -e "${YELLOW}📦 Installing dependencies...${NC}"

# **Improved: Check if Poetry is functional before using it**
POETRY_AVAILABLE=false
if command -v poetry >/dev/null 2>&1 && poetry --version >/dev/null 2>&1; then
    POETRY_AVAILABLE=true
fi

# Prefer Poetry if available and functional, otherwise use pip + venv
if $POETRY_AVAILABLE; then
    echo "🎵 Poetry detected and functional. Using Poetry for installation."
    poetry install --quiet || {
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
    pip install --upgrade pip --quiet || {
        echo -e "${RED}❌ Failed to upgrade pip.${NC}"
        exit 1
    }
    pip install -r requirements.txt --quiet || {
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

# Step 5: Auto-commit generated files (with user consent)
echo -e "${YELLOW}📝 Committing generated files to Git...${NC}"
git add .conductor .github setup.py requirements.txt pyproject.toml VERSION 2>/dev/null
if git diff --staged --quiet; then
    echo -e "${GREEN}✅ No changes to commit (files already in Git).${NC}"
else
    read -p "Commit these changes automatically? [Y/n]: " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        git commit -m "Initialize Code Conductor setup" || echo -e "${YELLOW}⚠️ Commit failed.${NC}"
        echo -e "${GREEN}✅ Changes committed.${NC}"
    else
        echo -e "${YELLOW}⚠️ Skipping commit. Remember to commit manually.${NC}"
    fi
fi
echo ""

# Step 6: Interactive Role Configuration (improved: numbered menu)
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

# Parse current roles and filter suggestions
ALL_ROLES=("code-reviewer" "frontend" "mobile" "devops" "security" "ml-engineer" "ui-designer" "data")
ROLE_DESCRIPTIONS=(
    "AI-powered PR reviews"
    "React, Vue, Angular development"
    "React Native, Flutter development"
    "CI/CD, deployments, infrastructure"
    "Security audits, vulnerability scanning"
    "Machine learning tasks"
    "Design systems, UI/UX"
    "Data pipelines, analytics"
)

# Get array of current roles
IFS=' ' read -ra CURRENT_ROLES_ARRAY <<< "$CONFIGURED_ROLES"

# Build suggested roles (exclude already configured)
SUGGESTED_ROLES=()
SUGGESTED_INDICES=()
for i in "${!ALL_ROLES[@]}"; do
    role="${ALL_ROLES[$i]}"
    if [[ ! " ${CURRENT_ROLES_ARRAY[@]} " =~ " ${role} " ]]; then
        SUGGESTED_ROLES+=("$role")
        SUGGESTED_INDICES+=("$i")
    fi
done

# Ask if user wants to adjust roles
if [ ${#SUGGESTED_ROLES[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ All available roles are already configured.${NC}"
else
    echo "Available roles to add:"
    for i in "${!SUGGESTED_ROLES[@]}"; do
        idx=${SUGGESTED_INDICES[$i]}
        echo "  $((i+1))) ${SUGGESTED_ROLES[$i]} - ${ROLE_DESCRIPTIONS[$idx]}"
    done
    echo ""
    read -p "Select roles to add (comma-separated numbers, or Enter to skip): " -r ROLE_SELECTION
    
    if [ -n "$ROLE_SELECTION" ]; then
        # Parse selected numbers and build role list
        SELECTED_ROLES=()
        IFS=',' read -ra SELECTIONS <<< "$ROLE_SELECTION"
        for num in "${SELECTIONS[@]}"; do
            num=$(echo $num | tr -d ' ')  # Trim spaces
            if [[ $num =~ ^[0-9]+$ ]] && [ "$num" -ge 1 ] && [ "$num" -le "${#SUGGESTED_ROLES[@]}" ]; then
                SELECTED_ROLES+=("${SUGGESTED_ROLES[$((num-1))]}")
            fi
        done
        
        if [ ${#SELECTED_ROLES[@]} -gt 0 ]; then
            # Update config.yaml with selected roles
            ROLES_TO_ADD=$(IFS=','; echo "${SELECTED_ROLES[*]}")
            python3 -c "
import yaml
with open('.conductor/config.yaml', 'r') as f:
    config = yaml.safe_load(f)
current_roles = config.get('roles', {}).get('specialized', [])
new_roles = [r.strip() for r in '$ROLES_TO_ADD'.split(',') if r.strip()]
combined_roles = list(set(current_roles + new_roles))
config['roles']['specialized'] = combined_roles
with open('.conductor/config.yaml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False)
print(f'✅ Roles added: {", ".join(new_roles)}')
" || echo -e "${YELLOW}⚠️ Could not update roles automatically.${NC}"
        else
            echo -e "${YELLOW}⚠️ No valid selections made.${NC}"
        fi
    else
        echo -e "${GREEN}✅ Keeping current role configuration.${NC}"
    fi
fi

# Step 7: Seed Demo Tasks
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

# Step 8: Launch Agent (improved: handle uncommitted changes)
echo ""
read -p "Would you like to start a dev agent now? [Y/n]: " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    echo -e "${YELLOW}🤖 Starting dev agent...${NC}"
    
    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        echo -e "${YELLOW}⚠️ Uncommitted changes detected.${NC}"
        read -p "Stash them automatically before starting agent? [Y/n]: " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
            git stash push -m "Auto-stash before Conductor agent startup" || {
                echo -e "${RED}❌ Failed to stash changes.${NC}"
                echo "Please commit or stash changes manually, then run: bash .conductor/scripts/bootstrap.sh dev"
                exit 1
            }
            echo -e "${GREEN}✅ Changes stashed. You can restore them later with: git stash pop${NC}"
        else
            echo -e "${YELLOW}⚠️ Skipping agent startup. Please handle uncommitted changes first.${NC}"
            echo "Then run: bash .conductor/scripts/bootstrap.sh dev"
            exit 0
        fi
    fi
    
    bash .conductor/scripts/bootstrap.sh dev || {
        echo -e "${YELLOW}⚠️ Agent startup failed.${NC}"
        echo "You can try again with: bash .conductor/scripts/bootstrap.sh dev"
        if git stash list | grep -q "Auto-stash before Conductor"; then
            echo "To restore your stashed changes: git stash pop"
        fi
    }
fi

# Note: No cleanup of setup.py, requirements.txt, etc. - leaving them in place for user reference and future use.

# Step 9: Next Steps (enhanced with copy-pasteable commands)
echo ""
echo -e "${GREEN}🎉 Installation Successful!${NC}"
echo "=========================================="
echo "Code Conductor is now installed with:"
if [ -n "$DETECTED_STACKS" ]; then
    echo "  ✅ Auto-detected: $DETECTED_STACKS"
else
    echo "  ✅ Auto-detected technology stack"
fi
echo "  ✅ AI code-reviewer for all PRs"
echo "  ✅ Specialized roles: ${CONFIGURED_ROLES}"
echo "  ✅ Demo tasks ready to claim"
echo ""
echo "${YELLOW}Quick Start Commands:${NC}"
echo "  📋 View tasks:     ${GREEN}cat .conductor/workflow-state.json | jq '.available_tasks'${NC}"
echo "  🤖 Start agent:    ${GREEN}bash .conductor/scripts/bootstrap.sh dev${NC}"
echo "  📝 Create task:    ${GREEN}gh issue create -l 'conductor:task'${NC}"
echo "  🔧 Adjust config:  ${GREEN}$EDITOR .conductor/config.yaml${NC}"
echo ""
echo "${YELLOW}Your first PR will automatically get AI code reviews!${NC}"
echo ""
echo "📚 Documentation: https://github.com/ryanmac/code-conductor"
echo "🐛 Report issues: https://github.com/ryanmac/code-conductor/issues"
echo ""
echo -e "${GREEN}Happy orchestrating! 🎼${NC}"
