#!/bin/bash
set -e

# Conductor-Score Agent Bootstrap Script
# Universal agent initialization for both Conductor GUI and terminal workflows

echo "🎼 Conductor-Score Agent Bootstrap"
echo "=================================="

# Load configuration
CONFIG_FILE=".conductor/config.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Configuration not found. Run 'python setup.py' first."
    exit 1
fi

# Determine agent role
AGENT_ROLE=${AGENT_ROLE:-$(echo "$1" | tr '[:upper:]' '[:lower:]')}
if [ -z "$AGENT_ROLE" ] || [ "$AGENT_ROLE" = "unknown" ]; then
    echo "🔍 Agent role not specified. Available roles:"
    if [ -d ".conductor/roles" ]; then
        ls .conductor/roles/ | sed 's/.md$//' | sed 's/^/  - /'
    else
        echo "  - dev (default)"
    fi
    echo ""
    read -p "Enter your role [dev]: " AGENT_ROLE
    AGENT_ROLE=${AGENT_ROLE:-dev}
fi

echo "👤 Agent Role: $AGENT_ROLE"
echo ""

# Sync repository state
echo "🔄 Syncing repository state..."
if git remote get-url origin >/dev/null 2>&1; then
    git fetch origin || echo "⚠️  Could not fetch from remote"
    git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || echo "⚠️  Could not pull latest changes"
else
    echo "ℹ️  No remote configured, working with local repository"
fi

# Load role-specific instructions if available
ROLE_FILE=".conductor/roles/${AGENT_ROLE}.md"
if [ -f "$ROLE_FILE" ]; then
    echo "📖 Loaded role definition: $AGENT_ROLE"
else
    echo "ℹ️  No specific role definition found, using general dev role"
fi

# Check system dependencies
echo "🔍 Checking dependencies..."
if [ -f ".conductor/scripts/dependency-check.py" ]; then
    python3 .conductor/scripts/dependency-check.py || {
        echo "❌ Dependency check failed. Please resolve issues and try again."
        exit 1
    }
else
    echo "⚠️  dependency-check.py not found, skipping validation"
fi

# Attempt to claim a task
echo "🎯 Looking for available tasks..."
if [ ! -f ".conductor/scripts/task-claim.py" ]; then
    echo "❌ task-claim.py not found. Please run setup.py to generate required scripts."
    exit 1
fi

TASK_RESULT=$(python3 .conductor/scripts/task-claim.py --role "$AGENT_ROLE" 2>/dev/null || echo '{"status": "ERROR", "message": "Task claiming failed"}')

# Parse the result
TASK_STATUS=$(echo "$TASK_RESULT" | python3 -c "import json, sys; data=json.load(sys.stdin); print(data.get('status', 'ERROR'))" 2>/dev/null || echo "ERROR")

if [ "$TASK_STATUS" = "IDLE" ]; then
    echo ""
    echo "😴 No tasks available for role: $AGENT_ROLE"
    echo ""
    echo "💡 To create tasks:"
    echo "   - Create a GitHub Issue with 'conductor:task' label"
    echo "   - Or manually add tasks to .conductor/workflow-state.json"
    echo ""
    echo "🔄 Check back later when new tasks are available."
    exit 0
elif [ "$TASK_STATUS" = "ERROR" ]; then
    echo ""
    echo "❌ Failed to claim task. Error details:"
    echo "$TASK_RESULT" | python3 -m json.tool 2>/dev/null || echo "$TASK_RESULT"
    exit 1
