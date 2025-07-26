# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Code Conductor is an AI agent coordination system designed to orchestrate multiple AI coding agents (like Claude Code, Conductor, Warp) working on the same codebase. It provides GitHub-native task management with automatic conflict prevention through git worktrees.

**IMPORTANT**: This is a template repository. When you encounter Code Conductor files in a project, they have been imported to enable automated agent coordination. Work autonomously based on GitHub Issues with the `conductor:task` label and the guidance in these files.

## Documentation Map

**CRITICAL**: When starting work on any task, check if `.conductor/documentation-map.yaml` exists. This file contains:
- Comprehensive project analysis and structure
- Technology stack details and dependencies  
- List of completed vs. pending features
- Implementation status and critical paths
- Architectural decisions and constraints

If this file exists, load it to understand the project context before beginning work. This map is created by the `[INIT]` discovery task and provides essential context for all subsequent tasks.

## Key Development Commands

### Running Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python tests/test_basic.py
python tests/test_stack_detection.py
```

### Linting and Formatting
```bash
# Check code formatting (without making changes)
black --check .conductor/scripts/ setup.py

# Apply formatting
black .conductor/scripts/ setup.py

# Run linting
flake8 .conductor/scripts/ setup.py --max-line-length=88 --extend-ignore=E203,W503
```

### Validation Commands
```bash
# Validate conductor configuration
python .conductor/scripts/validate-config.py

# Check system dependencies
python .conductor/scripts/dependency-check.py

# Run health check
python .conductor/scripts/health-check.py
```

## Architecture Overview

### Core Components

1. **Setup System** (`setup.py`)
   - Interactive/auto configuration wizard
   - Detects technology stack automatically
   - Configures agent roles based on project type
   - Creates GitHub workflows for automation

2. **Task Management** (GitHub Issues)
   - GitHub Issues with `conductor:task` label serve as tasks
   - Issues have unique numbers, descriptions, success criteria
   - GitHub's atomic operations prevent race conditions
   - Native integration with GitHub Projects and Actions

3. **Agent Roles** (`.conductor/roles/`)
   - `dev.md` - Default generalist role for most tasks
   - Specialized roles: `devops`, `security`, `frontend`, `mobile`, `ml-engineer`, `data`
   - `code-reviewer` - AI-powered PR reviews (always included)
   - Hybrid model: prefer `dev` role unless task requires specialization

4. **Agent Coordination** (`.conductor/scripts/`)
   - `conductor` - Universal agent command (primary interface)
   - `task-claim.py` - Task assignment via GitHub Issue assignment
   - `health-check.py` - Monitor agent heartbeats
   - `cleanup-stale.py` - Remove abandoned work
   - Git worktrees provide isolation between agents

5. **GitHub Integration**
   - Issues become tasks via `conductor:task` label
   - Actions run health checks every 15 minutes
   - AI code reviews on all PRs
   - Status dashboard via `conductor:status` issue

### Key Design Patterns

1. **Atomic Operations**: GitHub's issue assignment API ensures atomic task claiming
2. **Worktree Isolation**: Each agent works in separate git worktree (`worktrees/agent-{role}-{task_id}`)
3. **Heartbeat System**: Agents update timestamps; stale work auto-cleaned after timeout
4. **File Conflict Prevention**: Worktree isolation ensures agents work on separate branches
5. **Self-Healing**: GitHub Actions monitor health, clean stale work, process issues

### Configuration Structure

```yaml
# .conductor/config.yaml
project_name: string
documentation: 
  main: string (path to main docs)
  additional: [array of paths]
technology_stack:
  languages: [detected languages]
  frameworks: [detected frameworks]
  tools: [detected build tools]
roles:
  default: "dev"
  specialized: [list of specialized roles]
github_integration:
  enabled: boolean
  issue_to_task: boolean
  pr_reviews: boolean
