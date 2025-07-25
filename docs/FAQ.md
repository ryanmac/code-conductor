# Frequently Asked Questions

## Do I need to set up a CONDUCTOR_GITHUB_TOKEN?

**No!** Code Conductor uses GitHub's built-in authentication (`${{ github.token }}`) for all workflows. This token is automatically available in GitHub Actions with no setup required.

You only need a Personal Access Token (PAT) if you want:
- Higher API rate limits (5,000/hour vs 1,000/hour)
- Cross-repository access
- Ability to trigger other workflows

For detailed token information, see [.conductor/GITHUB_TOKEN_SETUP.md](.conductor/GITHUB_TOKEN_SETUP.md).

## Why does Code Conductor require Python?

Python is required **only for the conductor orchestration scripts**, not for your project's CI/CD. Here's what this means:

- ✅ **Required**: Python 3.9-3.12 to run conductor commands
- ❌ **NOT added**: Python test runners (pytest)
- ❌ **NOT added**: Python linters (flake8, black)
- ❌ **NOT added**: Python security scanners (safety)
- ❌ **NOT added**: Any Python-specific CI/CD workflows

Your project's existing CI/CD remains unchanged. Code Conductor only adds three language-agnostic GitHub workflows for task orchestration.

## Does Code Conductor add Python CI/CD to my JavaScript/TypeScript/Go project?

**No!** Code Conductor is language-agnostic. It detects your project's technology stack and configures roles accordingly, but it does NOT add language-specific CI/CD workflows.

The only workflows added are:
1. `conductor.yml` - Task orchestration and health checks
2. `conductor-cleanup.yml` - Stale worktree cleanup
3. `pr-review.yml` - AI code reviews (if enabled)

These workflows only run conductor scripts and do not test, lint, or build your code.

## What if I see Python test failures in my CI?

If you're seeing Python test failures like:
```
============================= test session starts ==============================
collected 0 items
============================ no tests ran in 0.02s =============================
Error: Process completed with exit code 5.
```

This is NOT from Code Conductor. Check if:
1. You accidentally copied CI workflows from the Code Conductor repository itself
2. You have existing Python CI workflows in your project
3. Another tool added Python-specific workflows

Code Conductor's template workflows do not include any Python testing commands.

## Can I use Code Conductor without installing Python?

Currently, Python is required because the conductor scripts are written in Python. We chose Python for:
- Maximum compatibility across all platforms
- Easy installation via standard package managers
- Reliable YAML and JSON processing
- Strong GitHub API support

Future versions may offer alternative implementations, but Python remains the most universal choice.

## Do I need to manage Python dependencies for my non-Python project?

No, the Python dependencies are isolated to Code Conductor's functionality:
- `pyyaml` - For configuration file handling
- Standard library modules only

These are only used by conductor scripts and do not affect your project's dependencies.

## How do I know which workflows were added by Code Conductor?

Code Conductor only adds workflows from its templates:
- `.github/workflows/conductor.yml`
- `.github/workflows/conductor-cleanup.yml`
- `.github/workflows/pr-review.yml` (if code-reviewer role is enabled)

Any other workflows (especially those running pytest, flake8, etc.) are from other sources.

## Can I remove the Python dependency from Code Conductor?

The conductor scripts require Python to run. However, you can:
1. Run agents from the Conductor app (macOS) which handles Python internally
2. Use containerized environments where Python is pre-installed
3. Install Python in your CI environment only (not locally)

The Python requirement is minimal and doesn't affect your project's runtime or deployment.