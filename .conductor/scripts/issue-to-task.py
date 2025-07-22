#!/usr/bin/env python3
"""Convert GitHub Issue to Conductor Task"""

import json
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime


def get_issue_details(issue_number):
    """Get issue details from GitHub CLI"""
    try:
        result = subprocess.run(
            [
                "gh",
                "issue",
                "view",
                str(issue_number),
                "--json",
                "title,body,labels,assignees,state",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to fetch issue #{issue_number}: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ GitHub CLI (gh) not found. Please install it.")
        sys.exit(1)


def parse_issue_body(body):
    """Parse issue body for task metadata"""
    if not body:
        return {}

    metadata = {}
    lines = body.split("\n")
    current_section = None
    content = []

    for line in lines:
        line = line.strip()
        if line.startswith("## ") or line.startswith("### "):
            if current_section and content:
                metadata[current_section] = "\n".join(content).strip()
            current_section = line.replace("#", "").strip().lower()
            content = []
        else:
            if line:
                content.append(line)

    # Capture final section
    if current_section and content:
        metadata[current_section] = "\n".join(content).strip()

    return metadata


def extract_task_data(issue, metadata, issue_number):
    """Extract task data from issue and metadata"""
    # Extract labels
    labels = [label["name"] for label in issue.get("labels", [])]

    # Determine required skills
    required_skills = []
    for label in labels:
        if label.startswith("skill:"):
            required_skills.append(label.replace("skill:", ""))
        elif label in ["devops", "security", "ui-designer", "rust-dev"]:
            required_skills.append(label)

    # Determine effort level
    effort = "medium"  # default
    for label in labels:
        if label.startswith("effort:"):
            effort = label.replace("effort:", "")
        elif label in ["small", "medium", "large"]:
            effort = label

    # Extract files from metadata or estimate from title/body
    files_involved = []
    if "files" in metadata:
        files_involved = [f.strip() for f in metadata["files"].split("\n") if f.strip()]

    # Build task
    task = {
        "id": f"issue_{issue_number}",
        "title": issue["title"],
        "description": metadata.get("description", issue["title"]),
        "specs": metadata.get("specifications", f"GitHub Issue #{issue_number}"),
        "best_practices": [],
        "success_criteria": {},
        "required_skills": required_skills,
        "estimated_effort": effort,
        "files_locked": files_involved,
        "dependencies": [],
        "source": {
            "type": "github_issue",
            "issue_number": issue_number,
            "url": f"https://github.com/ryanmac/conductor-score/issues/{issue_number}",
        },
        "created_at": datetime.utcnow().isoformat(),
    }

    # Parse best practices if available
    if "best practices" in metadata:
        task["best_practices"] = [
            bp.strip("- ").strip()
            for bp in metadata["best practices"].split("\n")
            if bp.strip()
        ]

    # Parse success criteria
    if "success criteria" in metadata:
        criteria_text = metadata["success criteria"]
        if criteria_text:
            # Try to parse as key-value pairs
            criteria = {}
            for line in criteria_text.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    criteria[key.strip("- ").strip()] = value.strip()
                else:
                    criteria["completion"] = criteria_text
            task["success_criteria"] = criteria

    return task


def add_task_to_state(task):
    """Add task to workflow state"""
    state_file = Path(".conductor/workflow-state.json")

    if not state_file.exists():
        print("❌ Workflow state file not found")
        sys.exit(1)

    try:
        with open(state_file, "r") as f:
            state = json.load(f)
    except json.JSONDecodeError:
        print("❌ Invalid workflow state file")
        sys.exit(1)

    # Check if task already exists
    existing_task = None
    for i, existing in enumerate(state.get("available_tasks", [])):
        if existing.get("id") == task["id"]:
            existing_task = i
            break

    if existing_task is not None:
        # Update existing task
        state["available_tasks"][existing_task] = task
        print(f"✅ Updated existing task: {task['id']}")
    else:
        # Add new task
        if "available_tasks" not in state:
            state["available_tasks"] = []
        state["available_tasks"].append(task)
        print(f"✅ Added new task: {task['id']}")

    # Update system status
    if "system_status" not in state:
        state["system_status"] = {}
    state["system_status"]["last_updated"] = datetime.utcnow().isoformat()

    # Write back to file
    try:
        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)
        print("✅ State file updated")
    except Exception as e:
        print(f"❌ Failed to write state file: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Convert GitHub Issue to Conductor Task"
    )
    parser.add_argument(
        "--issue-number", type=int, required=True, help="GitHub issue number"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )

    args = parser.parse_args()
    issue_number = args.issue_number

    print(f"🔄 Processing issue #{issue_number}...")

    # Get issue details
    issue = get_issue_details(issue_number)

    # Check if issue has conductor:task label
    labels = [label["name"] for label in issue.get("labels", [])]
    if "conductor:task" not in labels:
        print(f"⚠️  Issue #{issue_number} doesn't have 'conductor:task' label")
        print("Add the label and try again.")
        sys.exit(1)

    # Check if issue is open
    if issue.get("state") != "open":
        print(f"⚠️  Issue #{issue_number} is not open")
        sys.exit(1)

    # Parse issue body for metadata
    metadata = parse_issue_body(issue.get("body", ""))

    # Create task
    task = extract_task_data(issue, metadata, issue_number)

    if args.dry_run:
        print("\n📋 Task that would be created:")
        print(json.dumps(task, indent=2))
        print("\n(Use without --dry-run to actually create the task)")
    else:
        # Add to state
        add_task_to_state(task)
        print("\n🎯 Task created successfully!")
        print(f"   Title: {task['title']}")
        print(f"   ID: {task['id']}")
        print(f"   Effort: {task['estimated_effort']}")
        if task["required_skills"]:
            print(f"   Skills: {', '.join(task['required_skills'])}")


if __name__ == "__main__":
    main()
