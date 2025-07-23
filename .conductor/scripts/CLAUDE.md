# CLAUDE.md: Instructions for Claude Code - Automation Scripts

## Purpose
This directory contains Python and Bash scripts that power the Code-Conductor orchestration system. These scripts handle task management, agent coordination, health monitoring, and GitHub integration. Claude Code should understand their safe usage and guide modifications that maintain system integrity.

## Guidelines
- **Do**: Read scripts thoroughly before suggesting modifications
- **Do**: Test script changes in isolated environments first
- **Do**: Maintain atomic operations for state management
- **Do**: Preserve error handling and logging patterns
- **Don't**: Modify scripts that alter `workflow-state.json` without understanding locking
- **Don't**: Remove safety checks or validation steps
- **Don't**: Execute scripts without understanding their side effects

## Critical Scripts Overview

### State Management (Handle with Care)
- `task-claim.py` - Atomic task assignment with file locking
- `update-status.py` - Updates system status safely
- `cleanup-stale.py` - Removes abandoned work (has --dry-run option)
- `archive-completed.py` - Moves completed tasks to archive

### Agent Lifecycle
- `bootstrap.sh` - Universal agent initialization (safe to run)
- `health-check.py` - Read-only system health monitoring
- `cleanup-worktrees.py` - Removes old git worktrees

### Integration Scripts
- `issue-to-task.py` - Converts GitHub issues to tasks
- `code-reviewer.py` - AI-powered PR reviews
- `generate-summary.py` - Creates status reports

### Validation Scripts (Always Safe)
- `validate-config.py` - Checks configuration validity
- `dependency-check.py` - Verifies system requirements

## Autonomous Script Execution Decision Tree

```
Need to run a script?
├─ Identify script category
│   ├─ Read-only (health-check, validate-config) → Always safe to run
│   ├─ State-modifying (task-claim, update-status) → Check locks first
│   └─ Destructive (cleanup-*, archive-*) → Run with --dry-run first
├─ Pre-execution validation
│   ├─ Run dependency-check.py → All pass? Continue
│   ├─ Check workflow-state.json lock → Available? Continue
│   └─ Verify git status clean → Clean? Continue
└─ Execute with automatic fallbacks
    ├─ Success → Continue workflow
    ├─ Lock conflict → Retry with backoff (3x, 5s intervals)
    └─ Other error → Log and try alternative approach
```

## Step-by-Step Usage

### 1. Observe - Understanding Script Purpose
Automated script analysis:
```python
# Auto-classification logic
def classify_script(script_path):
    content = read_file(script_path)
    if "workflow-state.json" in content and "write" in content:
        return "state-modifying"
    elif any(word in content for word in ["remove", "delete", "cleanup"]):
        return "destructive"
    else:
        return "read-only"
```

### 2. Plan - Safe Execution Strategy
Automatic safety checks:
- State-modifying scripts: Acquire lock with timeout
- Destructive scripts: Always run --dry-run first
- Permission errors: Fallback to alternative methods
- Lock conflicts: Implement exponential backoff

### 3. Act - Execute with Safeguards
```bash
# For Python scripts - always in virtual environment
python .conductor/scripts/script-name.py --help

# For state-modifying scripts - use dry-run first
python .conductor/scripts/cleanup-stale.py --dry-run

# For bash scripts - check syntax first
bash -n .conductor/scripts/bootstrap.sh
```

### 4. Evaluate - Verify Results
After execution:
- Check `workflow-state.json` for unexpected changes
- Verify no files were accidentally deleted
- Ensure other agents aren't blocked
- Review any error messages

## Examples

### Example 1: Safely Running Health Check
**Prompt**: "Check the health of the conductor system"

**Safe approach**:
```bash
# This is read-only, always safe
python .conductor/scripts/health-check.py

# For detailed output
python .conductor/scripts/health-check.py --verbose
```

### Example 2: Claiming a Task
**Scenario**: Need to claim next available task

**Autonomous approach**:
```python
# Automated task claiming with retry logic
def claim_task_safely(role="dev", max_retries=3):
    for attempt in range(max_retries):
        try:
            # Check available tasks first
            result = run_script("generate-summary.py")
            if not result["available_tasks"]:
                return {"status": "no_tasks_available"}
            
            # Attempt claim
            claim_result = run_script(f"task-claim.py --role {role}")
            if claim_result["status"] == "success":
                return claim_result
                
        except LockError:
            time.sleep(5 * (attempt + 1))  # Exponential backoff
            
    return {"status": "failed_after_retries"}
```

