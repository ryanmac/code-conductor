#!/usr/bin/env python3
"""Update system status using GitHub Issues"""

import json
import sys
import subprocess
from datetime import datetime, timedelta
from collections import defaultdict


def run_gh_command(args):
    """Run GitHub CLI command and return output"""
    try:
        result = subprocess.run(
            ["gh"] + args, capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ GitHub CLI error: {e.stderr}")
        return ""
    except FileNotFoundError:
        print("❌ GitHub CLI (gh) not found. Please install it.")
        sys.exit(1)


def get_status_issue():
    """Get or create the status issue"""
    # Check if status issue exists
    output = run_gh_command(
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
            "number,title",
        ]
    )

    if output:
        try:
            issues = json.loads(output)
            if issues:
                return issues[0]["number"]
        except json.JSONDecodeError:
            pass

    # Create new status issue if it doesn't exist
    print("📝 Creating new status issue...")
    output = run_gh_command(
        [
            "issue",
            "create",
            "--title",
            "🏥 Code-Conductor System Status",
            "--body",
            "This issue tracks the system status and health metrics for Code-Conductor.",
            "--label",
            "conductor:status",
        ]
    )

    # Extract issue number from output
    if output and "#" in output:
        issue_number = output.split("#")[1].split()[0]
        return int(issue_number)

    return None


def collect_metrics():
    """Collect system metrics from GitHub Issues"""
    metrics = {
        "timestamp": datetime.utcnow().isoformat(),
        "tasks": {},
        "agents": {},
        "health": {},
    }

    # Get all conductor task issues
    output = run_gh_command(
        [
            "issue",
            "list",
            "-l",
            "conductor:task",
            "--state",
            "all",
            "--limit",
            "1000",
            "--json",
            "number,title,state,assignees,labels,createdAt,updatedAt,closedAt",
        ]
    )

    if not output:
        return metrics

    try:
        all_issues = json.loads(output)
    except json.JSONDecodeError:
        return metrics

    # Categorize issues
    available_tasks = []
    assigned_tasks = []
    completed_tasks = []

    for issue in all_issues:
        if issue["state"] == "OPEN":
            if issue.get("assignees"):
                assigned_tasks.append(issue)
            else:
                available_tasks.append(issue)
        else:  # CLOSED
            completed_tasks.append(issue)

    metrics["tasks"]["available"] = len(available_tasks)
    metrics["tasks"]["assigned"] = len(assigned_tasks)
    metrics["tasks"]["completed"] = len(completed_tasks)
    metrics["tasks"]["total"] = len(all_issues)

    # Analyze available tasks
    tasks_by_effort = defaultdict(int)
    tasks_by_priority = defaultdict(int)
    tasks_by_skill = defaultdict(int)

    for task in available_tasks:
        for label in task.get("labels", []):
            name = label["name"]
            if name.startswith("effort:"):
                tasks_by_effort[name.replace("effort:", "")] += 1
            elif name.startswith("priority:"):
                tasks_by_priority[name.replace("priority:", "")] += 1
            elif name.startswith("skill:"):
                tasks_by_skill[name.replace("skill:", "")] += 1

        # Default counts
        if not any(l["name"].startswith("effort:") for l in task.get("labels", [])):
            tasks_by_effort["unspecified"] += 1
        if not any(l["name"].startswith("priority:") for l in task.get("labels", [])):
            tasks_by_priority["unspecified"] += 1
        if not any(l["name"].startswith("skill:") for l in task.get("labels", [])):
            tasks_by_skill["general"] += 1

    metrics["tasks"]["by_effort"] = dict(tasks_by_effort)
    metrics["tasks"]["by_priority"] = dict(tasks_by_priority)
    metrics["tasks"]["by_skill"] = dict(tasks_by_skill)

    # Calculate completion metrics
    now = datetime.utcnow()
    day_ago = now - timedelta(days=1)
    week_ago = now - timedelta(days=7)

    completions_24h = 0
    completions_7d = 0

    for task in completed_tasks:
        if task.get("closedAt"):
            closed_at = datetime.fromisoformat(
                task["closedAt"].replace("Z", "+00:00")
            ).replace(tzinfo=None)

            if closed_at >= day_ago:
                completions_24h += 1
            if closed_at >= week_ago:
                completions_7d += 1

    metrics["tasks"]["completions_24h"] = completions_24h
    metrics["tasks"]["completions_7d"] = completions_7d

    # Analyze active agents (from assigned tasks)
    active_agents = {}
    stale_agents = 0

    for task in assigned_tasks:
        # Get last activity from comments
        issue_number = task["number"]
        comments_output = run_gh_command(
            [
                "issue",
                "view",
                str(issue_number),
                "--json",
                "comments",
                "--jq",
                ".comments[-1]",  # Get last comment
            ]
        )

        if comments_output:
            try:
                last_comment = json.loads(comments_output)
                if last_comment and (
                    "Agent Claimed Task" in last_comment.get("body", "")
                    or "Heartbeat" in last_comment.get("body", "")
                ):
                    comment_time = datetime.fromisoformat(
                        last_comment["createdAt"].replace("Z", "+00:00")
                    ).replace(tzinfo=None)

                    # Check if stale (no activity in 30 minutes)
                    if (now - comment_time).total_seconds() > 1800:
                        stale_agents += 1
            except (json.JSONDecodeError, KeyError):
                pass

    metrics["agents"]["active"] = len(assigned_tasks)
    metrics["agents"]["stale"] = stale_agents

    # Calculate health metrics
    metrics["health"]["has_available_tasks"] = metrics["tasks"]["available"] > 0
    metrics["health"]["has_active_agents"] = metrics["agents"]["active"] > 0
    metrics["health"]["low_stale_ratio"] = (
        metrics["agents"]["stale"] < metrics["agents"]["active"] * 0.3
        if metrics["agents"]["active"] > 0
        else True
    )
    metrics["health"]["recent_activity"] = (
        completions_24h > 0 or metrics["agents"]["active"] > 0
    )

    # Calculate health score
    health_checks = [v for k, v in metrics["health"].items() if k != "score"]
    health_score = sum(health_checks) / len(health_checks) if health_checks else 0
    metrics["health"]["score"] = round(health_score, 2)

    return metrics