worktree_retention_days: number (default 7)
```

## Development Workflow

When modifying code-conductor itself:

1. Make changes in appropriate files:
   - Core scripts: `.conductor/scripts/`
   - Role definitions: `.conductor/roles/`
   - Setup logic: `setup.py`

2. Run validation after changes:
   ```bash
   python .conductor/scripts/validate-config.py
   black .conductor/scripts/ setup.py
   flake8 .conductor/scripts/ setup.py --max-line-length=88
   python -m pytest tests/ -v
   ```

3. Test setup flow:
   ```bash
   # Create test environment
   mkdir /tmp/test-conductor && cd /tmp/test-conductor
   git init
   # Copy conductor files and run setup
   python setup.py --auto
   ```

<!-- CONDUCTOR:START -->
## 🤖 AI Agent Quick Start

**IMPORTANT**: Always run from the project root directory where Code Conductor is configured!

### 🚀 The Universal Kickoff Prompt

Start every Code Conductor session with:

```
Ultrathink: What task will create the most value? Find it, claim it, complete it.
```

This prompt triggers deep analysis, focuses on value, and guides you through the complete workflow.

### Essential Commands

```bash
# Start work as your role (from project root)
./conductor start [role]

# Check your current task status
./conductor status

# Update progress on current task
./conductor progress  # or: ./conductor p

# Complete task and create PR
./conductor complete

# List available tasks
./conductor tasks

# Diagnose and fix issues
./conductor recover  # or: ./conductor debug, ./conductor fix
```

### Available Roles
- `dev` - General development (default)
- `frontend` (aliases: fe, front) - UI/React/Vue work
- `backend` (aliases: be, back) - API/server work  
- `devops` (aliases: ops) - Infrastructure/CI
- `security` (alias: sec) - Security tasks
- `mobile` - iOS/Android development
- `ml` (aliases: ai, ml-engineer) - Machine learning
- `data` - Data engineering/analytics

### Example Session
```bash
cd /path/to/project  # MUST be in project root
./conductor start frontend
# ... work on task ...
./conductor progress  # Post update to GitHub
# ... continue work ...
./conductor complete
```
<!-- CONDUCTOR:END -->

## Autonomous Operation Guidelines

**IMPORTANT**: Code Conductor is designed for FULLY AUTONOMOUS OPERATION. AI agents should complete entire workflows without waiting for human approval.

When working in a project with Code Conductor:

1. **Start work**: Use `./conductor start [role]` from the project root
2. **Track progress**: Use `./conductor progress` to post updates to GitHub
3. **Check status**: Use `./conductor status` to see your current task
4. **Complete work**: Use `./conductor complete` to finish and create PR
5. **Fix issues**: Use `./conductor recover` if you encounter problems
6. **Work in isolation**: The conductor command creates your worktree automatically
7. **Validate changes**: Always run the project's test/lint commands before committing

### Full Autonomy Principles

- **No human gates**: Tasks should be completable end-to-end without human intervention
- **Auto-generate tasks**: When running init tasks, use `python .conductor/scripts/generate-tasks-from-map.py --auto` (if available)
- **Self-validation**: Agents validate their own work before marking tasks complete
- **Continuous flow**: Complete tasks, create PRs, and move to the next task without pausing
- **Trust the process**: The system has guardrails; agents should proceed confidently

### Creating New Tasks - IMPORTANT Duplicate Prevention

**CRITICAL**: Before creating any new GitHub issue, you MUST check for duplicates:

1. **Search existing issues thoroughly**:
   ```bash
   # Check all open conductor tasks
   gh issue list --label "conductor:task" --state open --limit 100
   
   # Search by keywords
   gh issue list --search "your keywords here" --state all
   
   # Check closed issues too
   gh issue list --label "conductor:task" --state closed --limit 50
   ```

2. **Analyze similarity**:
   - Compare titles for semantic similarity
   - Check issue body content for overlapping requirements
   - Look for issues that might encompass your proposed task

3. **Only create if truly unique**:
   - No existing issue covers the same functionality
   - Not a subset of an existing larger task
   - Adds distinct value to the project

4. **If similar issue exists**:
   - Add a comment to the existing issue with additional details
   - Consider if the existing issue should be expanded
   - Do NOT create a duplicate

Example duplicate check:
```bash
# Before creating "Add user authentication"
gh issue list --search "auth OR authentication OR login" --state all

