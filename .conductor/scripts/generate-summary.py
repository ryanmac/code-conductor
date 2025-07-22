#!/usr/bin/env python3
"""Generate GitHub Actions summary from workflow state"""

import json
from pathlib import Path


def load_state():
    """Load workflow state"""
    state_file = Path(".conductor/workflow-state.json")
    if not state_file.exists():
        print("No workflow state found")
        return {}

    try:
        with open(state_file, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("Invalid workflow state file")
        return {}


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
    state = load_state()

    if not state:
        print("## 🎼 Conductor-Score Status\n")
        print("⚠️ No system data available")
        return

    status = state.get("system_status", {})
    active_work = state.get("active_work", {})
    available_tasks = state.get("available_tasks", [])
    _ = state.get("completed_work", [])

    print("## 🎼 Conductor-Score System Status\n")

    # Overview metrics
    print("### 📊 Overview\n")
    print("| Metric | Value |")
    print("|--------|-------|")
    print(f"| Active Agents | {status.get('active_agents', 0)} |")
    print(f"| Available Tasks | {status.get('available_tasks', 0)} |")
    print(f"| Completed Tasks | {status.get('completed_tasks', 0)} |")
    print(f"| Health Score | {format_health_status(status.get('health_score', 0))} |")
    print(f"| Last Updated | {status.get('last_updated', 'Unknown')} |")
    print()

    # Active work breakdown
    if active_work:
        print("### 🤖 Active Agents\n")
        for agent_id, work in active_work.items():
            task = work.get("task", {})
            role = agent_id.split("_")[0] if "_" in agent_id else "unknown"
            task_title = task.get("title", "Unknown Task")
            effort = task.get("estimated_effort", "unknown")

            print(f"- **{role}**: {task_title} ({effort})")
        print()

    # Available tasks breakdown
    if available_tasks:
        print("### 📋 Available Tasks\n")

        # Group by effort
        tasks_by_effort = {}
        for task in available_tasks:
            effort = task.get("estimated_effort", "unknown")
            if effort not in tasks_by_effort:
                tasks_by_effort[effort] = []
            tasks_by_effort[effort].append(task)

        for effort in ["small", "medium", "large", "unknown"]:
            if effort in tasks_by_effort:
                print(f"#### {effort.title()} Tasks")
                for task in tasks_by_effort[effort]:
                    title = task.get("title", "Untitled")
                    skills = task.get("required_skills", [])
                    skill_text = f" ({', '.join(skills)})" if skills else " (general)"
                    print(f"- {title}{skill_text}")
                print()
    else:
        print("### 📋 Available Tasks\n")
        print(
            "No tasks available. Create tasks via GitHub Issues with `conductor:task` label.\n"
        )

    # Recent activity
    recent_completions = status.get("completions_24h", 0)
    if recent_completions > 0:
        print("### 🏆 Recent Activity\n")
        print(f"✅ {recent_completions} task(s) completed in the last 24 hours\n")

    # Health indicators
    health = status.get("health", {})
    if health:
        print("### 🏥 System Health\n")
        indicators = []
        if health.get("has_available_tasks"):
            indicators.append("✅ Tasks available")
        else:
            indicators.append("❌ No tasks available")

        if health.get("has_active_agents"):
            indicators.append("✅ Agents active")
        else:
            indicators.append("❌ No active agents")

        if health.get("low_stale_agents"):
            indicators.append("✅ Low stale agents")
        else:
            indicators.append("⚠️ High stale agents")

        if health.get("recent_activity"):
            indicators.append("✅ Recent activity")
        else:
            indicators.append("⚠️ No recent activity")

        for indicator in indicators:
            print(f"- {indicator}")
        print()

    # Warnings
    stale_agents = status.get("stale_agents", 0)
    if stale_agents > 0:
        print("### ⚠️ Warnings\n")
        print(f"- {stale_agents} stale agent(s) detected (cleanup recommended)\n")

    # Quick actions
    print("### 🚀 Quick Actions\n")
    if not available_tasks:
        print(
            "- [Create a new task](../../issues/new?labels=conductor:task&template=conductor-task.yml)"
        )
    if not active_work:
        print("- Launch an agent: `bash .conductor/scripts/bootstrap.sh dev`")
    if stale_agents > 0:
        print("- Clean up stale work: `python .conductor/scripts/cleanup-stale.py`")
    print()

    # Footer
    print("---")
    print("*Generated by Conductor-Score health monitoring*")


def main():
    generate_summary()


if __name__ == "__main__":
    main()
