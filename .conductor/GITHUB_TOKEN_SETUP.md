# CONDUCTOR_GITHUB_TOKEN Setup Guide

## Overview
Code Conductor requires a GitHub Personal Access Token (PAT) with specific permissions to manage issues, pull requests, and labels through GitHub Actions and the GitHub CLI.

## Required Token Permissions

Create a personal access token at https://github.com/settings/tokens with the following scopes:

### Essential Permissions
- **repo** (Full control of private repositories)
  - Needed for: Creating/updating issues, pull requests, labels
  - Includes: repo:status, repo_deployment, public_repo, repo:invite

### Optional but Recommended
- **workflow** 
  - Needed if: You want to trigger or modify GitHub Actions workflows
- **write:discussion**
  - Needed if: Your project uses GitHub Discussions
- **admin:org** 
  - Needed if: Managing organization-level resources

## Creating the Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a descriptive name like "Code Conductor Bot"
4. Select the required scopes:
   - ✅ repo (all sub-permissions)
   - ✅ workflow (if using Actions)
5. Set an expiration (recommend 90 days with calendar reminder to renew)
6. Click "Generate token"
7. Copy the token immediately (you won't see it again!)

## Adding Token to Repository

1. Go to your repository's Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `CONDUCTOR_GITHUB_TOKEN`
4. Value: Paste your token
5. Click "Add secret"

## Verifying Token Setup

Run this command to verify your token has the correct permissions:
```bash
export GITHUB_TOKEN="your-token-here"
gh auth status
gh api user
```

You should see your username and no permission errors.

## Token Security Best Practices

1. **Never commit tokens** to your repository
2. **Rotate regularly** - Set calendar reminders to regenerate every 90 days
3. **Use least privilege** - Only grant permissions you actually need
4. **Monitor usage** - Check Settings → Personal access tokens for last used dates
5. **Revoke if compromised** - Immediately revoke and regenerate if exposed

## Troubleshooting

### "Bad credentials" or "401 Unauthorized"
- Token may be expired or revoked
- Regenerate token and update secret

### "Resource not accessible by integration"  
- Token missing required permissions
- Check token has `repo` scope

### "API rate limit exceeded"
- Token may not have sufficient rate limits
- Authenticated requests get 5,000/hour vs 60/hour unauthenticated

## Environment Variable Mapping

The conductor scripts automatically handle these token environment variables:
- `CONDUCTOR_GITHUB_TOKEN` → Preferred, set in GitHub Actions secrets
- `GITHUB_TOKEN` → Mapped to `GH_TOKEN` for GitHub CLI
- `GH_TOKEN` → Used directly by GitHub CLI

This ensures compatibility across different environments and tools.