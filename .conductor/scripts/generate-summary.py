#!/usr/bin/env python3
"""Generate GitHub Actions summary from GitHub Issues"""

import json
import subprocess
from datetime import datetime, timedelta
from collections import defaultdict


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
    except subprocess.CalledProcessError:
        return ""
    except FileNotFoundError:
        print("GitHub CLI (gh) not found. Please install it.")
        return ""


def get_all_conductor_issues():
    """Get all conductor-related issues"""
    output = run_gh_command([
        "issue", "list",
        "-l", "conductor:task",
        "--state", "all",
        "--limit", "1000",
        "--json", "number,title,body,labels,assignees,state,createdAt,updatedAt,comments"
    ])
    
    if not output:
        return []
    
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return []


def get_active_agents(issues):
    """Extract active agents from issue comments"""
    active_agents = {}
    now = datetime.utcnow()
    stale_threshold = now - timedelta(minutes=30)
    
    for issue in issues:
        if issue["state"] == "OPEN" and issue.get("assignees"):
            # Get recent comments to find agent metadata
            issue_number = issue["number"]
            comments_output = run_gh_command([
                "issue", "view", str(issue_number),
                "--json", "comments",
                "--jq", '.comments[-10:] | .[]'  # Get last 10 comments
            ])
            
            if comments_output:
                for line in comments_output.strip().split('\n'):
                    if line and "Agent Claimed Task" in line or "Heartbeat" in line:
                        try:
                            comment = json.loads(line)
                            comment_time = datetime.fromisoformat(
                                comment["createdAt"].replace("Z", "+00:00")
                            ).replace(tzinfo=None)
                            
                            if comment_time > stale_threshold:
                                # Parse agent metadata from comment
                                body = comment.get("body", "")
                                if "```json" in body:
                                    json_start = body.find("```json") + 7
                                    json_end = body.find("```", json_start)
                                    if json_end > json_start:
                                        try:
                                            metadata = json.loads(body[json_start:json_end])
                                            agent_id = metadata.get("agent_id")
                                            if agent_id:
                                                active_agents[agent_id] = {
                                                    "task": issue,
                                                    "metadata": metadata,
                                                    "last_heartbeat": comment_time
                                                }
                                        except json.JSONDecodeError:
                                            pass
                        except (json.JSONDecodeError, KeyError):
                            continue
    
    return active_agents


def calculate_health_score(metrics):
    """Calculate system health score"""
    score = 0.0
    weights = {
        "has_available_tasks": 0.3,
        "has_active_agents": 0.3,
        "low_stale_ratio": 0.2,
        "recent_activity": 0.2
    }
    
    if metrics["available_tasks"] > 0:
        score += weights["has_available_tasks"]
    
    if metrics["active_agents"] > 0:
        score += weights["has_active_agents"]
    
    # Stale ratio (lower is better)
    if metrics["active_agents"] > 0:
        stale_ratio = metrics["stale_agents"] / metrics["active_agents"]
        if stale_ratio < 0.2:  # Less than 20% stale
            score += weights["low_stale_ratio"]
    else:
        score += weights["low_stale_ratio"]  # No agents = no stale agents
    
    if metrics["completions_24h"] > 0:
        score += weights["recent_activity"]
    
    return score


def format_health_status(health_score):
    """Format health score with emoji"""
    if health_score >= 0.8:
        return f"🟢 Excellent ({health_score:.0%})"
    elif health_score >= 0.6:
        return f"🟡 Good ({health_score:.0%})"
    elif health_score >= 0.4:
        return f"🟠 Fair ({health_score:.0%})"
    else:
        return f"🔴 Needs Attention ({health_score:.0%})"


