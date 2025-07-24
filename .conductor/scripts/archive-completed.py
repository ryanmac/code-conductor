#!/usr/bin/env python3
"""Archive old completed tasks and generate cleanup reports using GitHub Issues"""

import json
import sys
import subprocess
import argparse
from datetime import datetime, timedelta


class TaskArchiver:
    def __init__(self):
        self.archived_count = 0
        self.report_data = {}

    def run_gh_command(self, args):
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
            print(f"GitHub CLI error: {e.stderr}")
            return ""
        except FileNotFoundError:
            print("GitHub CLI (gh) not found. Please install it.")
            return ""

    def get_closed_issues(self, days_back=90):
        """Get closed conductor task issues within the specified time range"""
        # Calculate the date range
        since_date = (datetime.utcnow() - timedelta(days=days_back)).strftime(
            "%Y-%m-%d"
        )

        output = self.run_gh_command(
            [
                "issue",
                "list",
                "-l",
                "conductor:task",
                "--state",
                "closed",
                "--limit",
                "1000",
                "--json",
                "number,title,closedAt,labels",
                "--search",
                f"closed:>={since_date}",
            ]
        )

        if not output:
            return []

        try:
            return json.loads(output)
        except json.JSONDecodeError:
            return []

    def archive_old_issues(self, max_age_days=30, dry_run=False):
        """Add archive label to closed issues older than max_age_days"""
        print(f"🔍 Looking for closed issues older than {max_age_days} days...")

        # Get all closed issues
        closed_issues = self.get_closed_issues(days_back=max_age_days + 30)

        if not closed_issues:
            print("ℹ️  No closed issues found")
            return

        current_time = datetime.utcnow()
        cutoff_date = current_time - timedelta(days=max_age_days)
        issues_to_archive = []

        for issue in closed_issues:
            # Skip if already archived
            if any(
                label["name"] == "conductor:archived"
                for label in issue.get("labels", [])
            ):
                continue

            closed_at_str = issue.get("closedAt")
            if closed_at_str:
                try:
                    closed_at = datetime.fromisoformat(
                        closed_at_str.replace("Z", "+00:00")
                    ).replace(tzinfo=None)

                    if closed_at < cutoff_date:
                        issues_to_archive.append(
                            {
                                "number": issue["number"],
                                "title": issue["title"],
                                "closed_at": closed_at_str,
                            }
                        )
                except ValueError:
                    continue

        if not issues_to_archive:
            print("ℹ️  No issues need archiving")
            return

        print(f"📦 Found {len(issues_to_archive)} issue(s) to archive")

        if not dry_run:
            for issue in issues_to_archive:
                print(f"  - Archiving issue #{issue['number']}: {issue['title']}")

                # Add archive label
                self.run_gh_command(
                    [
                        "issue",
                        "edit",
                        str(issue["number"]),
                        "--add-label",
                        "conductor:archived",
                    ]
                )

                # Add archive comment
                archive_comment = f"""### 📦 Task Archived

This completed task has been archived after {max_age_days} days.

- **Closed at**: {issue['closed_at']}
- **Archive date**: {current_time.isoformat()}

This helps keep the active task list manageable while preserving history.
"""

                self.run_gh_command(
                    [
                        "issue",
                        "comment",
                        str(issue["number"]),
                        "--body",
                        archive_comment,
                    ]
                )

                self.archived_count += 1
        else:
            print("(DRY RUN - no changes made)")
            for issue in issues_to_archive:
                print(f"  - Would archive issue #{issue['number']}: {issue['title']}")
            self.archived_count = len(issues_to_archive)

    def generate_metrics_report(self):
        """Generate system metrics report"""
        print("\n📊 Generating system metrics...")

        # Get counts for different states
        metrics = {}

        # Open tasks (available)
        output = self.run_gh_command(
            [
                "issue",
                "list",
                "-l",
                "conductor:task",
                "--state",
                "open",
                "--assignee",
                "!*",  # Not assigned
                "--json",
                "number",
                "--jq",
                ". | length",
            ]
        )
        metrics["available_tasks"] = int(output) if output.isdigit() else 0

        # Assigned tasks
        output = self.run_gh_command(
            [
                "issue",
                "list",
                "-l",
                "conductor:task",
                "--state",
                "open",
                "--assignee",
                "*",  # Has assignee
                "--json",
                "number",
                "--jq",
                ". | length",
            ]
        )
        metrics["assigned_tasks"] = int(output) if output.isdigit() else 0

        # Completed tasks (closed, not archived)
        output = self.run_gh_command(
            [
                "issue",
                "list",
                "-l",
                "conductor:task,!conductor:archived",
                "--state",
                "closed",
                "--json",
                "number",
                "--jq",
                ". | length",
            ]
        )
        metrics["completed_tasks"] = int(output) if output.isdigit() else 0

        # Archived tasks
        output = self.run_gh_command(
            [
                "issue",
                "list",
                "-l",
                "conductor:task,conductor:archived",
                "--state",
                "closed",
                "--json",
                "number",
                "--jq",
                ". | length",
            ]
        )
        metrics["archived_tasks"] = int(output) if output.isdigit() else 0

        # Recent completions (last 24h)
        yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
        output = self.run_gh_command(
            [
                "issue",
                "list",
                "-l",
                "conductor:task",
                "--state",
                "closed",
                "--search",
                f"closed:>={yesterday}",
                "--json",
                "number",
                "--jq",
                ". | length",
            ]
        )
        metrics["recent_completions"] = int(output) if output.isdigit() else 0

        self.report_data = metrics

        # Display report
        print("\n📊 System Metrics")
        print("=" * 40)
        print(f"Available Tasks:      {metrics['available_tasks']}")
        print(f"Assigned Tasks:       {metrics['assigned_tasks']}")
        print(f"Completed Tasks:      {metrics['completed_tasks']}")
        print(f"Archived Tasks:       {metrics['archived_tasks']}")
        print(f"Recent Completions:   {metrics['recent_completions']} (last 24h)")
        print(
            f"Total Active:         {metrics['available_tasks'] + metrics['assigned_tasks']}"
        )

    def update_status_issue(self):
        """Update the status issue with archive report"""
        if self.archived_count == 0:
            return

        # Find status issue
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
            # Add archive report
            archive_report = f"""### 📦 Archive Report

**Timestamp**: {datetime.utcnow().isoformat()}
**Archived**: {self.archived_count} tasks

#### System Metrics:
- Available Tasks: {self.report_data.get('available_tasks', 0)}
- Assigned Tasks: {self.report_data.get('assigned_tasks', 0)}
- Completed Tasks: {self.report_data.get('completed_tasks', 0)}
- Archived Tasks: {self.report_data.get('archived_tasks', 0)}
- Recent Completions (24h): {self.report_data.get('recent_completions', 0)}

---
*Automated archival by Code-Conductor*"""

            self.run_gh_command(
                ["issue", "comment", str(status_issue_number), "--body", archive_report]
            )


