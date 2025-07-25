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
echo -e "${GREEN}✨ No GitHub Token Setup Required!${NC}"
echo "Code Conductor uses GitHub's built-in authentication - no manual token needed."
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
    echo -e "${YELLOW}Note: Python is only needed for conductor scripts, NOT for your project's CI/CD.${NC}"
    echo -e "${YELLOW}Code Conductor does NOT add Python-specific workflows to non-Python projects.${NC}"
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

# Check for GitHub CLI (optional but recommended)
if ! command -v gh >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️ GitHub CLI (gh) not found. Install it for full functionality:${NC}"
    echo "  • macOS: brew install gh"
    echo "  • Linux: See https://cli.github.com/manual/installation"
    echo "  • Windows: winget install GitHub.cli"
    echo ""
elif ! gh auth status >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️ GitHub CLI not authenticated. Run 'gh auth login' after setup.${NC}"
fi

# **Improved: Check for pyenv and suggest version switch if Poetry fails later**
if command -v pyenv >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️ pyenv detected. Ensure your active Python version has Poetry installed if using it.${NC}"
fi

# Check for existing installation
IS_UPGRADE=false
CURRENT_VERSION=""
if [ -d ".conductor" ]; then
    echo -e "${YELLOW}⚠️ Existing Code Conductor installation detected.${NC}"
    
    # Check if VERSION file exists to determine version
    if [ -f "VERSION" ]; then
        CURRENT_VERSION=$(cat VERSION 2>/dev/null || echo "unknown")
        echo -e "Current version: ${GREEN}$CURRENT_VERSION${NC}"
        IS_UPGRADE=true
    else
        echo -e "${YELLOW}⚠️ Unknown version (no VERSION file found).${NC}"
    fi
    
    echo ""
    echo "Would you like to:"
    echo "  1) Upgrade - Update Code Conductor while preserving your configuration"
    echo "  2) Reinstall - Complete fresh installation (overwrites everything)"
    echo "  3) Cancel - Exit without making changes"
    echo ""
    read -p "Your choice [1-3]: " -n 1 -r INSTALL_CHOICE
    echo ""
    
    case "$INSTALL_CHOICE" in
        1)
            IS_UPGRADE=true
            echo -e "${GREEN}✅ Proceeding with upgrade...${NC}"
            ;;
        2)
            echo -e "${YELLOW}⚠️ This will delete all existing Code Conductor files and configurations.${NC}"
            read -p "Are you sure? [y/N]: " -n 1 -r
            echo ""
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo -e "${RED}❌ Installation cancelled.${NC}"
                exit 0
            fi
            rm -rf .conductor VERSION setup.py requirements.txt pyproject.toml
            IS_UPGRADE=false
            ;;
        *)
            echo -e "${RED}❌ Installation cancelled.${NC}"
            exit 0
            ;;
    esac
fi

echo -e "${GREEN}✅ All prerequisites met.${NC}"
echo ""

# Step 2: Download and Extract Essential Files from Tarball
if [ "$IS_UPGRADE" = true ]; then
    echo -e "${YELLOW}📥 Downloading latest version for upgrade...${NC}"
else
    echo -e "${YELLOW}📥 Downloading and extracting from GitHub tarball...${NC}"
fi

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

# Check new version
NEW_VERSION=$(cat "$TEMP_DIR/VERSION" 2>/dev/null || echo "unknown")
if [ "$IS_UPGRADE" = true ]; then
    echo -e "New version: ${GREEN}$NEW_VERSION${NC}"
    if [ "$CURRENT_VERSION" = "$NEW_VERSION" ]; then
        echo -e "${GREEN}✅ Already at latest version ($NEW_VERSION).${NC}"
        read -p "Continue anyway? [Y/n]: " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]] && [[ -n $REPLY ]]; then
            rm -rf "$TEMP_DIR"
            exit 0
        fi
    fi
fi

