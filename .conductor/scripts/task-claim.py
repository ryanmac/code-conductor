#!/usr/bin/env python3
"""Claim and assign tasks to agents using GitHub Issues"""

import json
import os
import sys
import uuid
import argparse
import subprocess
from datetime import datetime


def run_gh_command(args):
    """Run GitHub CLI command and return output"""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f'{{"status": "ERROR", "message": "GitHub CLI error: {e.stderr}"}}')
        sys.exit(1)
    except FileNotFoundError:
        print('{"status": "ERROR", "message": "GitHub CLI (gh) not found. Please install it."}')
        sys.exit(1)


def get_available_tasks():
    """Get available tasks from GitHub Issues"""
    # Query open issues with conductor:task label that are not assigned
    output = run_gh_command([
        "issue", "list",
        "-l", "conductor:task",
        "--state", "open",
        "--json", "number,title,body,labels,assignees,createdAt",
        "--jq", '.[] | select(.assignees | length == 0)'
    ])
    
    if not output:
        return []
    
    # Parse tasks from JSON lines
    tasks = []
    for line in output.strip().split('\n'):
        if line:
            try:
                issue = json.loads(line)
                # Convert issue to task format
                task = {
                    "id": str(issue["number"]),
                    "title": issue["title"],
                    "description": issue["body"] or "",
                    "created_at": issue["createdAt"],
                    "required_skills": [],
                    "estimated_effort": "medium",
                    "priority": "medium"
                }
                
                # Extract metadata from labels
                for label in issue["labels"]:
                    name = label["name"]
                    if name.startswith("skill:"):
                        task["required_skills"].append(name.replace("skill:", ""))
                    elif name.startswith("effort:"):
                        task["estimated_effort"] = name.replace("effort:", "")
                    elif name.startswith("priority:"):
                        task["priority"] = name.replace("priority:", "")
                
                tasks.append(task)
            except json.JSONDecodeError:
                continue
    
    return tasks


def find_suitable_task(tasks, role):
    """Find a task suitable for the given role"""
    if not tasks:
        return None

    # Try to find tasks that match the role's skills
    role_tasks = []
    general_tasks = []

    for task in tasks:
        required_skills = task.get("required_skills", [])

        # If no specific skills required, it's a general task
        if not required_skills:
            general_tasks.append(task)
        # If role matches required skills
        elif role in required_skills:
            role_tasks.append(task)
        # Special mapping for common roles
        elif role == "dev" and not required_skills:
            general_tasks.append(task)

    # Prefer tasks that specifically need this role
    if role_tasks:
        # Sort by effort (small tasks first) and priority
        effort_order = {"small": 1, "medium": 2, "large": 3}
        priority_order = {"high": 1, "medium": 2, "low": 3}
        role_tasks.sort(
            key=lambda x: (
                priority_order.get(x.get("priority", "medium"), 2),
                effort_order.get(x.get("estimated_effort", "medium"), 2)
            )
        )
        return role_tasks[0]

    # Fall back to general tasks if we're a dev role
    if general_tasks and role == "dev":
        effort_order = {"small": 1, "medium": 2, "large": 3}
        priority_order = {"high": 1, "medium": 2, "low": 3}
        general_tasks.sort(
            key=lambda x: (
                priority_order.get(x.get("priority", "medium"), 2),
                effort_order.get(x.get("estimated_effort", "medium"), 2)
            )
        )
        return general_tasks[0]

    return None


def claim_task(task, role):
    """Claim a task by assigning it to self and adding metadata"""
    task_id = task["id"]
    agent_id = f"{role}_{uuid.uuid4().hex[:8]}"
    current_time = datetime.utcnow().isoformat()
    
    # Assign the issue to self
    run_gh_command([
        "issue", "edit", task_id,
        "--add-assignee", "@me"
    ])
    
    # Add agent metadata as a comment
    metadata = {
        "agent_id": agent_id,
        "role": role,
        "status": "claimed",
        "claimed_at": current_time,
        "heartbeat": current_time,
        "worktree_path": f"./worktrees/agent-{role}-{task_id}"
    }
    
    comment = f"""### Agent Claimed Task
```json
{json.dumps(metadata, indent=2)}
```
"""
    
    run_gh_command([
        "issue", "comment", task_id,
        "--body", comment
    ])
    
    # Add in-progress label
    run_gh_command([
        "issue", "edit", task_id,
        "--add-label", "conductor:in-progress"
    ])
    
    return agent_id, metadata


def main():
    parser = argparse.ArgumentParser(description="Claim a task for an agent")
    parser.add_argument(
        "--role", required=True, help="Agent role (dev, devops, security, etc.)"
    )
    parser.add_argument("--task-id", help="Specific task ID to claim (optional)")
    parser.add_argument("--json", action="store_true", help="Output JSON format")

    args = parser.parse_args()

    # Get available tasks
    if args.task_id:
        # Check if specific task is available
        output = run_gh_command([
            "issue", "view", args.task_id,
            "--json", "number,title,body,labels,assignees,state"
        ])
        
        issue = json.loads(output)
        
        # Validate task is claimable
        if issue["state"] != "OPEN":
            result = {
                "status": "ERROR",
                "message": f"Task {args.task_id} is not open"
            }
            print(json.dumps(result))
            sys.exit(1)
        
        if issue["assignees"]:
            result = {
                "status": "ERROR",
                "message": f"Task {args.task_id} is already assigned"
            }
            print(json.dumps(result))
            sys.exit(1)
        
        # Check if it has conductor:task label
        has_conductor_label = any(
            label["name"] == "conductor:task" for label in issue["labels"]
        )
        if not has_conductor_label:
            result = {
                "status": "ERROR",
                "message": f"Issue {args.task_id} is not a conductor task"
            }
            print(json.dumps(result))
            sys.exit(1)
        
        # Convert to task format
        target_task = {
            "id": str(issue["number"]),
            "title": issue["title"],
            "description": issue["body"] or "",
            "required_skills": [],
            "estimated_effort": "medium",
            "priority": "medium"
        }
        
        # Extract metadata from labels
        for label in issue["labels"]:
            name = label["name"]
            if name.startswith("skill:"):
                target_task["required_skills"].append(name.replace("skill:", ""))
            elif name.startswith("effort:"):
                target_task["estimated_effort"] = name.replace("effort:", "")
            elif name.startswith("priority:"):
                target_task["priority"] = name.replace("priority:", "")
    else:
        # Find suitable task automatically
        available_tasks = get_available_tasks()
        target_task = find_suitable_task(available_tasks, args.role)

    if not target_task:
        result = {
            "status": "IDLE",
            "message": f"No tasks available for role: {args.role}",
        }
        print(json.dumps(result))
        sys.exit(0)

    # Claim the task
    try:
        agent_id, metadata = claim_task(target_task, args.role)

        result = {
            "status": "claimed",
            "agent_id": agent_id,
            "task_id": target_task["id"],
            "task": target_task,
            "worktree_path": metadata["worktree_path"],
            "claimed_at": metadata["claimed_at"],
        }
        print(json.dumps(result))

    except Exception as e:
        result = {"status": "ERROR", "message": f"Failed to claim task: {e}"}
        print(json.dumps(result))
        sys.exit(1)


if __name__ == "__main__":
    main()