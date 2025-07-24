# GitHub Token Setup Guide

## Token Strategy Overview

Code Conductor uses different token strategies depending on the context:

### 1. For Projects Using Code Conductor (Most Users)
When you install Code Conductor in your project:
- **Default**: Uses GitHub Actions' built-in `${{ github.token }}`
- **No setup required** - Works out of the box!
- **Limitations**: Can't trigger other workflows, rate limited
- **Optional upgrade**: Create a PAT for enhanced features (see below)

### 2. For Code Conductor Development (Maintainers Only)
The ryanmac/code-conductor repository itself uses:
- **Token name**: `CONDUCTOR_GITHUB_TOKEN`
- **Type**: Personal Access Token with enhanced permissions
- **Purpose**: Managing Code Conductor's own development

## For Most Users: No Token Setup Required!

When you install Code Conductor in your project using:
```bash
bash <(curl -fsSL https://raw.githubusercontent.com/ryanmac/code-conductor/main/conductor-init.sh)
```

The generated workflows will use GitHub's built-in token, which provides:
- ✅ Read/write access to issues, pull requests, and code
- ✅ Ability to create labels and manage project boards
- ✅ 1,000 API requests per hour per repository

## Optional: Creating a Personal Access Token

You only need a PAT if you want:
- Higher API rate limits (5,000/hour instead of 1,000/hour)
- Ability to trigger other workflows
- Cross-repository access
- Access to private repositories

### How to Create a PAT

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a descriptive name like "Code Conductor Bot"
4. Select the required scopes:
   - ✅ repo (all sub-permissions)
   - ✅ workflow (if triggering other workflows)
5. Set expiration (90 days recommended)
6. Click "Generate token" and copy it

### Adding Your PAT to Your Project

1. Go to your repository's Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `CONDUCTOR_GITHUB_TOKEN` (or any name you prefer)
4. Value: Paste your token
5. Click "Add secret"

### Using Your PAT in Workflows

Update the workflows in `.github/workflows/` to use your token:
```yaml
env:
  GH_TOKEN: ${{ secrets.CONDUCTOR_GITHUB_TOKEN }}
```

## Token Security Best Practices

1. **Use built-in token when possible** - Simpler and more secure
2. **Never commit tokens** - Always use secrets
3. **Rotate PATs regularly** - Set calendar reminders
4. **Use least privilege** - Only grant needed permissions
5. **Revoke if compromised** - Act immediately

## Troubleshooting

### "Bad credentials" or "401 Unauthorized"
- Using built-in token: Check workflow permissions in Settings → Actions
- Using PAT: Token may be expired, regenerate and update secret

### "Resource not accessible by integration"  
- Built-in token has limited permissions
- Consider creating a PAT with `repo` scope

### "API rate limit exceeded"
- Built-in token: 1,000 requests/hour limit hit
- Solution: Create a PAT for 5,000 requests/hour

## For Code Conductor Maintainers

If you're contributing to the Code Conductor project itself:
- This repository uses `CONDUCTOR_GITHUB_TOKEN`
- It's a PAT with enhanced permissions for managing development
- Regular users don't need to worry about this!

## Summary

- **Most users**: No token setup needed, built-in token works great
- **Power users**: Create a PAT for enhanced features
- **Maintainers**: Use CONDUCTOR_GITHUB_TOKEN for development

The scripts work with any token setup - they use whatever environment they're given!