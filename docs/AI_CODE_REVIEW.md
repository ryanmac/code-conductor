# AI Code Review - Smart, Opt-In Quality Gates

Request AI code reviews when you need them - no more review spam for trivial changes:

- 🎯 **Opt-in reviews** - Add `needs-review` label or comment `/conductor review` to request
- 🔒 **Security scanning** - Agents check for hardcoded secrets, SQL injection risks, unsafe operations
- 🐛 **Bug detection** - Comprehensive analysis for null references, race conditions, logic errors
- 💡 **Smart filtering** - Automatically skips docs-only changes, tiny PRs, and bot updates
- 🧪 **Test coverage** - Suggests missing tests and edge cases

## How It Works

1. **Request a review** - Add `needs-review` label or comment `/conductor review` on your PR
2. **Smart filtering** - System checks if review is needed (skips trivial changes)
3. **Task creation** - Review task appears as GitHub Issue (only if needed)
4. **Agent review** - AI agents claim and complete thorough code review
5. **PR feedback** - Detailed review posted as PR comment

## Automatic Skip Conditions
- PRs with less than 10 lines changed
- Documentation-only changes
- Dependabot and bot PRs
- PRs labeled with `skip-review`
- Draft PRs

## Triggering Reviews
```bash
# Option 1: Add label
gh pr edit 123 --add-label needs-review

# Option 2: Comment on PR
@conductor review  # or /conductor review

# Option 3: Manual workflow
gh workflow run pr-review-tasks.yml -f pr_number=123
```