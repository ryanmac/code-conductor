# Architecture

## How It Works

1. **Setup Phase**: Use the universal installer to configure your project. The setup script detects your project type and configures roles.
2. **Task Creation**: Create tasks via GitHub Issues with the `conductor:task` label
3. **Agent Initialization**: Agents use the universal bootstrap to claim work
4. **Isolated Development**: Each agent works in a git worktree to prevent conflicts
5. **Automated Coordination**: GitHub Actions manage health, cleanup, and task flow

## Hybrid Role Model

The system uses a hybrid approach optimized for efficiency:

- **Default Role**: `dev` - A generalist that can handle any task without specific requirements
- **Specialized Roles**: Optional roles like `devops`, `security` for complex domains

This reduces the complexity of managing many agent types while maintaining quality for specialized work.

## File Structure

```
.conductor/
├── config.yaml           # Project configuration with auto-detected stack
├── roles/               # Role definitions
│   ├── dev.md          # Default generalist
│   ├── code-reviewer.md # AI-powered PR reviewer
│   ├── frontend.md     # UI/UX specialist
│   ├── mobile.md       # Mobile app developer
│   ├── devops.md       # CI/CD specialist
│   ├── security.md     # Security specialist
│   ├── ml-engineer.md  # ML/AI specialist
│   └── data.md         # Data engineer
├── scripts/            # Automation scripts
│   ├── conductor       # Universal AI agent command
│   ├── task-claim.py   # Atomic task assignment
│   ├── create-review-task.py # Creates review tasks from PRs
│   └── health-check.py # System monitoring
└── examples/           # Stack-specific task templates
    ├── nextjs-webapp/
    ├── python-webapp/
    ├── mobile-app/
    └── ...
```

## Core Components

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

## Key Design Patterns

1. **Atomic Operations**: GitHub's issue assignment API ensures atomic task claiming
2. **Worktree Isolation**: Each agent works in separate git worktree (`worktrees/agent-{role}-{task_id}`)
3. **Heartbeat System**: Agents update timestamps; stale work auto-cleaned after timeout
4. **File Conflict Prevention**: Worktree isolation ensures agents work on separate branches
5. **Self-Healing**: GitHub Actions monitor health, clean stale work, process issues