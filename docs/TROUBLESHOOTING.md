# Troubleshooting

## Common Issues

### No tasks available
- Check GitHub issues: `gh issue list -l 'conductor:task'`
- Verify no file conflicts blocking tasks
- Create new tasks: `gh issue create --label 'conductor:task'`

### Agent can't claim tasks
- Run `python .conductor/scripts/dependency-check.py`
- Ensure GitHub CLI is authenticated: `gh auth status`
- Check git repository is clean: `git status`
- Note: No GitHub token setup required—workflows use built-in authentication

### File conflicts
- System prevents these automatically
- If occurs, check worktree isolation
- Run cleanup: `python .conductor/scripts/cleanup-stale.py`

## Debug Commands

```bash
# Check dependencies
python .conductor/scripts/dependency-check.py

# View system state
gh issue list -l 'conductor:task' --json state,assignees,title

# Force cleanup
python .conductor/scripts/cleanup-stale.py --timeout 0

# Validate configuration
python .conductor/scripts/validate-config.py
```

## Storage Footprint

**Disk Usage**: Each agent creates a Git worktree (~50-200MB depending on project size)
- **Cleanup**: Run `gtclean` weekly to remove abandoned worktrees
- **Monitor**: Use `gtw` to list active worktrees
- **Automatic**: Stale worktrees (>7 days inactive) are auto-archived via GitHub Actions

**Pro tip**: Large projects should set `worktree_retention_days: 3` in config.yaml