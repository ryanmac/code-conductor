# 🎼 Conductor-Score Usage Guide

This guide shows you two ways to use Conductor-Score: with the Conductor desktop app (macOS only) or manually with multiple terminals (all platforms).

## 🖥️ **Recommended Terminals**

**Primary: Warp** - AI-centered, tabbed, cross-platform terminal (2025)
- **macOS**: `brew install --cask warp`
- **Ubuntu/Debian**: `sudo apt install warp` or download .deb from [warp.dev](https://warp.dev)
- **Fedora/RHEL**: `sudo rpm -i warp-*.rpm`
- **Arch**: `pacman -U warp-*.pkg.tar.zst`
- **Windows**: `winget install Warp.Warp`

**Fallback Options**:
- **macOS**: iTerm2 (`brew install --cask iterm2`), Terminal.app
- **Linux**: Kitty (`apt install kitty`), Alacritty (`cargo install alacritty`), GNOME Terminal
- **Windows**: Windows Terminal with PowerShell + WSL
- **Session Management**: tmux (all platforms), screen for headless/SSH scenarios

## 🖥️ **Option A: Conductor Desktop App (Recommended)**

The Conductor app provides a streamlined experience with integrated AI sessions and workspace management.

### Prerequisites
- [Conductor Desktop App](https://conductor.build) installed
- Git repository with Conductor-Score installed

### Step-by-Step Workflow

#### 1. **Initialize Your Workspace**
```bash
# From your project root
bash .conductor/scripts/bootstrap.sh dev
```

The bootstrap script will:
- ✅ Check dependencies
- 🎯 Claim an available task
- 🌳 Create an isolated git worktree
- 📂 Print the workspace path

#### 2. **Open in Conductor App**

To open your workspace in Conductor:

**macOS Only:**
1. Open Conductor app: `open -a Conductor`
2. In Conductor: **File → Add Workspace**
3. Navigate to and select your worktree directory
4. Start coding with Claude Code

**Note:** Conductor desktop app is currently macOS-only. Linux/Windows users should use the terminal workflow below.

#### 3. **Start Your AI Session**

In Conductor:
1. The workspace opens with your task's isolated git branch
2. All task details are available in the worktree
3. Start coding with your Claude session
4. Commit and push when ready

#### 4. **Complete the Task**

```bash
# In your worktree (or via Conductor terminal)
git add .
git commit -m "Implement: [task title]"
git push origin agent-dev-task_001

# Create PR when ready
gh pr create --title "Complete: [task title]"
```

---

## 🖥️ **Option B: Multi-Terminal Workflow (All Platforms)**

For Linux/Windows users or those who prefer manual control. Conductor app is macOS-only.

### Prerequisites
- Git with worktree support
- Python 3.8+
- GitHub CLI (optional but recommended)

### Step-by-Step Workflow

#### 1. **Claim a Task**
```bash
# Terminal 1: Bootstrap
bash .conductor/scripts/bootstrap.sh dev
```

This creates an isolated worktree like:
```
worktrees/agent-dev-task_001/
```

#### 2. **Work in the Isolated Environment**

**Option 2A: Using tmux (Recommended for Linux/Unix)**
```bash
# Create a new tmux session
tmux new-session -d -s conductor-task
tmux send-keys "cd worktrees/agent-dev-task_001" Enter
tmux split-window -h
tmux send-keys "cd worktrees/agent-dev-task_001" Enter
tmux attach -t conductor-task
# Now you have two panes in the worktree directory
```

**Option 2B: Using screen**
```bash
# Create a new screen session
screen -S conductor-task
# In screen: cd worktrees/agent-dev-task_001
# Ctrl+A, c to create new window
# Ctrl+A, " to split horizontally
```

**Option 2C: Multiple terminal windows**
```bash
# Terminal 2: Development
cd worktrees/agent-dev-task_001

# Your task details are here:
cat .conductor/workflow-state.json  # Check your task
ls -la                              # See the isolated branch

# Start your development session
# (Open your preferred editor, IDE, or Claude session here)
```

#### 3. **Monitor System Status** (Optional)
```bash
# Terminal 3: Monitoring
python .conductor/scripts/update-status.py
python .conductor/scripts/health-check.py
```

#### 4. **Complete and Submit**
```bash
# In Terminal 2 (worktree)
git add .
git commit -m "feat: implement user authentication system

- Add JWT token handling
- Implement login/logout endpoints
- Add password hashing
- Include comprehensive tests

Closes: task_001"

git push origin agent-dev-task_001

# Create pull request
gh pr create \
  --title "feat: implement user authentication system" \
  --body "Implements task_001: Add user authentication

## Changes
- JWT token handling
- Login/logout endpoints
- Password hashing with bcrypt
- 100% test coverage

## Testing
- All tests pass
- Manual testing completed
- Security review ready"
```

---

## 🔧 **Advanced Usage**

### Managing Multiple Agents

You can run multiple agents simultaneously:

```bash
# Terminal 1: Dev agent
bash .conductor/scripts/bootstrap.sh dev

# Terminal 2: DevOps agent
bash .conductor/scripts/bootstrap.sh devops

# Terminal 3: Security review
bash .conductor/scripts/bootstrap.sh security
```

Each gets an isolated worktree:
```
worktrees/
├── agent-dev-task_001/
├── agent-devops-task_002/
└── agent-security-task_003/
```

### Checking System Health

```bash
# Quick status check
python .conductor/scripts/health-check.py

# Detailed system metrics
python .conductor/scripts/update-status.py

# Clean up stale work
python .conductor/scripts/cleanup-stale.py

# Validate configuration
python .conductor/scripts/validate-config.py
```

### Creating Tasks

#### Via GitHub Issues (Recommended)
1. Create a GitHub Issue
2. Add the `conductor:task` label
3. Use the issue template for structured task data
4. The system automatically converts it to a task

#### Via Direct State Modification
```bash
# Edit the state file directly (advanced)
nano .conductor/workflow-state.json

# Add to "available_tasks" array
{
  "id": "custom_task_001",
  "title": "Your task title",
  "description": "Detailed description",
  "estimated_effort": "medium",
  "required_skills": [],
  "files_locked": ["src/api/auth.py"]
}
```

### Worktree Management

```bash
# List all worktrees
git worktree list

# Remove completed worktree manually
git worktree remove worktrees/agent-dev-task_001

# Clean up all stale worktrees
python .conductor/scripts/cleanup-worktrees.py

# Force cleanup (removes uncommitted changes)
python .conductor/scripts/cleanup-worktrees.py --force
```

---

## 🚀 **Pro Tips**

### Conductor App Users
- **Workspace persistence**: Conductor remembers your workspaces
- **Session history**: Previous conversations are saved per workspace
- **File watching**: Auto-detects file changes for context
- **Terminal integration**: Built-in terminal for git commands

### Multi-Terminal Users
- **Use tmux/screen**: Manage multiple sessions easily
- **Shell aliases**: Create shortcuts for common commands
- **Git hooks**: Automate task status updates
- **IDE integration**: Many IDEs support worktree workflows

### Universal Tips
- **Commit often**: Small, atomic commits are easier to review
- **Clear messages**: Use conventional commit format
- **Test locally**: Run tests before pushing
- **Update task status**: Keep the system informed of progress

---

## 🔍 **Troubleshooting**

### Common Issues

**"No tasks available"**
```bash
# Check if tasks exist
cat .conductor/workflow-state.json | jq '.available_tasks'

# Create a test task via GitHub issue
gh issue create --title "Test task" --label "conductor:task"
```

**"Worktree creation failed"**
```bash
# Check git status
git status

# Ensure clean working directory
git stash

# Try again
bash .conductor/scripts/bootstrap.sh dev
```

**"Permission denied" on scripts**
```bash
# Make scripts executable
chmod +x .conductor/scripts/*.py
chmod +x .conductor/scripts/*.sh
```

**Conductor app won't open workspace**
```bash
# Check if path exists
ls -la /path/to/worktree

# Open Conductor app (macOS only)
open -a Conductor

# Then use File → Add Workspace to select the directory
```

### Getting Help

- **Validate setup**: `python .conductor/scripts/validate-config.py`
- **Check dependencies**: `python .conductor/scripts/dependency-check.py`
- **System health**: `python .conductor/scripts/health-check.py`
- **GitHub issues**: [Report bugs](https://github.com/ryanmac/conductor-score/issues)
- **Discussions**: [Ask questions](https://github.com/ryanmac/conductor-score/discussions)

---

**Ready to orchestrate your development workflow?** Pick your preferred approach and start building! 🎼 