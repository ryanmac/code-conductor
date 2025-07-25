# 🎼 Code Conductor

<img width="800" height="800" alt="image" src="https://github.com/user-attachments/assets/be1b47d2-8384-4012-b437-4d8316eaf9f7" />

**Orchestrate multiple AI coding agents. Ship 10x faster.**

## The Problem

You're using Claude Code to ship features, but you're still working sequentially. One task at a time. One PR at a time. Meanwhile, your backlog keeps growing.

## The Solution

Code Conductor lets you run multiple AI agents in parallel—each working on different features simultaneously. No conflicts. No coordination overhead. Just pure, parallelized productivity.

**Transform your workflow:**
- 🚀 **Hours, not weeks** - Multiple agents tackle your backlog in parallel
- 🔒 **Zero merge conflicts** - Each agent works in isolated git worktrees
- 🤖 **Works with Claude Code** - Your favorite AI assistant, multiplied
- 🎯 **Self-managing** - Agents claim tasks, implement, and ship autonomously

## Quick Start

One command. 60 seconds. Done.

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/ryanmac/code-conductor/main/conductor-init.sh)
```

The installer auto-detects your stack (React, Python, Go, etc.) and configures everything. **No GitHub tokens needed. No complex setup.**

✨ **What you get:**
- ✅ GitHub Actions workflows that use built-in authentication
- ✅ No manual token creation or repository secrets required
- ✅ AI code reviews work automatically on all PRs
- ✅ Language-agnostic setup (no Python CI/CD added to non-Python projects)

**For Claude Code (non-interactive):**
```bash
curl -fsSL https://raw.githubusercontent.com/ryanmac/code-conductor/main/conductor-init.sh | bash -s -- --auto
```

**Or paste this prompt into Claude Code:**
```
I need to move faster. Install Code Conductor into this project so we can run multiple Claude Code agents at once.

Execute: curl -fsSL https://raw.githubusercontent.com/ryanmac/code-conductor/main/conductor-init.sh | bash -s -- --auto
```

## See It In Action

```bash
# Create a task (GitHub Issue)
gh issue create --label "conductor:task" --title "Add dark mode toggle"

# Launch an agent
./conductor start frontend

# Watch it work
# ✓ Claims task #42
# ✓ Creates isolated worktree
# ✓ Implements feature
# ✓ Opens pull request
# ✓ Moves to next task

# Launch more agents to parallelize
./conductor start backend
./conductor start dev
```

**The secret:** Each agent works in its own git worktree—like having multiple copies of your repo. Agent A refactors authentication while Agent B adds dark mode. Zero conflicts.

## Learn More

📚 **[Full Documentation →](docs/)**
- [Installation Guide](docs/INSTALLATION.md) - All setup options
- [Stack Support](docs/STACK_SUPPORT.md) - Works with React, Vue, Python, Go, and more
- [Architecture](docs/ARCHITECTURE.md) - How it all works under the hood
- [AI Code Review](docs/AI_CODE_REVIEW.md) - Smart, opt-in PR reviews
- [FAQ](docs/FAQ.md) - Common questions about tokens, Python, and workflows
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues and solutions

🚀 **[Power User Prompts](CLAUDE_CODE_PROMPT.md)** - Game-changing automation with Claude Code

## Community

- 🐛 **Found a bug?** [Report it](https://github.com/ryanmac/code-conductor/issues)
- 💡 **Have an idea?** [Start a discussion](https://github.com/ryanmac/code-conductor/discussions)
- 🛠️ **Want to contribute?** [See our guide](.github/CONTRIBUTING.md)
- 𝕏 **Share your success** Mention [@ryanmac](https://x.com/ryanmac) with #CodeConductor

---

**Stop juggling tasks. Start shipping features.** 🎼
