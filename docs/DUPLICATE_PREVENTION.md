# Duplicate Issue Prevention Guide

This guide helps AI agents and developers avoid creating duplicate GitHub issues in Code Conductor projects.

## Why Duplicate Prevention Matters

- **Reduces confusion**: Multiple issues for the same work confuses agents
- **Saves time**: Prevents wasted effort on already-solved problems
- **Cleaner project**: Maintains organized, searchable issue tracking
- **Better coordination**: Agents can find and collaborate on existing work

## Before Creating Any Issue

### 1. Use the Duplicate Checker Tool

```bash
# Check if your issue already exists
./conductor check-dup "Your proposed issue title"

# Examples:
./conductor check-dup "Add user authentication"
./conductor check-dup "Improve error handling"
./conductor check-dup "Create API documentation"
```

### 2. Manual Search Commands

```bash
# Search all issues by keywords
gh issue list --search "keyword1 OR keyword2" --state all

# Search conductor tasks specifically
gh issue list --label "conductor:task" --state all --limit 100

# Search closed issues
gh issue list --label "conductor:task" --state closed --limit 50

# Search by multiple terms
gh issue list --search "auth login user session" --state all
```

### 3. Check Common Duplicate Patterns

Before creating issues for common tasks, always search for these terms:

- **Authentication**: `auth`, `login`, `user`, `session`, `jwt`, `oauth`
- **Testing**: `test`, `testing`, `coverage`, `unit`, `integration`, `e2e`
- **Documentation**: `docs`, `documentation`, `readme`, `api docs`, `guide`
- **Error Handling**: `error`, `exception`, `handling`, `logging`, `debug`
- **Performance**: `performance`, `optimization`, `speed`, `cache`, `slow`
- **Security**: `security`, `vulnerability`, `xss`, `csrf`, `injection`
- **CI/CD**: `ci`, `cd`, `pipeline`, `github actions`, `deploy`, `build`

## Smart Issue Creation Process

### Step 1: Define Your Task Clearly

Before searching, clearly define:
- What functionality you want to add/fix
- What component/area it affects
- What the end result should be

### Step 2: Search Multiple Ways

```bash
# Search by exact title
gh issue list --search "Add user authentication" --state all

# Search by component
gh issue list --search "auth component" --state all

# Search by feature area
gh issue list --search "in:title,body authentication" --state all
```

### Step 3: Analyze Similar Issues

If you find similar issues:

1. **Exact match**: Don't create a new issue. Work on the existing one.
2. **Partial match**: Check if your task is a subtask of a larger issue.
3. **Related but different**: Create your issue but reference the related ones.

### Step 4: Create With Context

If no duplicates exist:

```bash
# Create with clear title and labels
gh issue create \
  --title "Clear, specific title" \
  --label "conductor:task,effort:medium,priority:high" \
  --body "## Description
Detailed description here...

## Related Issues
- References #123 (if related but not duplicate)

## Why This Is Unique
Explain why this isn't covered by existing issues"
```

## AI Agent-Specific Guidelines

### For AI Agents Creating Tasks

1. **Always run duplicate check first**:
   ```python
   # In your task generation logic
   def create_task(title, body):
       # First, check for duplicates
       similar = check_duplicates(title)
       if similar:
           print(f"Similar issue exists: #{similar['number']}")
           return None
       
       # Only create if unique
       return create_issue(title, body)
   ```

2. **Use semantic similarity**:
   - "Add user auth" ≈ "Implement authentication" ≈ "Create login system"
   - Check for conceptual overlap, not just exact matches

3. **Check task scope**:
   - Is this task part of a larger epic?
   - Could it be a subtask instead of a new issue?

### For [INIT] Task Execution

When generating tasks from documentation mapping:

1. **Batch duplicate checking**:
   ```bash
   # Before creating multiple tasks
   for task in proposed_tasks; do
     ./conductor check-dup "$task"
   done
   ```