# Handle file copying based on installation type
if [ "$IS_UPGRADE" = true ]; then
    # Backup user configurations
    echo -e "${YELLOW}📁 Backing up user configurations...${NC}"
    BACKUP_DIR="/tmp/conductor-backup-$$"
    mkdir -p "$BACKUP_DIR"
    
    # Backup files that should be preserved
    [ -f ".conductor/config.yaml" ] && cp ".conductor/config.yaml" "$BACKUP_DIR/"
    [ -f ".conductor/CLAUDE.md" ] && cp ".conductor/CLAUDE.md" "$BACKUP_DIR/"
    [ -f "CLAUDE.md" ] && cp "CLAUDE.md" "$BACKUP_DIR/CLAUDE_ROOT.md"
    
    # Update core scripts only
    echo -e "${YELLOW}📥 Updating core scripts...${NC}"
    
    # Update scripts directory
    cp -r "$TEMP_DIR/.conductor/scripts" ".conductor/" || {
        echo -e "${RED}❌ Failed to update scripts.${NC}"
        rm -rf "$TEMP_DIR" "$BACKUP_DIR"
        exit 1
    }
    
    # Update roles directory
    cp -r "$TEMP_DIR/.conductor/roles" ".conductor/" || {
        echo -e "${RED}❌ Failed to update roles.${NC}"
        rm -rf "$TEMP_DIR" "$BACKUP_DIR"
        exit 1
    }
    
    # Note: We do NOT copy workflow files during upgrade
    # Workflows are generated by setup.py with proper token configuration
    echo -e "${YELLOW}📝 Workflow files will be regenerated with correct configuration...${NC}"
    
    # Update root files
    cp "$TEMP_DIR/setup.py" . || {
        echo -e "${RED}❌ Failed to update setup.py.${NC}"
        rm -rf "$TEMP_DIR" "$BACKUP_DIR"
        exit 1
    }
    cp "$TEMP_DIR/requirements.txt" . || {
        echo -e "${RED}❌ Failed to update requirements.txt.${NC}"
        rm -rf "$TEMP_DIR" "$BACKUP_DIR"
        exit 1
    }
    cp "$TEMP_DIR/pyproject.toml" . || {
        echo -e "${RED}❌ Failed to update pyproject.toml.${NC}"
        rm -rf "$TEMP_DIR" "$BACKUP_DIR"
        exit 1
    }
    cp "$TEMP_DIR/VERSION" . || {
        echo -e "${RED}❌ Failed to update VERSION.${NC}"
        rm -rf "$TEMP_DIR" "$BACKUP_DIR"
        exit 1
    }
    
    # Restore user configurations
    echo -e "${YELLOW}📁 Restoring user configurations...${NC}"
    [ -f "$BACKUP_DIR/config.yaml" ] && cp "$BACKUP_DIR/config.yaml" ".conductor/"
    [ -f "$BACKUP_DIR/CLAUDE.md" ] && cp "$BACKUP_DIR/CLAUDE.md" ".conductor/"
    [ -f "$BACKUP_DIR/CLAUDE_ROOT.md" ] && cp "$BACKUP_DIR/CLAUDE_ROOT.md" "CLAUDE.md"
    
    # Cleanup backup
    rm -rf "$BACKUP_DIR"
    
    echo -e "${GREEN}✅ Core files updated while preserving configurations.${NC}"
else
    # Fresh installation - copy everything
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
fi

# Optionally copy examples (prompt user) - only for fresh installs
if [ "$IS_UPGRADE" = false ]; then
    read -p "Do you want to copy example configurations (recommended for new users)? [Y/n]: " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        cp -r "$TEMP_DIR/examples" .conductor/ || {
            echo -e "${YELLOW}⚠️ Failed to copy examples directory (continuing anyway).${NC}"
        }
        echo -e "${GREEN}✅ Examples copied to .conductor/examples.${NC}"
    fi
fi

# Clean up temp dir
rm -rf "$TEMP_DIR"

if [ "$IS_UPGRADE" = true ]; then
    echo -e "${GREEN}✅ Upgrade complete: Updated from $CURRENT_VERSION to $NEW_VERSION${NC}"
else
    echo -e "${GREEN}✅ Files extracted: .conductor/, setup.py, requirements.txt, pyproject.toml, VERSION${NC}"
fi
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

# Step 4: Run Setup (only for fresh installs)
if [ "$IS_UPGRADE" = false ]; then
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
    
    # Emphasize no token requirement
    echo -e "${GREEN}🔐 GitHub Integration Status:${NC}"
    echo "  ✅ Workflows configured to use GitHub's built-in token"
    echo "  ✅ No CONDUCTOR_GITHUB_TOKEN setup required"
    echo "  ✅ AI code reviews will work automatically on PRs"
    echo ""
