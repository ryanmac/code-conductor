#!/usr/bin/env python3
"""Claim and assign tasks to agents using GitHub Issues"""

import os
import json
import sys
import uuid
import argparse
import subprocess
from datetime import datetime


def run_gh_command(args):
    """Run GitHub CLI command and return output"""
    try:
        result = subprocess.run(
            ["gh"] + args, capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f'{{"status": "ERROR", "message": "GitHub CLI error: {e.stderr}"}}')
        sys.exit(1)
    except FileNotFoundError:
        print(
            '{"status": "ERROR", "message": "GitHub CLI (gh) not found. Please install it."}'
        )
        sys.exit(1)


def get_available_tasks():
    """Get available tasks from GitHub Issues"""
    # Query open issues with conductor:task label that are not assigned
    output = run_gh_command(
        [
            "issue",
            "list",
            "-l",
            "conductor:task",
            "--state",
            "open",
            "--json",
            "number,title,body,labels,assignees,createdAt",
            "--jq",
            ".[] | select(.assignees | length == 0)",
        ]
    )

    if not output:
        return []

    # Parse tasks from JSON lines
    tasks = []
    for line in output.strip().split("\n"):
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
                    "priority": "medium",
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
    """Find a task suitable for the given role with smart matching"""
    if not tasks:
        return None

    # Role relationships for smart matching
    role_affinities = {
        "frontend": ["ui-designer", "ui", "react", "vue", "angular", "css"],
        "backend": ["api", "database", "server", "devops"],
        "devops": ["infrastructure", "ci-cd", "deployment", "monitoring"],
        "security": ["auth", "authentication", "vulnerability", "audit"],
        "ml-engineer": ["ml", "ai", "data-science", "model", "training"],
        "data": ["etl", "pipeline", "analytics", "database"],
        "mobile": ["ios", "android", "react-native", "flutter"],
        "ui-designer": ["design", "ux", "frontend", "css", "accessibility"],
    }

    # Score each task for the role
    scored_tasks = []

    for task in tasks:
        score = 0
        required_skills = task.get("required_skills", [])
        title_lower = task.get("title", "").lower()
        desc_lower = task.get("description", "").lower()

        # Exact role match gets highest score
        if role in required_skills:
            score += 100

        # Check if task requires no specific skills (general task)
        if not required_skills:
            if role == "dev":
                score += 50  # Dev role is perfect for general tasks
            else:
                score += 10  # Other roles can do general tasks too

        # Check role affinities
        if role in role_affinities:
            for affinity in role_affinities[role]:
                if affinity in required_skills:
                    score += 30
                # Check title and description for keywords
                if affinity in title_lower or affinity in desc_lower:
                    score += 20

        # Check for init tasks - everyone should be able to claim these
        # Note: labels might be in the raw issue data, not processed into task
        if (
            "init" in title_lower
            or "initialization" in title_lower
            or "discovery" in title_lower
        ):
            score += 80  # High priority for initialization tasks

        # Priority scoring
        priority_scores = {"critical": 30, "high": 20, "medium": 10, "low": 5}
        score += priority_scores.get(task.get("priority", "medium"), 10)

        # Effort scoring (prefer smaller tasks for faster iteration)
        effort_scores = {"small": 15, "medium": 10, "large": 5}
        score += effort_scores.get(task.get("estimated_effort", "medium"), 10)

        if score > 0:
            scored_tasks.append((score, task))

    if not scored_tasks:
        return None

    # Sort by score (highest first)
    scored_tasks.sort(key=lambda x: x[0], reverse=True)

    # Return the best matching task
    return scored_tasks[0][1]


def claim_task(task, role):
    """Claim a task by assigning it to self and adding metadata"""
    task_id = task["id"]
    agent_id = f"{role}_{uuid.uuid4().hex[:8]}"
    current_time = datetime.utcnow().isoformat()

    # Assign the issue to self
    run_gh_command(["issue", "edit", task_id, "--add-assignee", "@me"])

    # Add agent metadata as a comment
    metadata = {
        "agent_id": agent_id,
        "role": role,
        "status": "claimed",
        "claimed_at": current_time,
        "heartbeat": current_time,
        "worktree_path": f"./worktrees/agent-{role}-{task_id}",
    }

    comment = f"""### Agent Claimed Task
```json
{json.dumps(metadata, indent=2)}
```
"""

    run_gh_command(["issue", "comment", task_id, "--body", comment])

    # Add in-progress label
    run_gh_command(["issue", "edit", task_id, "--add-label", "conductor:in-progress"])

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
        output = run_gh_command(
            [
                "issue",
                "view",
                args.task_id,
                "--json",
                "number,title,body,labels,assignees,state",
            ]
        )

        issue = json.loads(output)

        # Validate task is claimable
        if issue["state"] != "OPEN":
            result = {"status": "ERROR", "message": f"Task {args.task_id} is not open"}
            print(json.dumps(result))
            sys.exit(1)

        if issue["assignees"]:
            result = {
                "status": "ERROR",
                "message": f"Task {args.task_id} is already assigned",
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
                "message": f"Issue {args.task_id} is not a conductor task",
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
            "priority": "medium",
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