def main():
    parser = argparse.ArgumentParser(
        description="Archive old completed tasks and generate reports"
    )
    parser.add_argument(
        "--max-age",
        type=int,
        default=30,
        help="Maximum age in days for completed tasks before archiving (default: 30)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--skip-metrics",
        action="store_true",
        help="Skip generating metrics report",
    )

    args = parser.parse_args()

    print("🧹 Starting archive and cleanup process...")

    archiver = TaskArchiver()

    # Check if we have a token available
    if not any(
        os.environ.get(var)
        for var in ["GH_TOKEN", "GITHUB_TOKEN", "CONDUCTOR_GITHUB_TOKEN"]
    ):
        print("❌ No GitHub token found. Please set CONDUCTOR_GITHUB_TOKEN.")
        sys.exit(1)

    # Archive old issues
    archiver.archive_old_issues(max_age_days=args.max_age, dry_run=args.dry_run)

    # Generate metrics report
    if not args.skip_metrics:
        archiver.generate_metrics_report()

    # Update status issue
    if not args.dry_run and archiver.archived_count > 0:
        archiver.update_status_issue()

    print(f"\n✅ Archive process completed")
    print(f"   Archived: {archiver.archived_count} tasks")

    if args.dry_run:
        print("\nRun without --dry-run to perform archival")


if __name__ == "__main__":
    main()