else
    echo -e "${GREEN}✅ Skipping setup - existing configuration preserved.${NC}"
    echo ""
fi

# Step 5: Auto-configure All Roles - skip for upgrades
if [ "$IS_UPGRADE" = false ]; then
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

    # Define all available roles
    ALL_ROLES=("code-reviewer" "frontend" "mobile" "devops" "security" "ml-engineer" "ui-designer" "data")
    
    # Automatically configure all roles
    echo -e "${YELLOW}📝 Configuring all available roles...${NC}"
    
    # Update config.yaml with all roles
    python3 - <<EOF
import yaml

# Define all available roles
all_roles = ["code-reviewer", "frontend", "mobile", "devops", "security", "ml-engineer", "ui-designer", "data"]

# Read current config
with open('.conductor/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Update roles to include all available roles
config['roles']['specialized'] = all_roles

# Write updated config
with open('.conductor/config.yaml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False)

print(f'✅ All {len(all_roles)} roles configured: {", ".join(all_roles)}')
EOF

    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}⚠️ Could not configure roles automatically. Continuing anyway...${NC}"
    else
        echo -e "${GREEN}✅ All agent roles are now available for use!${NC}"
    fi
    echo ""
else
    echo -e "${GREEN}✅ Existing role configuration preserved.${NC}"
fi

# Step 6: Seed Demo Tasks - skip for upgrades
if [ "$IS_UPGRADE" = false ]; then
    echo ""
    echo -e "${YELLOW}📝 Creating demo tasks...${NC}"

    # Check if GitHub CLI is available
    if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
        # Check if demo tasks already exist
        EXISTING_TASKS=$(gh issue list -l 'conductor:task' --limit 10 --json number 2>/dev/null | jq length 2>/dev/null || echo "0")
        
        if [ "$EXISTING_TASKS" = "0" ]; then
            echo "Creating demo GitHub Issues..."
            
            # Create first demo task
            gh issue create \
                --title "Add README documentation" \
                --body "## Description
Create or update README.md with project overview, installation instructions, and usage examples.

## Success Criteria
- Clear project description
- Installation steps for all platforms
- Usage examples with code snippets
- Contribution guidelines

## Files to Modify
- README.md" \
                --label "conductor:task" \
                --label "effort:small" \
                --label "priority:medium" \
                2>/dev/null && echo "  ✅ Created demo task: Add README documentation"
            
            # Create second demo task
            gh issue create \
                --title "Set up CI/CD pipeline" \
                --body "## Description
Create GitHub Actions workflow for automated testing and deployment.

## Success Criteria
- Automated test runs on PR
- Code linting and formatting checks
- Build validation
- Optional: deployment automation

## Files to Modify
- .github/workflows/ci.yml" \
                --label "conductor:task" \
                --label "effort:medium" \
                --label "priority:high" \
                --label "skill:devops" \
                2>/dev/null && echo "  ✅ Created demo task: Set up CI/CD pipeline"
            
            echo -e "${GREEN}✅ Demo tasks created as GitHub Issues${NC}"
        else
            echo -e "${GREEN}✅ Tasks already exist (found $EXISTING_TASKS tasks)${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️ GitHub CLI not available or not authenticated.${NC}"
        echo "To create demo tasks later, run:"
        echo "  gh auth login"
        echo "  gh issue create --label 'conductor:task'"
    fi
fi

# Step 7: Auto-commit all generated files (with user consent)
echo ""
if [ "$IS_UPGRADE" = true ]; then
    echo -e "${YELLOW}📝 Committing upgraded files to Git...${NC}"
    COMMIT_MESSAGE="Upgrade Code Conductor from $CURRENT_VERSION to $NEW_VERSION"
else
    echo -e "${YELLOW}📝 Committing all generated files to Git...${NC}"
    COMMIT_MESSAGE="Initialize Code Conductor setup with configuration"
fi

git add .conductor .github setup.py requirements.txt pyproject.toml VERSION 2>/dev/null
if git diff --staged --quiet; then
    echo -e "${GREEN}✅ No changes to commit (files already in Git).${NC}"
else
    read -p "Commit these changes automatically? [Y/n]: " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        git commit -m "$COMMIT_MESSAGE" || echo -e "${YELLOW}⚠️ Commit failed.${NC}"
        echo -e "${GREEN}✅ Changes committed.${NC}"
    else
        echo -e "${YELLOW}⚠️ Skipping commit. Remember to commit manually.${NC}"
    fi
fi

# Step 8: Development Environment Selection - skip for upgrades
if [ "$IS_UPGRADE" = false ]; then
    echo ""
    echo -e "${YELLOW}🖥️  Select your primary development environment:${NC}"
    echo ""
    echo "  1) Conductor (https://conductor.build - macOS only)"
    echo "  2) Terminal (Warp, iTerm2, Windows Terminal, etc.)"
    echo "  3) IDE (Cursor, Cline, Windsurf, VSCode, etc.)"
    echo ""
    read -p "Enter your choice [1-3]: " -n 1 -r ENV_CHOICE
    echo ""
else
    # Skip environment selection for upgrades
    ENV_CHOICE="skip"
fi

case "$ENV_CHOICE" in
    1)
        # Conductor App Flow
        if [[ "$OSTYPE" != "darwin"* ]]; then
            echo -e "${YELLOW}⚠️  Conductor app is currently macOS-only.${NC}"
            echo "Please select Terminal or IDE option instead."
            exit 0
        fi
        
        echo -e "${GREEN}🎼 Conductor App Setup${NC}"
        echo "=========================================="
        echo ""
        echo "📋 Next Steps:"
        echo ""
        echo "1. Open Conductor app:"
        echo -e "   ${GREEN}open -a Conductor${NC}"
        echo ""
        echo "2. Add this project as a workspace:"
        echo -e "   • In Conductor: ${YELLOW}File → Add Workspace${NC}"
        echo -e "   • Select directory: ${GREEN}$(pwd)${NC}"
        echo ""
        echo "3. Start working with this prompt:"
        echo ""
        echo -e "   ${YELLOW}\"Ultrathink: What task will create the most value? Find it, claim it, complete it.\"${NC}"
        echo ""
        echo "💡 Pro Tips:"
        echo "   • Conductor will handle task claiming and worktree setup automatically"
        echo "   • Use the built-in terminal for git operations"
        echo "   • AI code reviews happen automatically on PRs"
        echo -e "   • ${GREEN}No GitHub token setup needed—uses built-in authentication${NC}"
        echo ""
        echo "📚 Learn more: https://conductor.build"
        ;;
        
    2|3)
        # Terminal/IDE Flow - Run bootstrap
        if [ "$ENV_CHOICE" = "2" ]; then
            echo -e "${GREEN}🖥️  Terminal Workflow${NC}"
        else
            echo -e "${GREEN}💻 IDE Workflow${NC}"
        fi
        echo "=========================================="
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
                        echo "Please commit or stash changes manually, then run: ./conductor start dev"
                        exit 1
                    }
                    echo -e "${GREEN}✅ Changes stashed. You can restore them later with: git stash pop${NC}"
                else
                    echo -e "${YELLOW}⚠️ Skipping agent startup. Please handle uncommitted changes first.${NC}"
                    echo "Then run: ./conductor start dev"
                    exit 0
                fi
            fi
            
            ./conductor start dev || {
                echo -e "${YELLOW}⚠️ Agent startup failed.${NC}"
                echo "You can try again with: ./conductor start dev"
                if git stash list | grep -q "Auto-stash before Conductor"; then
                    echo "To restore your stashed changes: git stash pop"
                fi
            }
        else
            echo ""
            echo "📋 To start an agent later:"
            echo -e "   ${GREEN}./conductor start dev${NC}"
        fi
        ;;
        
    skip)
        # Skip environment selection for upgrades
        ;;
        
    *)
        echo -e "${RED}❌ Invalid choice. Please run the installer again.${NC}"
        exit 1
        ;;
