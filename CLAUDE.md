# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Code Conductor is an AI agent coordination system designed to orchestrate multiple AI coding agents (like Claude Code, Conductor, Warp) working on the same codebase. It provides GitHub-native task management with automatic conflict prevention through git worktrees.

**IMPORTANT**: This is a template repository. When you encounter Code Conductor files in a project, they have been imported to enable automated agent coordination. Work autonomously based on GitHub Issues with the `conductor:task` label and the guidance in these files.

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
   - `bootstrap.sh` - Universal agent initialization
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

## Autonomous Operation Guidelines

When working in a project with Code Conductor:

1. **Check for tasks**: Run `python .conductor/scripts/generate-summary.py` to see available work
2. **Claim a task**: Use `python .conductor/scripts/task-claim.py --role [your-role]`
3. **Work in isolation**: The bootstrap script creates your worktree automatically
4. **Validate changes**: Always run the project's test/lint commands before committing
5. **Complete work**: Close the GitHub Issue when done

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