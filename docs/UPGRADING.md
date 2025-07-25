# Upgrading Code Conductor

Keep your Code Conductor installation up-to-date with the latest features!

## Automatic Upgrade Detection

Simply run the same installation command in your project:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/ryanmac/code-conductor/main/conductor-init.sh)
```

The installer will:
- ✅ Detect your existing installation and version
- ✅ Prompt to upgrade, reinstall, or cancel
- ✅ Preserve your configurations and customizations
- ✅ Update only core scripts and workflows
- ✅ Show what's new after upgrading

## What Gets Updated
- `.conductor/scripts/` - Core conductor commands
- `.conductor/roles/` - Latest role definitions
- `.github/workflows/` - Updated GitHub Actions
- `setup.py`, `requirements.txt` - Dependency updates

## What Gets Preserved
- `.conductor/config.yaml` - Your project configuration
- `CLAUDE.md` - Your custom AI instructions
- All existing tasks and work in progress
- Git worktrees and agent states

## Using Claude Code for Upgrades

Want to upgrade in seconds? Copy this power prompt into Claude Code:

```
We need the latest Code Conductor features. Upgrade our installation to unlock enhanced task management and duplicate prevention.

Run: bash <(curl -fsSL https://raw.githubusercontent.com/ryanmac/code-conductor/main/conductor-init.sh)
Choose option 1 (Upgrade) and verify with ./conductor status
```

**🚀 See [CLAUDE_CODE_PROMPT.md](../CLAUDE_CODE_PROMPT.md) for game-changing automation prompts** that transform your project into an agentic development powerhouse.