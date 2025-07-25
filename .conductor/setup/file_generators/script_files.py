"""
Script Files Generator
Generates bootstrap scripts and the universal conductor command
"""

import os
from pathlib import Path
from typing import Dict, Any


class ScriptFileGenerator:
    """Generates executable scripts for Code Conductor"""

    def __init__(self, project_root: Path, config: Dict[str, Any]):
        self.project_root = project_root
        self.conductor_dir = project_root / ".conductor"
        self.config = config

    def create_bootstrap_scripts(self):
        """Create bootstrap and utility scripts"""
        print("\n⚡ Creating bootstrap scripts...")

        scripts_dir = self.conductor_dir / "scripts"
        scripts_dir.mkdir(exist_ok=True)

        # Create bootstrap script
        self._create_bootstrap_script(scripts_dir)

        # Create task-claim script
        self._create_task_claim_script(scripts_dir)

        # Create universal conductor command
        self._create_conductor_command(scripts_dir)

        # Create project-root wrapper
        self._create_conductor_shortcut()

    def _create_bootstrap_script(self, scripts_dir: Path):
        """Create the bootstrap.sh script"""
        bootstrap_content = """#!/bin/bash
set -e

# Universal Agent Bootstrap Script
echo "🤖 Initializing Conductor Agent..."

# Load configuration
CONFIG_FILE=".conductor/config.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Configuration not found. Run 'python setup.py' first."
    exit 1
fi

# Determine agent role
AGENT_ROLE=${AGENT_ROLE:-$(python3 -c \\
    "import sys; print(sys.argv[1] if len(sys.argv) > 1 else 'unknown')" $1)}
if [ "$AGENT_ROLE" = "unknown" ]; then
    echo "🔍 Agent role not specified. Available roles:"
    ls .conductor/roles/ | sed 's/.md$//' | sed 's/^/  - /'
    read -p "Enter your role: " AGENT_ROLE
fi

echo "👤 Agent Role: $AGENT_ROLE"

# Sync repository state
echo "🔄 Syncing repository state..."
git fetch origin
git pull origin main || true

# Load role-specific instructions
ROLE_FILE=".conductor/roles/${AGENT_ROLE}.md"
if [ ! -f "$ROLE_FILE" ]; then
    echo "❌ Role definition not found: $ROLE_FILE"
    exit 1
fi

echo "📖 Loaded role definition: $AGENT_ROLE"

# Check system dependencies
echo "🔍 Checking dependencies..."
python3 .conductor/scripts/dependency-check.py

# Attempt to claim a task
echo "🎯 Looking for available tasks..."
TASK_RESULT=$(python3 .conductor/scripts/task-claim.py --role "$AGENT_ROLE")

if echo "$TASK_RESULT" | grep -q "IDLE"; then
    echo "😴 No tasks available. Agent is idle."
    echo "💡 Check back later or create new tasks via GitHub issues."
    exit 0
fi

# Task claimed successfully
echo "✅ Task claimed successfully!"
echo "$TASK_RESULT" | python3 -m json.tool

# Create git worktree for isolated work
TASK_ID=$(echo "$TASK_RESULT" | python3 -c \\
    "import json, sys; data=json.load(sys.stdin); print(data['task_id'])")
BRANCH_NAME="agent-$AGENT_ROLE-$TASK_ID"
WORKTREE_PATH="./worktrees/$BRANCH_NAME"

echo "🌳 Creating git worktree: $WORKTREE_PATH"
git worktree add "$WORKTREE_PATH" -b "$BRANCH_NAME"

# Display next steps
echo ""
echo "🚀 Agent initialization complete!"
echo "📂 Your isolated workspace: $WORKTREE_PATH"
echo ""
echo "Next steps:"
echo "1. cd $WORKTREE_PATH"
echo "2. Review your task details in the output above"
echo "3. Implement according to specifications"
echo "4. Commit and push your changes"
echo "5. Create a pull request when ready"
"""

        bootstrap_file = scripts_dir / "bootstrap.sh"
        with open(bootstrap_file, "w") as f:
            f.write(bootstrap_content)
        os.chmod(bootstrap_file, 0o755)
        print(f"✓ Created {bootstrap_file}")

    def _create_task_claim_script(self, scripts_dir: Path):
        """Create the task-claim.py script"""
        task_claim_content = '''#!/usr/bin/env python3
"""Task claiming script for atomic task assignment"""

import json
import sys
import fcntl
import argparse
from datetime import datetime
from pathlib import Path


class TaskClaimer:
    def __init__(self, role):
        self.role = role
        self.state_file = Path(".conductor/state.json")

    def claim_task(self):
        """Atomically claim an available task using GitHub Issues"""
        # Ensure file exists
        if not self.state_file.exists():
            return {"status": "ERROR", "message": "State file not found"}

        with open(self.state_file, "r+") as f:
            # Exclusive lock for atomic operations
            fcntl.flock(f, fcntl.LOCK_EX)

            try:
                state = json.load(f)
            except json.JSONDecodeError:
                return {"status": "ERROR", "message": "Invalid state file"}

            claimed_task = None

            # Find suitable task
            for i, task in enumerate(state.get("available_tasks", [])):
                # Check skill requirements
                required_skills = task.get("required_skills", [])

                # Hybrid logic: empty skills = any dev, otherwise need match
                if not required_skills or self.role in required_skills:
                    # Check no file conflicts
                    if not self._has_file_conflicts(task, state):
                        claimed_task = task
                        state["available_tasks"].pop(i)
                        break

            if claimed_task:
                # Create agent ID
                agent_id = f"{self.role}_{int(datetime.utcnow().timestamp())}"

                # Move to active work
                if "active_work" not in state:
                    state["active_work"] = {}

                state["active_work"][agent_id] = {
                    "task": claimed_task,
                    "status": "in_progress",
                    "started_at": datetime.utcnow().isoformat(),
                    "heartbeat": datetime.utcnow().isoformat(),
                    "files_locked": claimed_task.get("files_locked", []),
                }

                # Update agent counts
                if "system_status" not in state:
                    state["system_status"] = {}
                state["system_status"]["active_agents"] = len(state["active_work"])
                state["system_status"]["last_updated"] = datetime.utcnow().isoformat()

                # Write back atomically
                f.seek(0)
                json.dump(state, f, indent=2)
                f.truncate()

                # Release lock
                fcntl.flock(f, fcntl.LOCK_UN)

                # Return success with task details
                return {
                    "status": "claimed",
                    "task_id": claimed_task["id"],
                    "task": claimed_task,
                    "agent_id": agent_id,
                }
            else:
                # Release lock
                fcntl.flock(f, fcntl.LOCK_UN)
                return {"status": "IDLE", "reason": "No suitable tasks available"}

    def _has_file_conflicts(self, task, state):
        """Check if task files conflict with active work"""
        task_files = set(task.get("files_locked", []))
        if not task_files:
            return False

        for agent_work in state.get("active_work", {}).values():
            locked_files = set(agent_work.get("files_locked", []))
            if task_files & locked_files:  # Intersection = conflict
                return True

        return False


def main():
    parser = argparse.ArgumentParser(description="Claim a task for agent work")
    parser.add_argument("--role", default="dev", help="Agent role (default: dev)")
    args = parser.parse_args()

    claimer = TaskClaimer(args.role)
    result = claimer.claim_task()

    # Output result as JSON
    print(json.dumps(result))

    # Exit with appropriate code
    sys.exit(0 if result["status"] in ["claimed", "IDLE"] else 1)


if __name__ == "__main__":
    main()
'''

        task_claim_file = scripts_dir / "task-claim.py"
        with open(task_claim_file, "w") as f:
            f.write(task_claim_content)
        os.chmod(task_claim_file, 0o755)
        print(f"✓ Created {task_claim_file}")

    def _create_conductor_command(self, scripts_dir: Path):
        """Create the universal conductor command - split into a separate file"""
        # Due to size constraints, the conductor command will be imported from
        # a dedicated conductor_command.py file
        from .conductor_command import CONDUCTOR_COMMAND_CONTENT

        conductor_file = scripts_dir / "conductor"
        with open(conductor_file, "w") as f:
            f.write(CONDUCTOR_COMMAND_CONTENT)
        os.chmod(conductor_file, 0o755)
        print(f"✓ Created {conductor_file}")

    def _create_conductor_shortcut(self):
        """Create easy-to-find shortcut in project root"""
        wrapper_content = """#!/bin/bash
# Conductor command wrapper - project-specific
exec .conductor/scripts/conductor "$@"
"""

        wrapper_path = self.project_root / "conductor"
        with open(wrapper_path, "w") as f:
            f.write(wrapper_content)
        os.chmod(wrapper_path, 0o755)
        print("✓ Created ./conductor shortcut command")