esac

# Note: No cleanup of setup.py, requirements.txt, etc. - leaving them in place for user reference and future use.

# Step 9: Next Steps (contextual based on installation type and environment choice)
if [ "$IS_UPGRADE" = true ]; then
    # Upgrade complete
    echo ""
    echo -e "${GREEN}🎉 Upgrade Complete!${NC}"
    echo "=========================================="
    echo -e "Updated Code Conductor from ${YELLOW}$CURRENT_VERSION${NC} to ${GREEN}$NEW_VERSION${NC}"
    echo ""
    echo "✅ What was updated:"
    echo "  • Core scripts (.conductor/scripts/)"
    echo "  • Role definitions (.conductor/roles/)"
    echo "  • GitHub workflows (.github/workflows/)"
    echo "  • Setup and configuration tools"
    echo -e "  • ${GREEN}Token configuration (uses GitHub's built-in auth)${NC}"
    echo ""
    echo "✅ What was preserved:"
    echo "  • Your project configuration (.conductor/config.yaml)"
    echo "  • Your CLAUDE.md customizations"
    echo "  • All existing tasks and work"
    echo ""
    echo -e "${YELLOW}What's New:${NC}"
    echo "  • Enhanced task listing with rich formatting"
    echo "  • Better status command with health checks"
    echo "  • Improved error handling and recovery"
    echo "  • See full changelog: https://github.com/ryanmac/code-conductor/releases"
    echo ""
    echo -e "${YELLOW}Quick Commands:${NC}"
    echo -e "  📋 View tasks:     ${GREEN}./conductor tasks${NC}"
    echo -e "  📊 Check status:   ${GREEN}./conductor status${NC}"
    echo -e "  🤖 Start work:     ${GREEN}./conductor start [role]${NC}"
    echo -e "  🔧 Diagnose:       ${GREEN}./conductor diagnose${NC}"
    echo ""
    echo "📚 Documentation: https://github.com/ryanmac/code-conductor"
    echo "🐛 Report issues: https://github.com/ryanmac/code-conductor/issues"
    echo ""
    echo -e "${GREEN}Happy orchestrating! 🎼${NC}"