def format_status_report(metrics):
    """Format metrics as a status report"""
    report = f"""## 🏥 Code-Conductor System Status

**Last Updated**: {metrics['timestamp']}
**Health Score**: {metrics['health']['score']:.0%} {get_health_emoji(metrics['health']['score'])}

### 📊 Task Metrics

| Metric | Count |
|--------|-------|
| Available Tasks | {metrics['tasks']['available']} |
| Assigned Tasks | {metrics['tasks']['assigned']} |
| Completed Tasks | {metrics['tasks']['completed']} |
| Total Tasks | {metrics['tasks']['total']} |
| Completions (24h) | {metrics['tasks']['completions_24h']} |
| Completions (7d) | {metrics['tasks']['completions_7d']} |

### 🤖 Agent Metrics

| Metric | Count |
|--------|-------|
| Active Agents | {metrics['agents']['active']} |
| Stale Agents | {metrics['agents']['stale']} |

"""

    # Add task breakdown if available
    if metrics["tasks"]["available"] > 0:
        report += "### 📋 Available Task Breakdown\n\n"

        if metrics["tasks"]["by_effort"]:
            report += "**By Effort:**\n"
            for effort, count in sorted(metrics["tasks"]["by_effort"].items()):
                report += f"- {effort}: {count}\n"
            report += "\n"

        if metrics["tasks"]["by_priority"]:
            report += "**By Priority:**\n"
            for priority, count in sorted(metrics["tasks"]["by_priority"].items()):
                report += f"- {priority}: {count}\n"
            report += "\n"

        if metrics["tasks"]["by_skill"]:
            report += "**By Required Skills:**\n"
            for skill, count in sorted(metrics["tasks"]["by_skill"].items()):
                report += f"- {skill}: {count}\n"
            report += "\n"

    # Add health indicators
    report += "### 🏥 Health Indicators\n\n"
    report += f"- {'✅' if metrics['health']['has_available_tasks'] else '❌'} Has available tasks\n"
    report += f"- {'✅' if metrics['health']['has_active_agents'] else '❌'} Has active agents\n"
    report += f"- {'✅' if metrics['health']['low_stale_ratio'] else '❌'} Low stale agent ratio\n"
    report += (
        f"- {'✅' if metrics['health']['recent_activity'] else '❌'} Recent activity\n"
    )

    # Add quick actions
    report += "\n### 🚀 Quick Actions\n\n"
    if metrics["tasks"]["available"] == 0:
        report += "- [Create a new task](../../issues/new?labels=conductor:task)\n"
    if metrics["agents"]["active"] == 0:
        report += "- Launch an agent: `bash .conductor/scripts/bootstrap.sh dev`\n"
    if metrics["agents"]["stale"] > 0:
        report += (
            "- Clean up stale agents: `python .conductor/scripts/cleanup-stale.py`\n"
        )

    report += "\n---\n*Updated automatically by Code-Conductor status monitor*"

    return report