def generate_summary():
    """Generate markdown summary for GitHub Actions"""
    issues = get_all_conductor_issues()
    
    if not issues:
        print("## 🎼 Code-Conductor Status\n")
        print("⚠️ No conductor tasks found. Create tasks with `conductor:task` label.")
        return
    
    # Calculate metrics
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)
    
    available_tasks = [i for i in issues if i["state"] == "OPEN" and not i.get("assignees")]
    assigned_tasks = [i for i in issues if i["state"] == "OPEN" and i.get("assignees")]
    completed_tasks = [i for i in issues if i["state"] == "CLOSED"]
    
    # Get completions in last 24h
    recent_completions = [
        i for i in completed_tasks
        if datetime.fromisoformat(i["updatedAt"].replace("Z", "+00:00")).replace(tzinfo=None) > yesterday
    ]
    
    # Get active agents
    active_agents = get_active_agents(assigned_tasks)
    stale_agents = sum(
        1 for a in active_agents.values()
        if (now - a["last_heartbeat"]).total_seconds() > 1800  # 30 minutes
    )
    
    metrics = {
        "available_tasks": len(available_tasks),
        "active_agents": len(active_agents),
        "completed_tasks": len(completed_tasks),
        "completions_24h": len(recent_completions),
        "stale_agents": stale_agents
    }
    
    health_score = calculate_health_score(metrics)
    
    print("## 🎼 Code-Conductor System Status\n")
    
    # Overview metrics
    print("### 📊 Overview\n")
    print("| Metric | Value |")
    print("|--------|-------|")
    print(f"| Active Agents | {metrics['active_agents']} |")
    print(f"| Available Tasks | {metrics['available_tasks']} |")
    print(f"| Completed Tasks | {metrics['completed_tasks']} |")
    print(f"| Health Score | {format_health_status(health_score)} |")
    print(f"| Last Updated | {now.strftime('%Y-%m-%d %H:%M:%S UTC')} |")
    print()
    
    # Active work breakdown
    if active_agents:
        print("### 🤖 Active Agents\n")
        for agent_id, agent_data in active_agents.items():
            task = agent_data["task"]
            metadata = agent_data["metadata"]
            role = metadata.get("role", "unknown")
            task_title = task.get("title", "Unknown Task")
            
            # Get effort from labels
            effort = "unknown"
            for label in task.get("labels", []):
                if label["name"].startswith("effort:"):
                    effort = label["name"].replace("effort:", "")
                    break
            
            print(f"- **{role}**: {task_title} ({effort})")
        print()
    
    # Available tasks breakdown
    if available_tasks:
        print("### 📋 Available Tasks\n")
        
        # Group by effort
        tasks_by_effort = defaultdict(list)
        for task in available_tasks:
            effort = "unknown"
            for label in task.get("labels", []):
                if label["name"].startswith("effort:"):
                    effort = label["name"].replace("effort:", "")
                    break
            tasks_by_effort[effort].append(task)
        
        for effort in ["small", "medium", "large", "unknown"]:
            if effort in tasks_by_effort:
                print(f"#### {effort.title()} Tasks")
                for task in tasks_by_effort[effort]:
                    title = task.get("title", "Untitled")
                    skills = []
                    for label in task.get("labels", []):
                        if label["name"].startswith("skill:"):
                            skills.append(label["name"].replace("skill:", ""))
                    skill_text = f" ({', '.join(skills)})" if skills else " (general)"
                    print(f"- {title}{skill_text}")
                print()
    else:
        print("### 📋 Available Tasks\n")
        print("No tasks available. Create tasks via GitHub Issues with `conductor:task` label.\n")
    
    # Recent activity
    if metrics["completions_24h"] > 0:
        print("### 🏆 Recent Activity\n")
        print(f"✅ {metrics['completions_24h']} task(s) completed in the last 24 hours\n")
    
    # Health indicators
    print("### 🏥 System Health\n")
    indicators = []
    
    if metrics["available_tasks"] > 0:
        indicators.append("✅ Tasks available")
    else:
        indicators.append("❌ No tasks available")
    
    if metrics["active_agents"] > 0:
        indicators.append("✅ Agents active")
    else:
        indicators.append("❌ No active agents")
    
    if metrics["active_agents"] == 0 or stale_agents < metrics["active_agents"] * 0.5:
        indicators.append("✅ Low stale agents")
    else:
        indicators.append("⚠️ High stale agents")
    
    if metrics["completions_24h"] > 0:
        indicators.append("✅ Recent activity")
    else:
        indicators.append("⚠️ No recent activity")
    
    for indicator in indicators:
        print(f"- {indicator}")
    print()
    
    # Warnings
    if stale_agents > 0:
        print("### ⚠️ Warnings\n")
        print(f"- {stale_agents} stale agent(s) detected (cleanup recommended)\n")
    
    # Quick actions
    print("### 🚀 Quick Actions\n")
    if not available_tasks:
        print("- [Create a new task](../../issues/new?labels=conductor:task&template=conductor-task.yml)")
    if not active_agents:
        print("- Launch an agent: `bash .conductor/scripts/bootstrap.sh dev`")
    if stale_agents > 0:
        print("- Clean up stale work: `python .conductor/scripts/cleanup-stale.py`")
    print()
    
    # Footer
    print("---")
    print("*Generated by Code-Conductor health monitoring*")


def main():
    generate_summary()


if __name__ == "__main__":
    main()