elif [ "$TASK_STATUS" = "claimed" ]; then
    echo ""
    echo "✅ Task claimed successfully!"
    echo ""
    echo "📋 Task Details:"
    echo "$TASK_RESULT" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    task = data.get('task', {})
    print(f\"  Title: {task.get('title', 'Unknown')}\"  )
    print(f\"  ID: {task.get('id', 'Unknown')}\")
    print(f\"  Effort: {task.get('estimated_effort', 'Unknown')}\")
    if task.get('description'):
        print(f\"  Description: {task.get('description')}\")
    if task.get('files_locked'):
        print(f\"  Files: {', '.join(task.get('files_locked', []))}\")
except:
    print('  Could not parse task details')
" 2>/dev/null

    # Extract task ID for worktree creation
    TASK_ID=$(echo "$TASK_RESULT" | python3 -c "import json, sys; data=json.load(sys.stdin); print(data.get('task_id', 'unknown'))" 2>/dev/null || echo "unknown")
    AGENT_ID=$(echo "$TASK_RESULT" | python3 -c "import json, sys; data=json.load(sys.stdin); print(data.get('agent_id', 'unknown'))" 2>/dev/null || echo "unknown")

    # Create git worktree for isolated work
    BRANCH_NAME="agent-$AGENT_ROLE-$TASK_ID"
    WORKTREE_PATH="./worktrees/$BRANCH_NAME"

    echo ""
    echo "🌳 Creating isolated workspace..."

    # Ensure worktrees directory exists
    mkdir -p worktrees

    # Create worktree
    if git worktree add "$WORKTREE_PATH" -b "$BRANCH_NAME" 2>/dev/null; then
        echo "✅ Worktree created: $WORKTREE_PATH"
    else
        echo "⚠️  Worktree creation failed, working in main branch"
        WORKTREE_PATH="."
    fi

    # Display next steps with OS-specific Conductor app integration
    echo ""
    echo "🚀 Agent initialization complete!"
    echo "==============================================="
    echo ""
    echo "📂 Your workspace: $WORKTREE_PATH"
    echo ""
    echo "🎯 Next Steps:"
    echo ""
    # Detect preferred terminal
    FULL_PATH=$(cd "$WORKTREE_PATH" && pwd)
    
    if command -v warp >/dev/null 2>&1; then
        OPEN_CMD="warp --new-window"
        TERMINAL_NAME="Warp"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v iterm >/dev/null 2>&1; then
            OPEN_CMD="open -a iTerm"
            TERMINAL_NAME="iTerm2"
        else
            OPEN_CMD="open -a Terminal"
            TERMINAL_NAME="Terminal"
        fi
    elif [[ "$OSTYPE" == "linux"* ]]; then
        if command -v kitty >/dev/null 2>&1; then
            OPEN_CMD="kitty --directory"
            TERMINAL_NAME="Kitty"
        elif command -v alacritty >/dev/null 2>&1; then
            OPEN_CMD="alacritty --working-directory"
            TERMINAL_NAME="Alacritty"
        else
            OPEN_CMD="xdg-open"
            TERMINAL_NAME="Default terminal"
        fi
    else
        OPEN_CMD=""
        TERMINAL_NAME="Windows Terminal"
    fi

    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Option A - Conductor Desktop App (macOS only):"
        echo "   1. Open Conductor app: open -a Conductor"
        echo "   2. In Conductor: File → Add Workspace"
        echo "   3. Select directory: $FULL_PATH"
        echo "   4. Start coding with Claude Code"
        echo ""
        echo "Option B - Terminal Workflow:"
    else
        echo "💻 Terminal Workflow (Linux/Windows):"
        echo "   Conductor app is macOS-only. Use terminal workflow:"
        echo ""
    fi

    echo "   👉 Open workspace with $TERMINAL_NAME:"
    if [ -n "$OPEN_CMD" ]; then
        echo "      $OPEN_CMD \"$FULL_PATH\""
    else
        echo "      Open $TERMINAL_NAME manually and navigate to: $FULL_PATH"
    fi
    echo ""
    echo "   💡 Recommended: Use Warp terminal for AI-enhanced workflow"
    echo "      Install: https://warp.dev"
    echo ""
    echo "   📦 Session Management Options:"
    echo "      tmux new-session -d -s conductor"
    echo "      tmux send-keys \"cd $WORKTREE_PATH\" Enter"
    echo "      tmux attach -t conductor"
    echo "   cd $WORKTREE_PATH"
    echo "   # Work on your task"
    echo "   git add ."
    echo "   git commit -m \"Implement: \$(task-title)\""
    echo "   git push origin $BRANCH_NAME"
    echo "   # Create PR when ready"

    echo ""
    echo "📚 Task Resources:"
    echo "   - Role guide: $ROLE_FILE"
    echo "   - System state: .conductor/workflow-state.json"
    echo "   - Task specs: Check task description for documentation links"

    echo ""
    echo "💡 Pro Tips:"
    echo "   - Commit frequently with clear messages"
    echo "   - Run tests before pushing"
    echo "   - Update task status via PR description"

else
    echo "❌ Unexpected task status: $TASK_STATUS"
    exit 1
fi 