elif [ "$ENV_CHOICE" != "1" ]; then
    # Fresh install - Terminal/IDE users get the full command list
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
    echo "  ✅ All specialized roles configured (frontend, backend, devops, security, etc.)"
    echo "  ✅ Demo tasks ready to claim"
    echo -e "  ${GREEN}✅ No GitHub token setup required${NC}"
    echo -e "  ${GREEN}✅ No Python CI/CD workflows added${NC}"
    echo ""
    echo -e "${YELLOW}Quick Start Commands:${NC}"
    echo -e "  📋 View tasks:     ${GREEN}./conductor tasks${NC}"
    echo -e "  🤖 Start agent:    ${GREEN}./conductor start [role]${NC}"
    echo -e "  📝 Create task:    ${GREEN}gh issue create -l 'conductor:task'${NC}"
    echo -e "  🔧 Adjust config:  ${GREEN}$EDITOR .conductor/config.yaml${NC}"
    echo ""
    echo -e "${YELLOW}Your first PR will automatically get AI code reviews!${NC}"
    echo ""
    echo "📚 Documentation: https://github.com/ryanmac/code-conductor"
    echo "🐛 Report issues: https://github.com/ryanmac/code-conductor/issues"
    echo ""
    echo -e "${GREEN}Happy orchestrating! 🎼${NC}"
else
    # Fresh install - Conductor app users get a simplified message (already shown above)
    echo ""
    echo -e "${GREEN}🎉 Setup Complete!${NC}"
    echo "=========================================="
    echo "Code Conductor is configured with:"
    if [ -n "$DETECTED_STACKS" ]; then
        echo "  ✅ Auto-detected: $DETECTED_STACKS"
    else
        echo "  ✅ Auto-detected technology stack"
    fi
    echo "  ✅ AI code-reviewer for all PRs"
    echo "  ✅ All specialized roles configured (frontend, backend, devops, security, etc.)"
    echo "  ✅ Demo tasks ready in Conductor"
    echo -e "  ${GREEN}✅ No GitHub token setup required${NC}"
    echo -e "  ${GREEN}✅ No Python CI/CD workflows added${NC}"
    echo ""
    echo "📚 Documentation: https://github.com/ryanmac/code-conductor"
    echo "🐛 Report issues: https://github.com/ryanmac/code-conductor/issues"
    echo ""
    echo -e "${GREEN}Happy orchestrating with Conductor! 🎼${NC}"
fi
