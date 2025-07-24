#!/usr/bin/env python3
"""System health monitoring script using GitHub Issues"""

import json
import sys
import subprocess
import argparse
import os
from datetime import datetime, timedelta
from pathlib import Path


class HealthChecker:
    def __init__(self):
        self.config_file = Path(".conductor/config.yaml")
        self.issues = []
        self.warnings = []
        self.active_agents = {}
        self.stale_agents = []

    def run_gh_command(self, args):
        """Run GitHub CLI command and return output"""
        try:
            result = subprocess.run(
                ["gh"] + args, capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return ""
        except FileNotFoundError:
            print("GitHub CLI (gh) not found. Please install it.")
            return ""

    def get_conductor_issues(self):
        """Get all conductor task issues"""
        output = self.run_gh_command(
            [
                "issue",
                "list",
                "-l",
                "conductor:task",
                "--state",
                "open",
                "--limit",
                "1000",
                "--json",
                "number,title,assignees,labels,updatedAt",
            ]
        )

        if not output:
            return []

        try:
            return json.loads(output)
        except json.JSONDecodeError:
            return []

    def check_agent_heartbeats(self, assigned_issues):
        """Check for stale agent heartbeats in issue comments"""
        current_time = datetime.utcnow()
        timeout = 1200  # 20 minutes default

        for issue in assigned_issues:
            issue_number = issue["number"]

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
                continue

            # Find most recent heartbeat or agent activity
            latest_heartbeat = None
            agent_info = None

            for line in comments_output.strip().split("\n"):
                if line:
                    try:
                        comment = json.loads(line)
                        body = comment.get("body", "")

                        # Check for agent metadata or heartbeat
                        if "Agent Claimed Task" in body or "Heartbeat" in body:
                            comment_time = datetime.fromisoformat(
                                comment["createdAt"].replace("Z", "+00:00")
                            ).replace(tzinfo=None)

                            if not latest_heartbeat or comment_time > latest_heartbeat:
                                latest_heartbeat = comment_time

                                # Try to extract agent info
                                if "```json" in body:
                                    json_start = body.find("```json") + 7
                                    json_end = body.find("```", json_start)
                                    if json_end > json_start:
                                        try:
                                            metadata = json.loads(
                                                body[json_start:json_end]
                                            )
                                            agent_info = {
                                                "agent_id": metadata.get(
                                                    "agent_id", "unknown"
                                                ),
                                                "role": metadata.get("role", "unknown"),
                                                "task_id": issue_number,
                                                "task_title": issue["title"],
                                                "last_heartbeat": latest_heartbeat,
                                            }
                                        except json.JSONDecodeError:
                                            pass
                    except (json.JSONDecodeError, KeyError):
                        continue

            if agent_info:
                self.active_agents[agent_info["agent_id"]] = agent_info

                # Check if stale
                if (current_time - latest_heartbeat).total_seconds() > timeout:
                    self.stale_agents.append(agent_info)

        if self.stale_agents:
            self.issues.append(
                {
                    "type": "stale_agents",
                    "severity": "warning",
                    "agents": [
                        {
                            "agent_id": a["agent_id"],
                            "last_seen": a["last_heartbeat"].isoformat(),
                            "task": a["task_title"],
                        }
                        for a in self.stale_agents
                    ],
                }
            )

        return len(self.stale_agents) == 0

    def check_blocked_tasks(self):
        """Check for tasks marked as blocked"""
        # Look for issues with conductor:blocked label
        output = self.run_gh_command(
            [
                "issue",
                "list",
                "-l",
                "conductor:task,conductor:blocked",
                "--state",
                "open",
                "--json",
                "number,title,createdAt,labels",
            ]
        )

        if not output:
            return True

        try:
            blocked_issues = json.loads(output)
        except json.JSONDecodeError:
            return True

        blocked_threshold = timedelta(hours=4)
        current_time = datetime.utcnow()
        blocked_tasks = []

        for issue in blocked_issues:
            created = datetime.fromisoformat(
                issue["createdAt"].replace("Z", "+00:00")
            ).replace(tzinfo=None)

            if current_time - created > blocked_threshold:
                blocked_tasks.append(
                    {
                        "task_id": issue["number"],
                        "task": issue["title"],
                        "blocked_since": issue["createdAt"],
                    }
                )

        if blocked_tasks:
            self.issues.append(
                {"type": "blocked_tasks", "severity": "warning", "tasks": blocked_tasks}
            )

        return len(blocked_tasks) == 0

    def check_task_queue_health(self, available_count, active_count):
        """Check if task queue is healthy"""
        # Warning if too many tasks queued
        if available_count > 50:
            self.warnings.append(f"Large task queue: {available_count} tasks pending")

        # Remove "no tasks available" warning - it's normal for stable repos
        # Only warn if there are assigned tasks but no activity
        
        return True

    def update_status_issue(self, report, summary_type='daily'):
        """Update or create a status issue with the health report"""
        # Determine if we should create a new issue based on summary type
        should_create_new = False
        issue_title_prefix = "🏥 Code-Conductor"
        
        if summary_type == 'weekly':
            issue_title_prefix = "📅 Weekly Status:"
            should_create_new = True
        elif summary_type == 'monthly':
            issue_title_prefix = "📊 Monthly Status:"
            should_create_new = True
        
        # Check if status issue exists
        output = self.run_gh_command(
            [
                "issue",
                "list",
                "-l",
                "conductor:status",
                "--state",
                "open",
                "--limit",
                "10",
                "--json",
                "number,title,createdAt",
            ]
        )

        status_issue_number = None
        if output:
            try:
                issues = json.loads(output)
                if issues and not should_create_new:
                    # Use the most recent daily status issue
                    status_issue_number = issues[0]["number"]
                elif should_create_new:
                    # Close old status issues
                    for issue in issues:
                        self.run_gh_command(
                            ["issue", "close", str(issue["number"]), "-c", "Archiving old status issue"]
                        )
            except json.JSONDecodeError:
                pass

        # Format the report
        status_content = f"""## {issue_title_prefix} Health Report

**Timestamp**: {report['timestamp']}
**Status**: {report['status'].upper()}
**Summary Type**: {summary_type.title()}

### 📊 Metrics
- Active Agents: {report['metrics']['active_agents']}
- Available Tasks: {report['metrics']['available_tasks']}
- Assigned Tasks: {report['metrics']['assigned_tasks']}
- Completed Tasks: {report['metrics']['completed_tasks']}

"""

        if report["issues"]:
            status_content += "### ⚠️ Issues\n"
            for issue in report["issues"]:
                status_content += f"- **{issue['type']}** ({issue['severity']})\n"
                if issue["type"] == "stale_agents":
                    for agent in issue["agents"]:
                        status_content += f"  - Agent `{agent['agent_id']}` - Last seen: {agent['last_seen']}\n"

        if report["warnings"]:
            status_content += "\n### 💡 Warnings\n"
            for warning in report["warnings"]:
                status_content += f"- {warning}\n"

        status_content += "\n---\n*Generated by Code-Conductor health monitoring*"

        # Check if we should comment based on significant changes
        should_comment = False
        days_inactive = int(os.environ.get('DAYS_INACTIVE', '0'))
        
        # Always comment for weekly/monthly summaries
        if summary_type in ['weekly', 'monthly']:
            should_comment = True
        # Comment if there are issues or it's been active recently
        elif report["issues"] or days_inactive < 3:
            should_comment = True
        
        if status_issue_number and not should_create_new:
            # Update existing issue body
            self.run_gh_command(
                ["issue", "edit", str(status_issue_number), "--body", status_content]
            )
            
            # Only add comment if significant
            if should_comment:
                comment = f"### 📊 Status Update ({summary_type})"
                if report["issues"]:
                    comment += "\n\n⚠️ Issues detected - see updated status above."
                else:
                    comment += "\n\nSystem healthy - status refreshed."
                comment += f"\n\n*Timestamp: {datetime.utcnow().isoformat()}*"
                
                self.run_gh_command(
                    ["issue", "comment", str(status_issue_number), "--body", comment]
                )
        else:
            # Create new status issue
            title = f"{issue_title_prefix} {datetime.utcnow().strftime('%Y-%m-%d')}"
            self.run_gh_command(
                [
                    "issue",
                    "create",
                    "--title",
                    title,
                    "--body",
                    status_content,
                    "--label",
                    "conductor:status",
                ]
            )

    def generate_report(self, all_issues):
        """Generate health report"""
        available_tasks = [i for i in all_issues if not i.get("assignees")]
        assigned_tasks = [i for i in all_issues if i.get("assignees")]

        # Get completed count
        completed_output = self.run_gh_command(
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
                "number",
            ]
        )

        completed_count = 0
        if completed_output:
            try:
                completed_count = len(json.loads(completed_output))
            except json.JSONDecodeError:
                pass

        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "healthy",
            "metrics": {
                "active_agents": len(self.active_agents),
                "available_tasks": len(available_tasks),
                "assigned_tasks": len(assigned_tasks),
                "completed_tasks": completed_count,
            },
            "issues": self.issues,
            "warnings": self.warnings,
        }

        if self.issues:
            report["status"] = (
                "unhealthy"
                if any(i["severity"] == "error" for i in self.issues)
                else "degraded"
            )

        return report

    def run_checks(self, summary_type='daily'):
        """Run all health checks"""
        # Get all conductor issues
        all_issues = self.get_conductor_issues()

        if not all_issues and not self.run_gh_command(["auth", "status"]):
            print("❌ GitHub CLI not authenticated. Run 'gh auth login' first.")
            return False

        # Separate available and assigned tasks
        available_tasks = [i for i in all_issues if not i.get("assignees")]
        assigned_tasks = [i for i in all_issues if i.get("assignees")]

        # Run all checks
        self.check_agent_heartbeats(assigned_tasks)
        self.check_blocked_tasks()
        self.check_task_queue_health(len(available_tasks), len(assigned_tasks))

        # Generate report
        report = self.generate_report(all_issues)

        # Display report
        print(f"🏥 System Health: {report['status'].upper()}")
        print("📊 Metrics:")
        print(f"  - Active Agents: {report['metrics']['active_agents']}")
        print(f"  - Available Tasks: {report['metrics']['available_tasks']}")
        print(f"  - Assigned Tasks: {report['metrics']['assigned_tasks']}")
        print(f"  - Completed Tasks: {report['metrics']['completed_tasks']}")

        if report["issues"]:
            print("\n⚠️  Issues:")
            for issue in report["issues"]:
                print(f"  - {issue['type']}: {issue['severity']}")

        if report["warnings"]:
            print("\n💡 Warnings:")
            for warning in report["warnings"]:
                print(f"  - {warning}")

        # Update status issue
        self.update_status_issue(report, summary_type)

        return report["status"] != "unhealthy"


def main():
    parser = argparse.ArgumentParser(description='Run health checks for Code Conductor')
    parser.add_argument('--summary-type', choices=['daily', 'weekly', 'monthly'], 
                        default='daily', help='Type of summary to generate')
    parser.add_argument('--json', action='store_true', help='Output JSON format')
    args = parser.parse_args()
    
    checker = HealthChecker()
    success = checker.run_checks(args.summary_type)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
