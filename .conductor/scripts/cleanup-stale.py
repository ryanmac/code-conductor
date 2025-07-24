#!/usr/bin/env python3
"""Clean up stale work and abandoned tasks using GitHub Issues"""

import os
import json
import sys
import argparse
import subprocess
from datetime import datetime, timedelta


class StaleCleaner:
    def __init__(self, timeout_minutes=30):
        self.timeout = timedelta(minutes=timeout_minutes)
        self.cleaned_agents = []

    def run_gh_command(self, args):
        """Run GitHub CLI command and return output"""
        try:
            result = subprocess.run(
                ["gh"] + args, capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"GitHub CLI error: {e.stderr}")
            return ""
        except FileNotFoundError:
            print("GitHub CLI (gh) not found. Please install it.")
            return ""

    def get_assigned_issues(self):
        """Get all assigned conductor task issues"""
        output = self.run_gh_command(
            [
                "issue",
                "list",
                "-l",
                "conductor:task",
                "--state",
                "open",
                "--assignee",
                "*",  # Issues with any assignee
                "--limit",
                "1000",
                "--json",
                "number,title,assignees,labels",
            ]
        )

        if not output:
            return []

        try:
            return json.loads(output)
        except json.JSONDecodeError:
            return []

    def check_issue_staleness(self, issue_number):
        """Check if an issue is stale based on comment activity"""
        # Get recent comments
        comments_output = self.run_gh_command(
            [
                "issue",
                "view",
                str(issue_number),
                "--json",
                "comments",
                "--jq",
                ".comments[-10:] | reverse | .[]",  # Last 10 comments, newest first
            ]
        )

        if not comments_output:
            return True, None, None  # Consider stale if no comments

        current_time = datetime.utcnow()
        latest_activity = None
        agent_info = None

        # Parse comments to find latest activity
        for line in comments_output.strip().split("\n"):
            if line:
                try:
                    comment = json.loads(line)
                    body = comment.get("body", "")

                    # Check for agent activity (heartbeat, progress, etc.)
                    if any(
                        marker in body
                        for marker in ["Agent Claimed Task", "Heartbeat", "Progress"]
                    ):
                        comment_time = datetime.fromisoformat(
                            comment["createdAt"].replace("Z", "+00:00")
                        ).replace(tzinfo=None)

                        if not latest_activity or comment_time > latest_activity:
                            latest_activity = comment_time

                            # Try to extract agent info
                            if "```json" in body:
                                json_start = body.find("```json") + 7
                                json_end = body.find("```", json_start)
                                if json_end > json_start:
                                    try:
                                        metadata = json.loads(body[json_start:json_end])
                                        agent_info = metadata.get("agent_id", "unknown")
                                    except json.JSONDecodeError:
                                        pass
                except (json.JSONDecodeError, KeyError):
                    continue

        if latest_activity:
            is_stale = (current_time - latest_activity) > self.timeout
            return is_stale, latest_activity, agent_info

        return True, None, None  # Stale if no activity found

    def clean_stale_issue(self, issue):
        """Clean up a stale issue by unassigning and removing in-progress label"""
        issue_number = issue["number"]
        issue_title = issue["title"]

        # Check staleness
        is_stale, last_activity, agent_id = self.check_issue_staleness(issue_number)

        if not is_stale:
            return False

        print(f"🧹 Cleaning stale issue #{issue_number}: {issue_title}")

        # Remove all assignees
        if issue.get("assignees"):
            for assignee in issue["assignees"]:
                self.run_gh_command(
                    [
                        "issue",
                        "edit",
                        str(issue_number),
                        "--remove-assignee",
                        assignee["login"],
                    ]
                )

        # Remove in-progress label
        self.run_gh_command(
            [
                "issue",
                "edit",
                str(issue_number),
                "--remove-label",
                "conductor:in-progress",
            ]
        )

        # Add comment explaining the cleanup
        cleanup_comment = f"""### 🧹 Task Released - Stale Agent

This task has been automatically released due to inactivity.

- **Last activity**: {last_activity.isoformat() if last_activity else 'Unknown'}
- **Agent**: {agent_id if agent_id else 'Unknown'}
- **Timeout**: {self.timeout.total_seconds() / 60:.0f} minutes

The task is now available for other agents to claim.
"""

        self.run_gh_command(
            ["issue", "comment", str(issue_number), "--body", cleanup_comment]
        )

        self.cleaned_agents.append(
            {
                "issue_number": issue_number,
                "task": issue_title,
                "agent_id": agent_id,
                "last_activity": (
                    last_activity.isoformat() if last_activity else "Unknown"
                ),
            }
        )

        return True

    def clean_stale_work(self):
        """Remove stale agent work from issues"""
        print("🔍 Checking for stale agents...")

        # Get all assigned issues
        assigned_issues = self.get_assigned_issues()

        if not assigned_issues:
            print("✅ No assigned tasks found")
            return True

        print(f"📋 Found {len(assigned_issues)} assigned tasks")

        # Check each issue for staleness
        cleaned_count = 0
        for issue in assigned_issues:
            if self.clean_stale_issue(issue):
                cleaned_count += 1

        if cleaned_count > 0:
            print(f"\n✅ Cleaned up {cleaned_count} stale tasks")
            for agent in self.cleaned_agents:
                print(f"  - Issue #{agent['issue_number']}: {agent['task']}")
                print(
                    f"    Agent: {agent['agent_id']}, Last activity: {agent['last_activity']}"
                )
        else:
            print("✅ No stale agents found")

        return True

    def update_status_issue(self):
        """Update the status issue with cleanup information"""
        if not self.cleaned_agents:
            return

        # Find or create status issue
        output = self.run_gh_command(
            [
                "issue",
                "list",
                "-l",
                "conductor:status",
                "--state",
                "open",
                "--limit",
                "1",
                "--json",
                "number",
            ]
        )

        status_issue_number = None
        if output:
            try:
                issues = json.loads(output)
                if issues:
                    status_issue_number = issues[0]["number"]
            except json.JSONDecodeError:
                pass

        if status_issue_number:
            # Add cleanup report as comment
            cleanup_report = f"""### 🧹 Stale Agent Cleanup Report

**Timestamp**: {datetime.utcnow().isoformat()}
**Cleaned**: {len(self.cleaned_agents)} stale tasks

#### Released Tasks:
"""
            for agent in self.cleaned_agents:
                cleanup_report += (
                    f"- **Issue #{agent['issue_number']}**: {agent['task']}\n"
                )
                cleanup_report += f"  - Agent: `{agent['agent_id']}`\n"
                cleanup_report += f"  - Last activity: {agent['last_activity']}\n"

            cleanup_report += "\n---\n*Automated cleanup by Code-Conductor*"

            self.run_gh_command(
                ["issue", "comment", str(status_issue_number), "--body", cleanup_report]
            )


def main():
    parser = argparse.ArgumentParser(description="Clean up stale conductor work")
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Timeout in minutes for stale agents (default: 30)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be cleaned without making changes",
    )

    args = parser.parse_args()

    cleaner = StaleCleaner(timeout_minutes=args.timeout)

    # Run cleanup
    success = cleaner.clean_stale_work()

    if success and cleaner.cleaned_agents:
        # Update status issue with cleanup report
        cleaner.update_status_issue()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