# Before creating "Improve error handling"  
gh issue list --search "error OR exception OR handling" --state all

# Review the results carefully before proceeding
```

### Managing Your Todo List - Prevent Internal Duplicates

**IMPORTANT**: Also maintain a clean internal todo list:

1. **Before adding todos**: Check if similar tasks already exist in your list
2. **Consolidate related items**: Instead of multiple similar todos, create one comprehensive task
3. **Clean up completed work**: Mark todos as completed immediately after finishing
4. **Remove obsolete items**: If an external issue is closed or no longer relevant, remove related todos

Example todo management:
```
BAD:
- Add login functionality
- Implement user authentication  
- Create auth system
- Add password reset

GOOD:
- Implement complete authentication system (login, logout, password reset)
```

This prevents both external (GitHub issues) and internal (todo list) duplication.

## GitHub Authentication

Code Conductor uses GitHub's built-in authentication for all operations. No manual token setup is required for most users!

### Default Setup (Recommended)
The workflows generated by Code Conductor automatically use GitHub Actions' built-in `${{ github.token }}`, which provides:
- ✅ Read/write access to issues, pull requests, and code
- ✅ Ability to create and manage labels
- ✅ No setup required - works out of the box!

### Advanced Setup (Optional)
Only create a Personal Access Token if you need:
- Higher API rate limits (5,000/hour instead of 1,000/hour)
- Cross-repository access
- Ability to trigger other workflows

For detailed setup instructions and troubleshooting, see [.conductor/GITHUB_TOKEN_SETUP.md](.conductor/GITHUB_TOKEN_SETUP.md).

## Common Tasks

### Adding a New Role
1. Create role definition: `.conductor/roles/[role-name].md`
2. Update setup.py to include in role options
3. Add example tasks in `.conductor/examples/`

### Modifying Task Processing
1. Core logic in `task-claim.py` for assignment
2. State management via GitHub Issues and labels
3. Update validation in `validate-config.py`

### Extending Stack Detection
1. Detection logic in `setup.py` (detect_technology_stack function)
2. Add patterns for new frameworks/languages
3. Update role recommendations based on stack

### Uninstalling Code Conductor
To remove Code Conductor from a project:
```bash
python uninstall.py              # Interactive removal
python uninstall.py --force      # Remove without confirmation
python uninstall.py --dry-run    # Preview what will be removed
```

The uninstaller safely removes all conductor components while preserving user files.
See `uninstall.py` for implementation details.

## Important Notes

- Always use GitHub CLI commands for state changes to ensure consistency
- Maintain backward compatibility with existing conductor setups
- Test with multiple Python versions (3.9-3.12)
- Ensure GitHub Actions workflows remain functional
- Keep agent bootstrap process simple and universal

## Self-Validation Protocols

When working autonomously, validate your actions:

### Pre-Work Validation
```python
# Before starting any task
validations = {
    "environment": check_dependencies(),
    "github_auth": verify_github_cli_auth(),
    "available_tasks": check_unassigned_issues(),
    "git": verify_clean_worktree()
}
if all(validations.values()):
    proceed_with_task()
else:
    handle_validation_failure(validations)
```

### Post-Work Validation
```python
# After completing changes
post_checks = {
    "tests": run_project_tests(),
    "lint": run_linting_commands(),
    "build": verify_build_success(),
    "pr_created": verify_pull_request_created()
}
```

### Fallback Decision Tree
```
Validation Failed?
├─ Missing dependency → Install or use alternative
├─ GitHub auth failed → Run 'gh auth login' or check credentials
├─ No available tasks → Create new issue or wait for assignments
├─ Test failure → Fix or document known issue
└─ Build failure → Rollback and try simpler approach
```