def get_health_emoji(score):
    """Get emoji for health score"""
    if score >= 0.8:
        return "🟢"
    elif score >= 0.6:
        return "🟡"
    elif score >= 0.4:
        return "🟠"
    else:
        return "🔴"


def update_status_issue(issue_number, report, add_comment=True):
    """Update the status issue with the latest report"""
    # Update issue body
    run_gh_command(["issue", "edit", str(issue_number), "--body", report])

    # Add update comment only if requested
    if add_comment:
        comment = f"""### 📊 Status Updated

System status has been refreshed with the latest metrics.

View the updated status in the issue description above.

*Timestamp: {datetime.utcnow().isoformat()}*"""

        run_gh_command(["issue", "comment", str(issue_number), "--body", comment])


def print_summary(metrics):
    """Print a summary to console"""
    print("\n📊 System Status Summary")
    print("=" * 40)
    print(
        f"Health Score:      {metrics['health']['score']:.0%} {get_health_emoji(metrics['health']['score'])}"
    )
    print(f"Available Tasks:   {metrics['tasks']['available']}")
    print(f"Active Agents:     {metrics['agents']['active']}")
    print(f"Completions (24h): {metrics['tasks']['completions_24h']}")

    if metrics["agents"]["stale"] > 0:
        print(f"⚠️  Stale Agents:    {metrics['agents']['stale']}")

    print(f"\nLast Updated: {metrics['timestamp']}")


def main():
    parser = argparse.ArgumentParser(description='Update system status')
    parser.add_argument('--no-comment', action='store_true', 
                        help='Update issue body without adding a comment')
    parser.add_argument('--json', action='store_true',
                        help='Output metrics as JSON')
    args = parser.parse_args()
    
    if not args.json:
        print("🔄 Updating system status...")

    # Check GitHub CLI authentication
    if not run_gh_command(["auth", "status"]):
        if not args.json:
            print("❌ GitHub CLI not authenticated. Run 'gh auth login' first.")
        sys.exit(1)

    # Get or create status issue
    issue_number = get_status_issue()
    if not issue_number:
        if not args.json:
            print("❌ Failed to get or create status issue")
        sys.exit(1)

    if not args.json:
        print(f"📍 Using status issue #{issue_number}")

    # Collect metrics
    if not args.json:
        print("📊 Collecting system metrics...")
    metrics = collect_metrics()

    # Output JSON if requested
    if args.json:
        # Add computed values for the workflow
        metrics['stale_agents'] = metrics.get('agents', {}).get('stale', 0)
        metrics['health_score'] = metrics.get('health', {}).get('score', 0)
        print(json.dumps(metrics))
        return

    # Format report
    report = format_status_report(metrics)

    # Update status issue
    print("✏️  Updating status issue...")
    update_status_issue(issue_number, report, add_comment=not args.no_comment)

    print("✅ System status updated successfully!")

    # Print summary
    print_summary(metrics)

    print(f"\n🔗 View full status: gh issue view {issue_number}")


if __name__ == "__main__":
    main()
