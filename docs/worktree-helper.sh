#!/bin/bash
# Code Conductor Worktree Helper
# Source this file for convenient worktree management aliases

# Terminal detection and opening functions
gtopen() {
    local worktree_path=${1:-$(find worktrees -name "agent-*" -type d | head -1)}
    if [ -z "$worktree_path" ]; then
        echo "❌ No worktree found"
        return 1
    fi

    echo "📂 Opening $worktree_path in terminal..."
    if command -v warp >/dev/null 2>&1; then
        warp --new-window "$worktree_path"
    elif command -v code >/dev/null 2>&1; then
        code "$worktree_path"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        open -a iTerm "$worktree_path" 2>/dev/null || open -a Terminal "$worktree_path"
    elif [[ "$OSTYPE" == "linux"* ]]; then
        kitty --directory "$worktree_path" 2>/dev/null || alacritty --working-directory "$worktree_path" 2>/dev/null || xdg-open "$worktree_path"
    else
        echo "💡 Navigate to: $worktree_path"
    fi
}

gtwarp() {
    if ! command -v warp >/dev/null 2>&1; then
        echo "⚠️  Warp not installed. Install with:"
        if [[ "$OSTYPE" == "darwin"* ]]; then
            echo "   brew install --cask warp"
        elif [[ "$OSTYPE" == "linux"* ]]; then
            echo "   Visit https://warp.dev/linux-terminal"
        else
            echo "   winget install Warp.Warp"
        fi
        return 1
    fi
    gtopen "$@"
}

# Alias: gtr (git-worktree-runner) - Quick worktree navigation
gtr() {
    local task_id="$1"
    if [ -z "$task_id" ]; then
        echo "Usage: gtr <task_id>"
        echo "Available worktrees:"
        find worktrees -maxdepth 1 -type d -name "agent-*" 2>/dev/null | sed 's|worktrees/||' | sed 's/^/  /'
        return 1
    fi

    local worktree_path="worktrees/agent-dev-$task_id"
    if [ ! -d "$worktree_path" ]; then
        # Try to find any agent with this task ID
        worktree_path=$(find worktrees -maxdepth 1 -type d -name "*-$task_id" 2>/dev/null | head -1)
        if [ -z "$worktree_path" ]; then
            echo "❌ Worktree for task $task_id not found"
            return 1
        fi
    fi

    echo "📂 Switching to $worktree_path"
    cd "$worktree_path" || return 1
}

# Alias: gtl (git-task-list) - List available tasks
gtl() {
    echo "📋 Available Tasks:"
    if command -v gh >/dev/null 2>&1; then
        gh issue list -l 'conductor:task' --assignee '!*' --state open --limit 20 | head -20 || echo "  No tasks found"
    else
        echo "  Install GitHub CLI for task listing:"
        echo "    brew install gh (macOS)"
        echo "    See: https://cli.github.com/manual/installation"
    fi
}

# Alias: gts (git-task-status) - Show current task status
gts() {
    echo "🔄 System Status:"
    if [ -f ".conductor/scripts/health-check.py" ]; then
        python .conductor/scripts/health-check.py
    else
        echo "  Health check script not found"
    fi
}

# Alias: gtc (git-task-claim) - Claim a task
gtc() {
    local role="${1:-dev}"
    echo "🎯 Claiming task for role: $role"
    bash .conductor/scripts/bootstrap.sh "$role"
}

# Alias: gtw (git-task-worktrees) - List all worktrees
gtw() {
    echo "🌳 Git Worktrees:"
    git worktree list 2>/dev/null || echo "  No worktrees found"
}

# Alias: gtclean (git-task-clean) - Clean up stale worktrees
gtclean() {
    echo "🧹 Cleaning up stale worktrees..."
    if [ -f ".conductor/scripts/cleanup-worktrees.py" ]; then
        python .conductor/scripts/cleanup-worktrees.py "$@"
    else
        echo "  Cleanup script not found"
    fi
}

# Alias: gti (git-task-issue) - View a specific task issue
gti() {
    local issue_number="$1"
    if [ -z "$issue_number" ]; then
        echo "Usage: gti <issue_number>"
        return 1
    fi
    if command -v gh >/dev/null 2>&1; then
        gh issue view "$issue_number"
    else
        echo "❌ GitHub CLI not installed"
    fi
}

# Alias: gtn (git-task-new) - Create a new task issue
gtn() {
    if command -v gh >/dev/null 2>&1; then
        echo "📝 Creating new task issue..."
        echo "💡 Tip: Use clear, actionable titles"
        gh issue create --label 'conductor:task' --label 'priority:medium' --label 'effort:medium'
    else
        echo "❌ GitHub CLI not installed"
    fi
}

# Alias: gtst (git-task-status) - View system status issue
gtst() {
    if command -v gh >/dev/null 2>&1; then
        echo "📊 Viewing system status..."
        local status_issue=$(gh issue list -l 'conductor:status' --state open --limit 1 --json number | jq -r '.[0].number // empty')
        if [ -n "$status_issue" ]; then
            gh issue view "$status_issue"
        else
            echo "❌ No status issue found. Run: python .conductor/scripts/update-status.py"
        fi
    else
        echo "❌ GitHub CLI not installed"
    fi
}

# Print available commands when sourced
echo "🎼 Code Conductor Worktree Helper Loaded"
echo ""
echo "Available commands:"
echo "  gtr <task_id>  - Switch to task worktree"
echo "  gtl            - List available tasks (GitHub Issues)"
echo "  gts            - Show system health check"
echo "  gtst           - View system status issue"
echo "  gti <number>   - View specific task issue"
echo "  gtn            - Create new task issue"
echo "  gtc [role]     - Claim a task (default: dev)"
echo "  gtw            - List all worktrees"
echo "  gtclean        - Clean up stale worktrees"
echo "  gtopen [path]  - Open worktree in best available terminal"
echo "  gtwarp [path]  - Open worktree in Warp (with install check)"
echo ""
echo "💡 Pro tip: Add 'source docs/worktree-helper.sh' to your ~/.bashrc" 