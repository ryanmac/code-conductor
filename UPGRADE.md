# Upgrading Code Conductor

This guide covers how to upgrade your Code Conductor installation to the latest version.

## Quick Upgrade

Run the same installation command you used initially:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/ryanmac/code-conductor/main/conductor-init.sh)
```

When prompted, choose option 1: **Upgrade**

## Upgrade Process Overview

### 1. Version Detection
The installer automatically detects:
- Your current Code Conductor version (from `VERSION` file)
- Whether an existing installation is present (`.conductor` directory)
- The latest available version from GitHub

### 2. Backup & Preservation
Before upgrading, the installer backs up:
- `.conductor/config.yaml` - Your project configuration
- `.conductor/CLAUDE.md` - Your AI agent instructions
- `CLAUDE.md` - Root-level AI instructions

### 3. Selective Update
Only these components are updated:
- `.conductor/scripts/` - Core conductor commands
- `.conductor/roles/` - Role definitions
- `.github/workflows/` - GitHub Actions
- `setup.py` - Setup script
- `requirements.txt` - Python dependencies
- `pyproject.toml` - Poetry configuration
- `VERSION` - Version tracking file

### 4. Configuration Restoration
After updating core files, your backed-up configurations are restored to their original locations.

## What's Preserved During Upgrade

✅ **Fully Preserved:**
- Your project configuration (`.conductor/config.yaml`)
- Custom AI instructions (`CLAUDE.md` files)
- All GitHub issues and tasks
- Git worktrees and branches
- Agent work in progress
- Task assignments and states

❌ **Not Preserved (Intentionally Updated):**
- Core scripts and commands
- Role definitions
- GitHub workflow files
- Python dependencies

## Manual Upgrade Steps

If you prefer to upgrade manually or need to customize the process:

### 1. Backup Your Configuration
```bash
cp .conductor/config.yaml .conductor/config.yaml.backup
cp .conductor/CLAUDE.md .conductor/CLAUDE.md.backup
cp CLAUDE.md CLAUDE.md.backup 2>/dev/null || true
```

### 2. Download Latest Version
```bash
curl -fsSL https://github.com/ryanmac/code-conductor/archive/main.tar.gz -o conductor-latest.tar.gz
tar -xzf conductor-latest.tar.gz
```

### 3. Update Core Files
```bash
# Update scripts
cp -r code-conductor-main/.conductor/scripts/* .conductor/scripts/

# Update roles
cp -r code-conductor-main/.conductor/roles/* .conductor/roles/

# Update workflows
cp -r code-conductor-main/.github/workflows/* .github/workflows/

# Update setup files
cp code-conductor-main/setup.py .
cp code-conductor-main/requirements.txt .
cp code-conductor-main/pyproject.toml .
cp code-conductor-main/VERSION .
```

### 4. Restore Configuration
```bash
cp .conductor/config.yaml.backup .conductor/config.yaml
cp .conductor/CLAUDE.md.backup .conductor/CLAUDE.md
cp CLAUDE.md.backup CLAUDE.md 2>/dev/null || true
```

### 5. Clean Up
```bash
rm -rf code-conductor-main conductor-latest.tar.gz
rm .conductor/*.backup CLAUDE.md.backup 2>/dev/null || true
```

## Version History

### v2.0.0 (Latest)
- Enhanced task listing with rich formatting and priority indicators
- Improved status command with health checks
- Better error handling and recovery mechanisms
- Automatic upgrade detection and seamless upgrade process
- Claude Code automation prompts

### v1.5.0
- Added conductor wrapper script for simplified commands
- Improved agent coordination with heartbeat monitoring
- Enhanced GitHub integration

### v1.0.0
- Initial release with core functionality
- GitHub Issues as tasks
- AI code review integration
- Multiple agent role support

## Troubleshooting Upgrades

### Issue: Upgrade Detection Not Working
**Solution:** Ensure you have a `VERSION` file in your project root. If missing:
```bash
echo "1.0.0" > VERSION  # Replace with your actual version
```

### Issue: Configuration Lost After Upgrade
**Solution:** The installer creates backups in `/tmp/conductor-backup-*`. To recover:
```bash
# Find backup directory
ls -la /tmp/conductor-backup-*

# Restore from backup
cp /tmp/conductor-backup-*/config.yaml .conductor/
```

### Issue: Scripts Not Working After Upgrade
**Solution:** Ensure executable permissions are set:
```bash
chmod +x .conductor/scripts/*
chmod +x conductor
```

### Issue: Python Dependencies Conflict
**Solution:** Recreate your virtual environment:
```bash
# If using venv
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# If using Poetry
poetry install
```

## Downgrading

If you need to downgrade to a previous version:

1. Note your current configuration
2. Remove the existing installation:
   ```bash
   rm -rf .conductor .github/workflows/conductor-*.yml
   ```
3. Install the specific version you want:
   ```bash
   # Replace VERSION with desired version tag
   curl -fsSL https://raw.githubusercontent.com/ryanmac/code-conductor/VERSION/conductor-init.sh | bash
   ```

## Getting Help

- **Documentation:** https://github.com/ryanmac/code-conductor
- **Issues:** https://github.com/ryanmac/code-conductor/issues
- **Community:** Join discussions in GitHub Issues

## Best Practices

1. **Always backup before upgrading** - While the installer does this automatically, having your own backup is recommended
2. **Test in a branch first** - Create a test branch to verify the upgrade works with your project
3. **Check the changelog** - Review what's new before upgrading to understand the changes
4. **Upgrade regularly** - Stay current to get bug fixes and new features
5. **Report issues** - If you encounter problems, please report them to help improve the upgrade process