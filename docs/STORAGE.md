# Storage Management

## Disk Usage

Each agent creates a Git worktree, which uses disk space:
- Small projects: ~50MB per worktree
- Medium projects: ~100-150MB per worktree  
- Large projects: ~200MB+ per worktree

## Automatic Cleanup

Stale worktrees are automatically cleaned up:
- Default retention: 7 days
- Configurable via `worktree_retention_days` in config.yaml
- GitHub Actions run cleanup every 15 minutes

## Manual Cleanup

```bash
# List all worktrees
git worktree list

# Remove specific worktree
git worktree remove worktrees/agent-dev-42

# Remove all stale worktrees
python .conductor/scripts/cleanup-stale.py --timeout 0

# Alias for quick cleanup (if configured)
gtclean
```

## Best Practices

1. **Large Projects**: Set `worktree_retention_days: 3` in config.yaml
2. **Regular Cleanup**: Run `gtclean` weekly
3. **Monitor Usage**: Use `du -sh worktrees/` to check disk usage
4. **CI/CD Servers**: Set aggressive cleanup (1-2 days retention)

## Storage Optimization

For projects with limited disk space:

```yaml
# .conductor/config.yaml
worktree_retention_days: 2
max_concurrent_agents: 3
```

This limits the number of worktrees and reduces retention time.