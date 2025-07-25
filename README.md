# 🎼 Code Conductor

<img width="800" height="800" alt="image" src="https://github.com/user-attachments/assets/be1b47d2-8384-4012-b437-4d8316eaf9f7" />

**Ship 10x faster with AI agents working in parallel.**

## What Does This Do For Me?

Code Conductor orchestrates multiple AI coding agents (like Claude Code) to work on your codebase simultaneously—without conflicts. 

**Instead of juggling tasks manually**, you create GitHub Issues and watch AI agents claim, implement, and ship features autonomously. It's like having a dev team that never sleeps.

### Real Results
- 🚀 **Ship features in hours, not weeks** - Multiple agents work in parallel
- 🎯 **Zero coordination overhead** - Agents handle their own task management
- 🔒 **No merge conflicts** - Each agent works in isolated git worktrees
- 🤖 **Works with Claude Code** - Your favorite AI coding assistant, multiplied

## How Do I Install It? (60 seconds)

Run this one command in your project's root directory:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/ryanmac/code-conductor/main/conductor-init.sh)
```

**That's it.** The installer auto-detects your tech stack (React, Python, Go, etc.) and configures everything. No GitHub token needed.

### Or Let Claude Code Do It
Paste this into Claude Code:
```
I need to move faster. Install Code Conductor into this project so we can run multiple Claude Code agents at once.

Execute: bash <(curl -fsSL https://raw.githubusercontent.com/ryanmac/code-conductor/main/conductor-init.sh)
```

## How Does It Work?

### 1. Create Tasks
Create GitHub Issues with the `conductor:task` label. Each issue becomes a task for agents to claim.

### 2. Launch Agents
```bash
./conductor start dev  # Start a generalist developer agent
./conductor start frontend  # Start a frontend specialist
```

### 3. Watch Them Work
Agents automatically:
- Claim the best matching task
- Work in isolated git worktrees (no conflicts!)
- Create pull requests when done
- Move to the next task

### The Magic: Isolated Worktrees
Each agent works in their own git worktree—like having multiple copies of your repo. Agent A can refactor the auth system while Agent B adds a new feature, with zero conflicts.

## Quick Example

```bash
# 1. Install Code Conductor (60 seconds)
bash <(curl -fsSL https://raw.githubusercontent.com/ryanmac/code-conductor/main/conductor-init.sh)

# 2. Create a task via GitHub Issue
gh issue create --label "conductor:task" --title "Add dark mode toggle"

# 3. Launch an agent
./conductor start frontend

# 4. Agent claims task, implements feature, creates PR
# 5. Launch more agents to parallelize work!
```

## Learn More

📚 **[Full Documentation →](docs/)**
- [Installation Guide](docs/INSTALLATION.md) - All setup options
- [Stack Support](docs/STACK_SUPPORT.md) - Works with React, Vue, Python, Go, and more
- [Architecture](docs/ARCHITECTURE.md) - How it all works under the hood
- [AI Code Review](docs/AI_CODE_REVIEW.md) - Smart, opt-in PR reviews
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues and solutions

🚀 **[Power User Prompts](CLAUDE_CODE_PROMPT.md)** - Game-changing automation with Claude Code

## Community

- 🐛 **Found a bug?** [Report it](https://github.com/ryanmac/code-conductor/issues)
- 💡 **Have an idea?** [Start a discussion](https://github.com/ryanmac/code-conductor/discussions)
- 🛠️ **Want to contribute?** [See our guide](.github/CONTRIBUTING.md)
- 𝕏 **Share your success** Mention [@ryanmac](https://x.com/ryanmac) with #CodeConductor

---

**Stop juggling tasks. Start shipping features.** 🎼
