#!/bin/bash
set -e

# Conductor-Score: One-Command Install Script
# From tweet discovery to AI agent coordination in 60 seconds
echo "🎼 Conductor-Score Installer"
echo "═══════════════════════════════════════"
echo "Transform your dev workflow with AI agent coordination"
echo ""

# Configuration
REPO_URL="https://github.com/ryanmac/conductor-score.git"
TEMP_DIR=".conductor-score-temp"
AUTO_MODE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --auto)
      AUTO_MODE=true
      shift
      ;;
    --help|-h)
      echo "Usage: $0 [--auto] [--help]"
      echo ""
      echo "Options:"
      echo "  --auto    Run setup in auto mode (minimal prompts)"
      echo "  --help    Show this help message"
      echo ""
      echo "This script will:"
      echo "  1. Check prerequisites (Python, Git, GitHub CLI)"
      echo "  2. Clone conductor-score template"
      echo "  3. Copy files to your project"
      echo "  4. Run interactive setup"
      echo "  5. Clean up temporary files"
      echo ""
      echo "Run from your project root directory."
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Utility functions
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo "❌ $1 is required but not installed."
        echo "💡 Install it with: $2"
        return 1
    else
        echo "✅ $1 found"
        return 0
    fi
}

install_missing_deps() {
    local missing=false

    echo "🔍 Checking prerequisites..."

    # Check Python
    if ! check_command "python3" "brew install python (macOS) or apt install python3 (Ubuntu)"; then
        missing=true
    fi

    # Check Git
    if ! check_command "git" "brew install git (macOS) or apt install git (Ubuntu)"; then
        missing=true
    fi

    # Check GitHub CLI (optional but recommended)
    if ! check_command "gh" "brew install gh (macOS) or apt install gh (Ubuntu)"; then
        echo "⚠️  GitHub CLI is optional but recommended for best experience"
        echo "💡 You can install it later with: brew install gh"
    fi

    if [ "$missing" = true ]; then
        echo ""
        echo "❌ Missing required dependencies. Please install them and run again."
        exit 1
    fi

    echo "✅ All prerequisites satisfied!"
    echo ""
}

# Check if we're in a git repository
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo "❌ This doesn't appear to be a git repository."
        echo "💡 Run 'git init' first, or cd to your project root."
        exit 1
    fi

    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        echo "⚠️  You have uncommitted changes."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Cancelled. Please commit or stash your changes first."
            exit 1
        fi
    fi

    echo "✅ Git repository ready"
}

# Main installation process
main() {
    echo "Installing to: $(pwd)"
    echo ""

    # Step 1: Check prerequisites
    install_missing_deps

    # Step 2: Verify git repository
    check_git_repo

    # Step 3: Clone template
    echo "📥 Downloading conductor-score template..."
    if [ -d "$TEMP_DIR" ]; then
        rm -rf "$TEMP_DIR"
    fi

    git clone --quiet "$REPO_URL" "$TEMP_DIR"
    echo "✅ Template downloaded"

    # Step 4: Copy template files
    echo "📁 Installing conductor-score files..."

    # Copy core files, excluding git history and temp files
    cp -r "$TEMP_DIR/.conductor" .
    cp -r "$TEMP_DIR/examples" .
    cp "$TEMP_DIR/setup.py" .

    # Create .gitignore entries if file exists
    if [ -f ".gitignore" ]; then
        echo "" >> .gitignore
        echo "# Conductor-Score" >> .gitignore
        cat "$TEMP_DIR/.gitignore" >> .gitignore
    else
        cp "$TEMP_DIR/.gitignore" .
    fi

    echo "✅ Files installed"

    # Step 5: Run setup
    echo "⚙️  Running conductor-score setup..."
    echo ""

    if [ "$AUTO_MODE" = true ]; then
        python3 setup.py --auto
    else
        python3 setup.py
    fi

    # Step 6: Cleanup
    echo ""
    echo "🧹 Cleaning up..."
    rm -rf "$TEMP_DIR"

    # Step 7: Success message
    echo ""
    echo "🎉 Conductor-Score installed successfully!"
    echo "═══════════════════════════════════════════"
    echo ""
    echo "Next steps:"
    echo "1. Commit the new .conductor/ directory:"
    echo "   git add .conductor/ setup.py examples/ .gitignore"
    echo "   git commit -m '🎼 Add conductor-score agent coordination'"
    echo ""
    echo "2. Create your first task via GitHub Issue with 'conductor:task' label"
    echo ""
    echo "3. Launch an agent:"
    echo "   export AGENT_ROLE=dev"
    echo "   bash .conductor/scripts/bootstrap.sh"
    echo ""
    echo "🚀 Ready to transform your development workflow!"
echo "📚 Usage guide: docs/USAGE.md"
echo "🌐 Learn more: https://github.com/ryanmac/conductor-score"
}

# Safety check - don't run in the conductor-score repo itself
if [ -f "install.sh" ] && [ -f "setup.py" ] && [ -d ".conductor" ]; then
    echo "❌ It looks like you're running this from the conductor-score repo itself."
    echo "💡 Clone this into your project directory instead:"
    echo ""
    echo "   cd /path/to/your/project"
    echo "   curl -sSL https://github.com/ryanmac/conductor-score/raw/main/install.sh | bash"
    echo ""
    exit 1
fi

# Run main installation
main 