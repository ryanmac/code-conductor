# Monitoring

## System Health

```bash
# Check local status
python .conductor/scripts/health-check.py

# View GitHub dashboard
# Check issue with 'conductor:status' label
```

## Metrics Tracked

- Active agents and their tasks
- Available task queue depth
- Completion rate and velocity
- System health indicators

## Health Monitoring

GitHub Actions run health checks every 15 minutes to:
- Monitor agent heartbeats
- Clean up stale worktrees
- Update status dashboard
- Process new tasks

## Status Dashboard

The system automatically maintains a GitHub Issue with the `conductor:status` label that shows:
- Currently active agents
- Tasks in progress
- Recent completions
- System health status

## Debugging

Use these commands to diagnose issues:

```bash
# View all conductor tasks
gh issue list -l 'conductor:task' --json state,assignees,title

# Check agent worktrees
ls -la worktrees/

# View recent activity
gh issue list -l 'conductor:task' --state all --limit 20
```