2. **Group related work**:
   - Instead of: "Add login", "Add logout", "Add password reset"
   - Create: "Implement complete authentication system"

3. **Reference existing issues**:
   - If your task list includes items that exist, note them
   - Mark them as "Already exists: #123"

### AI Agent Todo List Management

**CRITICAL**: Maintain clean internal todo lists to prevent duplicate work:

1. **Todo List Hygiene**:
   - Before adding a new todo, scan your existing list for similar items
   - Consolidate related todos into single comprehensive tasks
   - Mark todos as completed immediately upon finishing work
   - Remove todos that reference closed or obsolete GitHub issues

2. **Example of Good Todo Management**:
   ```
   ❌ BAD (Duplicate todos):
   - Add user login page
   - Implement authentication
   - Create login functionality  
   - Add JWT tokens
   - Build password reset
   
   ✅ GOOD (Consolidated):
   - Implement complete auth system (login, JWT, password reset)
   ```

3. **Sync with GitHub Issues**:
   - Each todo should correspond to a unique GitHub issue
   - If you find duplicate todos, check if duplicate issues exist
   - Clean up both internal todos and external issues

4. **Regular Cleanup**:
   - At the start of each session, review and clean your todo list
   - Remove completed items
   - Consolidate similar tasks
   - Ensure alignment with current GitHub issues

## Common Anti-Patterns to Avoid

### ❌ Don't Do This:

1. **Creating without searching**:
   ```bash
   # BAD: Direct creation
   gh issue create --title "Add tests"
   ```

2. **Overly generic titles**:
   - "Fix bugs"
   - "Improve performance"
   - "Add features"

3. **Duplicating with slight variations**:
   - Issue #1: "Add user login"
   - Issue #2: "Implement user authentication"
   - Issue #3: "Create login functionality"

### ✅ Do This Instead:

1. **Search first, create second**:
   ```bash
   # GOOD: Check first
   ./conductor check-dup "Add test coverage for auth module"
   # If no duplicates found, then create
   ```

2. **Specific, searchable titles**:
   - "Add JWT authentication to REST API"
   - "Improve database query performance in user.list()"
   - "Add unit tests for payment processing module"

3. **Link related issues**:
   ```markdown
   Related to #45 but specifically addresses the OAuth2 flow
   which wasn't covered in the original issue.
   ```

## Duplicate Detection Algorithm

The `check-duplicate-issues.py` script uses:

1. **Title similarity**: 70% weight
   - Uses sequence matching for fuzzy comparison
   - Case-insensitive matching

2. **Keyword overlap**: 30% weight
   - Extracts meaningful keywords
   - Ignores common stop words
   - Measures intersection of keyword sets

3. **Similarity threshold**: 60% default
   - Issues with >80% similarity: Very likely duplicates
   - Issues with 60-80% similarity: Possibly related
   - Issues with <60% similarity: Probably unique

## Quick Reference Card

```bash
# Before creating any issue:
./conductor check-dup "Your title here"

# If you must search manually:
gh issue list --search "keywords" --state all

# When in doubt:
# - Search broader terms
# - Check closed issues too
# - Ask in existing related issues
```

## Integration with Workflow

### In CLAUDE.md

All agents are instructed to check for duplicates before creating issues.
See the "Creating New Tasks - IMPORTANT Duplicate Prevention" section.

### In Conductor Script

The demo task creation now checks for existing similar tasks before creating new ones.

### In Your Workflow

1. Think of issue title
2. Run `./conductor check-dup "title"`
3. Review results
4. Only create if truly unique

## Reporting Duplicate Issues

If you find duplicates after they're created:

1. Comment on both issues noting the duplication
2. Close the newer issue with a reference to the older one
3. Transfer any unique information to the surviving issue

```bash
# Close duplicate
gh issue close 123 --comment "Duplicate of #45. Transferring unique details there."
```