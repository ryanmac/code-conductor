# Installation Guide

## Prerequisites
All installation methods require:
- Git
- Python 3.9-3.12
- curl (for one-liner)
- tar

Run from the root of an existing Git repository. **If using pyenv, ensure your active Python version (e.g., via `pyenv shell 3.12.x`) has Poetry installed if you prefer it; otherwise, the script falls back to pip.**

## Option 1: Universal One-Liner (Recommended - No Cloning Required)
Run this in your existing project's root directory to download and install Code Conductor directly:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/ryanmac/code-conductor/main/conductor-init.sh)
```

### For Claude Code and Non-Interactive Environments

Use the `--auto` flag for non-interactive installation (perfect for Claude Code):

```bash
curl -fsSL https://raw.githubusercontent.com/ryanmac/code-conductor/main/conductor-init.sh | bash -s -- --auto
```

**Recommended: Create PR with auto-merge for immediate activation:**
```bash
curl -fsSL https://raw.githubusercontent.com/ryanmac/code-conductor/main/conductor-init.sh | bash -s -- --auto --create-pr --auto-merge
```

This creates a pull request that:
- Makes Code Conductor visible to all agents and developers
- Auto-merges once CI checks pass (if configured)
- Provides a clear installation record in your git history

### Installation Options

The installer supports various command-line flags for customization:

```bash
# Show all available options
bash <(curl -fsSL https://raw.githubusercontent.com/ryanmac/code-conductor/main/conductor-init.sh) --help

# Common options:
--auto                # Non-interactive mode with sensible defaults
--upgrade             # Force upgrade even if already installed
--reinstall           # Force fresh installation (removes existing config)
--force               # Continue even when already at latest version
--skip-examples       # Skip copying example configurations
--skip-commit         # Skip auto-committing changes to Git
--skip-agent-start    # Skip starting a dev agent after installation
--create-pr           # Create a pull request after installation
--auto-merge          # Enable auto-merge on the created PR (implies --create-pr)
--pr-branch <name>    # Specify branch name for PR (default: auto-generated)

# Examples:
curl -fsSL ... | bash -s -- --auto --upgrade        # Auto-upgrade
curl -fsSL ... | bash -s -- --auto --skip-commit    # Install without committing
curl -fsSL ... | bash -s -- --auto --create-pr      # Install and create PR
curl -fsSL ... | bash -s -- --auto --auto-merge     # Install, create PR, and auto-merge
```

### Installation Notes

- This method avoids cloning the full Code Conductor repo and is ideal for integrating into existing projects without repository pollution.
- The script will prompt before overwriting any existing installation (in interactive mode).
- **Security best practice:** Review the script at the raw URL before running.
- **Pyenv users:** If Poetry install fails, switch to the Python version that has Poetry installed (e.g., `pyenv shell 3.10.13`) and re-run.

<img width="1084" height="350" alt="One-line Install" src="https://github.com/user-attachments/assets/3a04506f-982f-457a-b8ea-98b6448c0219" />
<img width="1084" height="540" alt="Happy orchestrating" src="https://github.com/user-attachments/assets/1c7bb744-1194-471f-a12c-9672d208dbf3" />

### Pull Request Workflow

**Why create a PR during installation?**

When Code Conductor is installed locally, the `.conductor` directory only exists in your working copy. Other agents or developers won't see it until these changes are merged into the main branch. The `--create-pr` option solves this by:

1. **Automatic Branch Creation**: If you're on the main branch, creates a new feature branch
2. **Push and PR Creation**: Pushes changes and creates a PR with detailed description
3. **Optional Auto-Merge**: With `--auto-merge`, the PR merges automatically once CI passes
4. **Visibility**: Makes Code Conductor immediately visible to all agents and collaborators

**Example workflow:**
```bash
# Install and create PR in one command
curl -fsSL https://raw.githubusercontent.com/ryanmac/code-conductor/main/conductor-init.sh | bash -s -- --auto --create-pr --auto-merge

# The installer will:
# 1. Install Code Conductor locally
# 2. Commit all changes
# 3. Create branch "conductor-setup-20240125-143022" (or use custom with --pr-branch)
# 4. Push to origin
# 5. Create PR with comprehensive description
# 6. Enable auto-merge (if --auto-merge specified)
# 7. Add labels "conductor:setup" and "automation"
```

**Requirements:**
- GitHub CLI (`gh`) must be installed and authenticated
- Repository must have a remote origin configured
- For auto-merge: repository must have branch protection that allows it

## Option 2: Poetry (For Cloned Repo)
```bash
# Clone the repository
git clone https://github.com/ryanmac/code-conductor.git
cd code-conductor

# Install with Poetry (auto-creates virtual environment)
poetry install
poetry run python setup.py
```

## Option 3: Pip + Virtual Environment (For Cloned Repo)
```bash
# Clone the repository
git clone https://github.com/ryanmac/code-conductor.git
cd code-conductor

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run setup
python setup.py
```

## Option 4: One-Command Install Script (For Cloned Repo)
```bash
# From the repository directory:
./install.sh

# Or with custom setup options:
./install.sh --auto
```

## After Installation

No GitHub token setup required—the system uses GitHub Actions' built-in authentication. Now create a GitHub Issue with `conductor:task` label, launch an agent via [Conductor.build](https://conductor.build) (macOS only as of 2024-07-22) or terminal workflow (all platforms), and watch it work.