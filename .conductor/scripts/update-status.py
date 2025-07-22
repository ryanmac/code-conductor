#!/usr/bin/env python3
"""Update system status in workflow state"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta


def load_state():
    """Load workflow state"""
    state_file = Path('.conductor/workflow-state.json')
    if not state_file.exists():
        print("❌ Workflow state file not found")
        sys.exit(1)

    try:
        with open(state_file, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("❌ Invalid workflow state file")
        sys.exit(1)


def save_state(state):
    """Save workflow state"""
    state_file = Path('.conductor/workflow-state.json')
    try:
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"❌ Failed to save state: {e}")
        sys.exit(1)


def update_system_status(state):
    """Update system status with current metrics"""
    if 'system_status' not in state:
        state['system_status'] = {}

    status = state['system_status']
    current_time = datetime.utcnow()

    # Count active and idle agents
    active_work = state.get('active_work', {})
    status['active_agents'] = len(active_work)

    # Count agents by status
    agents_by_status = {}
    stale_agents = []
    idle_timeout = 1800  # 30 minutes default

    for agent_id, work in active_work.items():
        work_status = work.get('status', 'unknown')
        agents_by_status[work_status] = agents_by_status.get(work_status, 0) + 1

        # Check for stale agents
        heartbeat_str = work.get('heartbeat')
        if heartbeat_str:
            try:
                heartbeat = datetime.fromisoformat(heartbeat_str.replace('Z', '+00:00'))
                if (current_time - heartbeat).total_seconds() > idle_timeout:
                    stale_agents.append(agent_id)
            except ValueError:
                pass

    status['agents_by_status'] = agents_by_status
    status['stale_agents'] = len(stale_agents)

    # Count available tasks
    available_tasks = state.get('available_tasks', [])
    status['available_tasks'] = len(available_tasks)

    # Count tasks by effort
    tasks_by_effort = {}
    tasks_by_skills = {}

    for task in available_tasks:
        effort = task.get('estimated_effort', 'unknown')
        tasks_by_effort[effort] = tasks_by_effort.get(effort, 0) + 1

        skills = task.get('required_skills', [])
        if not skills:
            tasks_by_skills['general'] = tasks_by_skills.get('general', 0) + 1
        else:
            for skill in skills:
                tasks_by_skills[skill] = tasks_by_skills.get(skill, 0) + 1

    status['tasks_by_effort'] = tasks_by_effort
    status['tasks_by_skills'] = tasks_by_skills

    # Count completed work
    completed_work = state.get('completed_work', [])
    status['completed_tasks'] = len(completed_work)

    # Calculate completion rate (last 24 hours)
    day_ago = current_time - timedelta(days=1)
    recent_completions = 0

    for work in completed_work:
        completed_at_str = work.get('completed_at')
        if completed_at_str:
            try:
                completed_at = datetime.fromisoformat(completed_at_str.replace('Z', '+00:00'))
                if completed_at >= day_ago:
                    recent_completions += 1
            except ValueError:
                pass

    status['completions_24h'] = recent_completions

    # System health indicators
    status['health'] = {
        'has_available_tasks': len(available_tasks) > 0,
        'has_active_agents': len(active_work) > 0,
        'low_stale_agents': len(stale_agents) < len(active_work) * 0.3,  # Less than 30% stale
        'recent_activity': recent_completions > 0 or len(active_work) > 0
    }

    # Overall health score
    health_checks = list(status['health'].values())
    health_score = sum(health_checks) / len(health_checks) if health_checks else 0
    status['health_score'] = round(health_score, 2)

    # Update timestamp
    status['last_updated'] = current_time.isoformat()

    return status


def print_status_summary(status):
    """Print a human-readable status summary"""
    print("📊 System Status Summary")
    print("=" * 30)
    print(f"Active Agents: {status.get('active_agents', 0)}")
    print(f"Available Tasks: {status.get('available_tasks', 0)}")
    print(f"Completed (24h): {status.get('completions_24h', 0)}")
    print(f"Health Score: {status.get('health_score', 0):.0%}")

    if status.get('stale_agents', 0) > 0:
        print(f"⚠️  Stale Agents: {status['stale_agents']}")

    # Tasks breakdown
    tasks_by_effort = status.get('tasks_by_effort', {})
    if tasks_by_effort:
        print("\nTasks by Effort:")
        for effort, count in tasks_by_effort.items():
            print(f"  {effort}: {count}")

    # Skills breakdown
    tasks_by_skills = status.get('tasks_by_skills', {})
    if tasks_by_skills:
        print("\nTasks by Skills:")
        for skill, count in tasks_by_skills.items():
            print(f"  {skill}: {count}")

    print(f"\nLast Updated: {status.get('last_updated', 'Unknown')}")


def main():
    print("🔄 Updating system status...")

    # Load current state
    state = load_state()

    # Update status
    updated_status = update_system_status(state)

    # Save state
    save_state(state)

    print("✅ System status updated")

    # Print summary
    print_status_summary(updated_status)


if __name__ == "__main__":
    main()
