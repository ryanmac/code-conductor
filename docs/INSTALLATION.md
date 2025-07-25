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

- This method avoids cloning the full Code Conductor repo and is ideal for integrating into existing projects without repository pollution.
- The script will prompt before overwriting any existing installation.
- **Security best practice:** Review the script at the raw URL before running.
- **Pyenv users:** If Poetry install fails, switch to the Python version that has Poetry installed (e.g., `pyenv shell 3.10.13`) and re-run.

<img width="1084" height="350" alt="One-line Install" src="https://github.com/user-attachments/assets/3a04506f-982f-457a-b8ea-98b6448c0219" />
<img width="1084" height="540" alt="Happy orchestrating" src="https://github.com/user-attachments/assets/1c7bb744-1194-471f-a12c-9672d208dbf3" />

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