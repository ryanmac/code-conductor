#!/usr/bin/env python3
"""Format GitHub Issue as a Conductor Task"""

import json
import sys
import argparse
import subprocess
from datetime import datetime


def run_gh_command(args):
    """Run GitHub CLI command and return output"""
    try:
        # Pass environment variables and map GITHUB_TOKEN to GH_TOKEN
        env = os.environ.copy()
        if "GITHUB_TOKEN" in env and "GH_TOKEN" not in env:
            env["GH_TOKEN"] = env["GITHUB_TOKEN"]
        elif "CONDUCTOR_GITHUB_TOKEN" in env and "GH_TOKEN" not in env:
            env["GH_TOKEN"] = env["CONDUCTOR_GITHUB_TOKEN"]
        
        result = subprocess.run(
            ["gh"] + args, capture_output=True, text=True, check=True, env=env
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ GitHub CLI error: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ GitHub CLI (gh) not found. Please install it.")
        sys.exit(1)


def get_issue_details(issue_number):
    """Get issue details from GitHub"""
    output = run_gh_command(
        [
            "issue",
            "view",
            str(issue_number),
            "--json",
            "title,body,labels,assignees,state",
        ]
    )

    try:
        return json.loads(output)
    except json.JSONDecodeError:
        print(f"❌ Failed to parse issue #{issue_number}")
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


def format_task_body(issue, metadata):
    """Format issue body with conductor task structure"""
    title = issue["title"]
    existing_body = issue.get("body", "")

    # If body already has good structure, preserve it
    if any(
        section in existing_body.lower()
        for section in ["## description", "## specifications", "## success criteria"]
    ):
        return existing_body

    # Otherwise, create structured body
    body_parts = []

    # Description
    body_parts.append("## Description")
    if "description" in metadata:
        body_parts.append(metadata["description"])
    elif existing_body:
        # Use first paragraph as description
        desc_lines = []
        for line in existing_body.split("\n"):
            if line.strip():
                desc_lines.append(line)
            else:
                break
        body_parts.append("\n".join(desc_lines) if desc_lines else title)
    else:
        body_parts.append(title)

    # Specifications
    body_parts.append("\n## Specifications")
    if "specifications" in metadata:
        body_parts.append(metadata["specifications"])
    else:
        body_parts.append("- [ ] Implement the feature/fix as described")
        body_parts.append("- [ ] Add appropriate tests")
        body_parts.append("- [ ] Update documentation if needed")

    # Success Criteria
    body_parts.append("\n## Success Criteria")
    if "success criteria" in metadata:
        body_parts.append(metadata["success criteria"])
    else:
        body_parts.append("- All tests pass")
        body_parts.append("- Code follows project conventions")
        body_parts.append("- Feature works as described")

    # Files (if specified)
    if "files" in metadata:
        body_parts.append("\n## Files Involved")
        body_parts.append(metadata["files"])

    # Best Practices (if specified)
    if "best practices" in metadata:
        body_parts.append("\n## Best Practices")
        body_parts.append(metadata["best practices"])

    return "\n".join(body_parts)


def add_conductor_labels(issue_number, issue_labels):
    """Add appropriate conductor labels to issue"""
    existing_labels = [label["name"] for label in issue_labels]
    labels_to_add = []

    # Always add conductor:task if not present
    if "conductor:task" not in existing_labels:
        labels_to_add.append("conductor:task")

    # Check for effort labels
    has_effort = any(label.startswith("effort:") for label in existing_labels)
    if not has_effort and not any(
        label in ["small", "medium", "large"] for label in existing_labels
    ):
        labels_to_add.append("effort:medium")  # Default effort

    # Check for priority labels
    has_priority = any(label.startswith("priority:") for label in existing_labels)
    if not has_priority and not any(
        label in ["high", "medium", "low"] for label in existing_labels
    ):
        labels_to_add.append("priority:medium")  # Default priority

    # Add labels if needed
    if labels_to_add:
        print(f"📎 Adding labels: {', '.join(labels_to_add)}")
        for label in labels_to_add:
            run_gh_command(["issue", "edit", str(issue_number), "--add-label", label])

    return labels_to_add


def format_issue_as_task(issue_number, dry_run=False):
    """Format a GitHub issue as a conductor task"""
    print(f"🔄 Processing issue #{issue_number}...")

    # Get issue details
    issue = get_issue_details(issue_number)

    # Check if issue is open
    if issue.get("state") != "OPEN":
        print(f"⚠️  Issue #{issue_number} is not open")
        return False

    # Parse existing body
    metadata = parse_issue_body(issue.get("body", ""))

    # Format body with conductor structure
    new_body = format_task_body(issue, metadata)

    if dry_run:
        print("\n📋 Changes that would be made:")
        print("\nFormatted body:")
        print("-" * 40)
        print(new_body)
        print("-" * 40)

        # Check what labels would be added
        existing_labels = [label["name"] for label in issue.get("labels", [])]
        if "conductor:task" not in existing_labels:
            print("\nWould add label: conductor:task")
        if not any(
            label.startswith("effort:") or label in ["small", "medium", "large"]
            for label in existing_labels
        ):
            print("Would add label: effort:medium")
        if not any(
            label.startswith("priority:") or label in ["high", "medium", "low"]
            for label in existing_labels
        ):
            print("Would add label: priority:medium")
    else:
        # Update issue body if changed
        if new_body != issue.get("body", ""):
            print("📝 Updating issue body with conductor structure...")
            run_gh_command(["issue", "edit", str(issue_number), "--body", new_body])

        # Add conductor labels
        labels_added = add_conductor_labels(issue_number, issue.get("labels", []))

        # Add formatting comment
        if labels_added or new_body != issue.get("body", ""):
            comment = """### 🎼 Issue Formatted as Conductor Task

This issue has been formatted to work with the Code-Conductor system.

**What changed:**
"""
            if new_body != issue.get("body", ""):
                comment += "- ✅ Body structured with Description, Specifications, and Success Criteria\n"
            if labels_added:
                comment += f"- ✅ Added labels: {', '.join(labels_added)}\n"

            comment += """
**Next steps:**
1. Review and adjust the task description if needed
2. Add skill labels if specific expertise is required (e.g., `skill:rust`, `skill:frontend`)
3. Adjust effort/priority labels if needed
4. The task is now ready for agents to claim!

Use `python .conductor/scripts/bootstrap.sh dev` to claim this task.
"""

            run_gh_command(["issue", "comment", str(issue_number), "--body", comment])

        print(f"\n✅ Issue #{issue_number} formatted as conductor task!")
        print(f"   Title: {issue['title']}")
        print("   Status: Ready for agents to claim")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Format GitHub Issue as a Conductor Task"
    )
    parser.add_argument("issue_number", type=int, help="GitHub issue number to format")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )

    args = parser.parse_args()

    # Check if we have a token available
    if not any(
        os.environ.get(var)
        for var in ["GH_TOKEN", "GITHUB_TOKEN", "CONDUCTOR_GITHUB_TOKEN"]
    ):
        print("❌ No GitHub token found. Please set CONDUCTOR_GITHUB_TOKEN.")
        sys.exit(1)

    # Format the issue
    success = format_issue_as_task(args.issue_number, args.dry_run)

    if args.dry_run and success:
        print("\nRun without --dry-run to apply these changes.")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
