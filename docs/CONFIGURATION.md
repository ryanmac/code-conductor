# Configuration Guide

## Project Configuration

The main configuration file is `.conductor/config.yaml`, created during setup.

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

## Setup Options

Run `python setup.py` to configure:

- Project name and documentation location
- Technology stack detection
- Role selection (hybrid model)
- Task management approach
- GitHub integration settings

## Role Definitions

Each role has a Markdown file in `.conductor/roles/` defining:

- Responsibilities
- Task selection criteria
- Required skills
- Success metrics

## Environment Variables

- `AGENT_ROLE` - Set the default agent role
- `CONDUCTOR_DEBUG` - Enable debug logging
- `WORKTREE_BASE` - Override default worktree location