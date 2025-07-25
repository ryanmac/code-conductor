# Agent Workflow

## AI Agent Quick Start

After setup, Code Conductor creates a `CLAUDE.md` file with AI agent instructions. For Claude Code or other AI coding assistants:

```bash
# The ONLY command AI agents need to know:
./conductor start [role]
```

This single command:
- ✅ Shows your role and capabilities
- ✅ Lists available tasks (creates demo tasks if needed)
- ✅ Claims the best matching task automatically
- ✅ Creates an isolated git worktree
- ✅ Provides all context needed to start

## The Perfect Kickoff Prompt

Start any Claude Code session with this value-focused prompt:

```
Ultrathink: What task will create the most value? Find it, claim it, complete it.
```

This prompt:
- Triggers deep analysis with "ultrathink"
- Focuses on value creation over busy work
- Provides clear action steps: find → claim → complete
- Works with any role or project type

**Pro tip**: Add this to your text expander (e.g., `;ustart`) for instant agent activation.

## Example AI Agent Session

```
> ./conductor start frontend

🤖 Code Conductor Agent: frontend
==================================
📋 Role: frontend

📊 Available Tasks:
  #42: Implement dark mode toggle
  #43: [INIT] Discover project documentation and create task map
  #44: Add responsive navigation menu

🎯 Claiming task...
✅ Claimed task #42
📁 Workspace: worktrees/agent-frontend-42

Next: cd worktrees/agent-frontend-42
```

## AI Agent Workflow

1. **Start work**: `./conductor start dev`
2. **Implement**: Work in the created worktree
3. **Complete**: `./conductor complete`
4. **Repeat**: Automatically moves to next task

## Smart Task Discovery

For existing projects, Code Conductor creates a special discovery task that AI agents can claim to:
- Map all project documentation
- Identify implemented vs missing features
- Generate 10-20 specific development tasks
- Create proper GitHub issues automatically

## Launching an Agent

**Option A: Conductor Desktop App (macOS only)**
```bash
export AGENT_ROLE=dev  # or devops, security, etc.
./conductor start
# Follow the printed instructions to open in Conductor app
```

**Option B: Multiple Terminals (All Platforms)**
```bash
./conductor start dev
cd worktrees/agent-dev-[task_id]
# Use tmux or screen for session management on Linux/Windows
# Start your Claude Code session in the worktree
```

## Agent Lifecycle

1. **Initialize**: Load role definition and check dependencies
2. **Claim Task**: Atomically claim an available task
3. **Create Worktree**: Isolated git workspace for conflict-free work
4. **Execute Task**: Follow specifications and success criteria
5. **Report Status**: Update heartbeat and progress
6. **Complete/Idle**: Mark complete or report idle for cleanup

## Universal Bootstrap Prompt

The system provides a single prompt that works for any agent:

```
You are a Claude Code agent in a Code Conductor coordinated project.
ROLE: {role}
PROJECT: {project_name}

1. Read your role definition: .conductor/roles/{role}.md
2. Check available tasks: gh issue list -l 'conductor:task' --assignee '!*'
3. Claim a task: python .conductor/scripts/task-claim.py --role {role}
4. Work in your isolated worktree
5. Commit and push changes when complete

Note: Heartbeats are automatically managed by GitHub Actions.
```