### Example 3: Cleaning Stale Work
**Prompt**: "Clean up abandoned agent work"

**Safe approach**:
```bash
# ALWAYS use dry-run first
python .conductor/scripts/cleanup-stale.py --dry-run

# Review what would be cleaned
# If safe, proceed without dry-run
python .conductor/scripts/cleanup-stale.py --timeout 3600
```

### Example 4: Modifying a Script
**Prompt**: "Add logging to task-claim.py"

**Safe approach**:
1. Copy the original: `cp task-claim.py task-claim-modified.py`
2. Make changes to the copy
3. Test thoroughly with mock state file
4. Only replace original after verification

## Script Modification Guidelines

When creating or modifying scripts:

### State Management Scripts
```python
# Always use file locking for state changes
import fcntl
with open(state_file, 'r+') as f:
    fcntl.flock(f, fcntl.LOCK_EX)
    state = json.load(f)
    # Make changes
    f.seek(0)
    json.dump(state, f, indent=2)
    f.truncate()
```

### Error Handling Pattern
```python
try:
    # Operation
except SpecificException as e:
    print(f'{{"status": "ERROR", "message": "{e}"}}')
    sys.exit(1)
```

### Logging Pattern
```python
# Use JSON for structured output
result = {
    "status": "SUCCESS",
    "timestamp": datetime.utcnow().isoformat(),
    "details": {...}
}
print(json.dumps(result))
```

## Warnings

### Critical Safety Rules
1. **State Corruption**: Never write to `workflow-state.json` without proper locking
2. **Race Conditions**: Always use atomic operations for multi-agent scenarios
3. **Destructive Operations**: Scripts like `cleanup-*.py` can delete work - use dry-run
4. **Permission Issues**: Some scripts need git/gh auth - check dependencies first
5. **Path Traversal**: Never use user input directly in file paths

### Common Pitfalls
- Forgetting to handle the case where state file is locked by another process
- Not preserving the exact JSON structure when modifying state
- Breaking GitHub Actions by changing script output format
- Removing validation that prevents conflicting task assignments

## Testing New Scripts

Template for safe script development:
```bash
# 1. Create test environment
mkdir -p /tmp/conductor-test
cp -r .conductor /tmp/conductor-test/
cd /tmp/conductor-test

# 2. Create mock state
echo '{"available_tasks": [], "active_work": {}}' > .conductor/workflow-state.json

# 3. Test your script
python .conductor/scripts/your-new-script.py

# 4. Verify state integrity
python .conductor/scripts/validate-config.py
```

## Common Error Patterns and Recovery

### Error Handling Matrix
```python
ERROR_HANDLERS = {
    "FileNotFoundError": lambda e: {
        "workflow-state.json": "Run setup.py to initialize",
        "config.yaml": "Run setup.py to create configuration",
        "role file": "Use default 'dev' role or create missing role"
    },
    "LockError": lambda e: {
        "retry_strategy": "exponential_backoff",
        "max_retries": 3,
        "fallback": "Report task as blocked, work on different task"
    },
    "PermissionError": lambda e: {
        "git": "Check git credentials with 'gh auth status'",
        "file": "Check file permissions, use sudo if authorized",
        "fallback": "Skip and document in task notes"
    },
    "JSONDecodeError": lambda e: {
        "action": "Restore from backup or reinitialize",
        "prevention": "Always use atomic writes with proper locking"
    }
}

def handle_script_error(error, context):
    handler = ERROR_HANDLERS.get(type(error).__name__, 
                                lambda e: {"action": "log and continue"})
    return handler(error)
```

### Self-Validation Checklist
After any script execution:
```python
def validate_script_execution(script_name, result):
    checks = {
        "task-claim.py": lambda r: "task_id" in r and "worktree_path" in r,
        "cleanup-stale.py": lambda r: "cleaned" in r and isinstance(r["cleaned"], list),
        "health-check.py": lambda r: "status" in r and r["status"] in ["healthy", "warning", "error"],
        "update-status.py": lambda r: "updated" in r and r["updated"] == True
    }
    
    validator = checks.get(script_name, lambda r: "status" in r)
    return validator(result)
```

## References
- `workflow-state.json` - Central state file (handle with extreme care)
- `../config.yaml` - Project configuration
- `bootstrap.sh` - Best example of safe script patterns
- GitHub Actions workflows - See how scripts are used in automation
- Python `fcntl` docs - For file locking patterns

Last Updated: 2025-07-23
Version: 1.1