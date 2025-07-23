#!/usr/bin/env python3
"""
Migrate Code Conductor from JSON-based state to GitHub Issues

This script converts existing workflow-state.json tasks to GitHub Issues
and helps transition to the GitHub-native integration model.
"""

import json
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime


def run_gh_command(args):
    """Run GitHub CLI command and return output"""
    try:
        result = subprocess.run(
            ["gh"] + args, capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ GitHub CLI error: {e.stderr}")
        return None
    except FileNotFoundError:
        print("❌ GitHub CLI (gh) not found. Please install it.")
        sys.exit(1)


def load_workflow_state():
    """Load existing workflow state"""
    state_file = Path(".conductor/workflow-state.json")

    if not state_file.exists():
        print("❌ No workflow-state.json found. Nothing to migrate.")
        return None

    try:
        with open(state_file, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse workflow-state.json: {e}")
        return None


def create_github_labels():
    """Ensure required GitHub labels exist"""
    print("\n🏷️  Creating required GitHub labels...")

    labels = [
        ("conductor:task", "0e8a16", "Task for AI agents"),
        ("conductor:status", "1d76db", "System status tracking"),
        ("conductor:in-progress", "fbca04", "Task being worked on"),
        ("conductor:blocked", "d73a4a", "Task is blocked"),
        ("conductor:archived", "c5def5", "Archived task"),
        ("effort:small", "d4c5f9", "Small effort task"),
        ("effort:medium", "d4c5f9", "Medium effort task"),
        ("effort:large", "d4c5f9", "Large effort task"),
        ("priority:low", "0e8a16", "Low priority"),
        ("priority:medium", "fbca04", "Medium priority"),
        ("priority:high", "d73a4a", "High priority"),
    ]

    created = 0
    for name, color, description in labels:
        result = run_gh_command(
            [
                "label",
                "create",
                name,
                "--color",
                color,
                "--description",
                description,
                "--force",  # Update if exists
            ]
        )
        if result is not None:
            created += 1
            print(f"  ✓ Created/updated label: {name}")

    print(f"  Created/updated {created} labels")
    return created > 0


def migrate_task_to_issue(task, dry_run=False):
    """Convert a single task to a GitHub issue"""
    title = task.get("title", "Untitled Task")
    task_id = task.get("id", "unknown")

    # Build issue body
    body_parts = ["## Description"]
    body_parts.append(task.get("description", "No description provided"))

    # Add specifications
    if task.get("specs"):
        body_parts.append("\n## Specifications")
        body_parts.append(task["specs"])

    # Add success criteria
    if task.get("success_criteria"):
        body_parts.append("\n## Success Criteria")
        if isinstance(task["success_criteria"], dict):
            for key, value in task["success_criteria"].items():
                body_parts.append(f"- {key}: {value}")
        else:
            body_parts.append(str(task["success_criteria"]))

    # Add best practices
    if task.get("best_practices"):
        body_parts.append("\n## Best Practices")
        for practice in task["best_practices"]:
            body_parts.append(f"- {practice}")

    # Add metadata
    body_parts.append("\n---")
    body_parts.append(f"*Migrated from workflow-state.json (original ID: {task_id})*")
    if task.get("created_at"):
        body_parts.append(f"*Original creation date: {task['created_at']}*")

    body = "\n".join(body_parts)

    # Prepare labels
    labels = ["conductor:task"]

    # Add effort label
    effort = task.get("estimated_effort", "medium")
    if effort in ["small", "medium", "large"]:
        labels.append(f"effort:{effort}")

    # Add skill labels
    for skill in task.get("required_skills", []):
        labels.append(f"skill:{skill}")

    # Add priority (if specified)
    priority = task.get("priority", "medium")
    if priority in ["low", "medium", "high"]:
        labels.append(f"priority:{priority}")

    if dry_run:
        print(f"\n📋 Would create issue:")
        print(f"   Title: {title}")
        print(f"   Labels: {', '.join(labels)}")
        print(f"   Body preview: {body[:200]}...")
        return None

    # Create the issue
    cmd = ["issue", "create", "--title", title, "--body", body]

    for label in labels:
        cmd.extend(["--label", label])

    result = run_gh_command(cmd)

    if result and "#" in result:
        issue_number = result.split("#")[1].split()[0]
        print(f"✅ Created issue #{issue_number}: {title}")
        return issue_number
    else:
        print(f"❌ Failed to create issue for task: {title}")
        return None


def migrate_active_work(work_items, dry_run=False):
    """Migrate active work items"""
    print("\n🔄 Migrating active work...")

    if not work_items:
        print("  No active work to migrate")
        return

    for agent_id, work in work_items.items():
        task = work.get("task", {})
        title = task.get("title", "Unknown Task")

        print(f"\n  Agent {agent_id} working on: {title}")

        # First create the issue
        issue_number = migrate_task_to_issue(task, dry_run)

        if issue_number and not dry_run:
            # Assign to a placeholder user or add a comment
            comment = f"""### Active Work Migration

This task was being worked on by agent `{agent_id}` at the time of migration.

**Agent Details:**
- Role: {work.get('role', 'unknown')}
- Started: {work.get('claimed_at', 'unknown')}
- Last heartbeat: {work.get('heartbeat', 'unknown')}
- Status: {work.get('status', 'unknown')}

The task has been migrated but is now unassigned. Please claim it again if you want to continue working on it.
"""

            run_gh_command(["issue", "comment", issue_number, "--body", comment])

            # Add in-progress label
            run_gh_command(
                ["issue", "edit", issue_number, "--add-label", "conductor:in-progress"]
            )


def archive_json_state(state_file):
    """Archive the old JSON state file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"workflow-state.backup.{timestamp}.json"
    backup_path = state_file.parent / backup_name

    state_file.rename(backup_path)
    print(f"\n📦 Archived original state to: {backup_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Migrate Code Conductor from JSON state to GitHub Issues"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be migrated without making changes",
    )
    parser.add_argument(
        "--skip-labels", action="store_true", help="Skip creating GitHub labels"
    )
    parser.add_argument(
        "--available-only",
        action="store_true",
        help="Only migrate available tasks (skip active/completed)",
    )
    parser.add_argument(
        "--keep-json",
        action="store_true",
        help="Keep workflow-state.json file after migration",
    )

    args = parser.parse_args()

    print("🚀 Code Conductor Migration to GitHub Issues")
    print("=" * 50)

    # Check GitHub CLI
    if not run_gh_command(["auth", "status"]):
        print("❌ GitHub CLI not authenticated. Run 'gh auth login' first.")
        sys.exit(1)

    # Load existing state
    state = load_workflow_state()
    if not state:
        sys.exit(1)

    # Create labels
    if not args.skip_labels and not args.dry_run:
        create_github_labels()

    # Count items
    available_count = len(state.get("available_tasks", []))
    active_count = len(state.get("active_work", {}))
    completed_count = len(state.get("completed_work", []))

    print(f"\n📊 Found in workflow-state.json:")
    print(f"   - Available tasks: {available_count}")
    print(f"   - Active work: {active_count}")
    print(f"   - Completed work: {completed_count}")

    if args.dry_run:
        print("\n🔍 DRY RUN MODE - No changes will be made")

    # Migrate available tasks
    print(f"\n📝 Migrating {available_count} available tasks...")
    migrated = 0

    for task in state.get("available_tasks", []):
        if migrate_task_to_issue(task, args.dry_run):
            migrated += 1

    if not args.dry_run:
        print(f"  ✅ Migrated {migrated} tasks to GitHub Issues")

    # Migrate active work
    if not args.available_only:
        migrate_active_work(state.get("active_work", {}), args.dry_run)

    # Handle the JSON file
    if not args.dry_run and not args.keep_json:
        state_file = Path(".conductor/workflow-state.json")
        archive_json_state(state_file)

    # Final message
    if args.dry_run:
        print("\n✅ Dry run complete. Run without --dry-run to perform migration.")
    else:
        print("\n✅ Migration complete!")
        print("\n📋 Next steps:")
        print("1. Review the created issues on GitHub")
        print(
            "2. Update .conductor/config.yaml to ensure github_integration is enabled"
        )
        print("3. Run 'python .conductor/scripts/validate-config.py' to verify setup")
        print("4. Agents can now claim tasks using the updated bootstrap.sh")

        if args.keep_json:
            print("\n⚠️  workflow-state.json was kept. Remove it manually when ready.")


if __name__ == "__main__":
    main()
