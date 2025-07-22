#!/usr/bin/env python3
"""Claim and assign tasks to agents"""

import json
import os
import sys
import uuid
import argparse
from pathlib import Path
from datetime import datetime


def load_state():
    """Load workflow state"""
    state_file = Path('.conductor/workflow-state.json')
    if not state_file.exists():
        print('{"status": "ERROR", "message": "Workflow state file not found"}')
        sys.exit(1)

    try:
        with open(state_file, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print('{"status": "ERROR", "message": "Invalid workflow state file"}')
        sys.exit(1)


def save_state(state):
    """Save workflow state with atomic write"""
    state_file = Path('.conductor/workflow-state.json')
    try:
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
    except Exception as e:
        print(f'{{"status": "ERROR", "message": "Failed to save state: {e}"}}')
        sys.exit(1)


def find_suitable_task(state, role):
    """Find a task suitable for the given role"""
    available_tasks = state.get('available_tasks', [])

    if not available_tasks:
        return None

    # Try to find tasks that match the role's skills
    role_tasks = []
    general_tasks = []

    for task in available_tasks:
        required_skills = task.get('required_skills', [])

        # If no specific skills required, it's a general task
        if not required_skills:
            general_tasks.append(task)
        # If role matches required skills
        elif role in required_skills:
            role_tasks.append(task)
        # Special mapping for common roles
        elif role == 'dev' and not required_skills:
            general_tasks.append(task)

    # Prefer tasks that specifically need this role
    if role_tasks:
        # Sort by effort (small tasks first)
        effort_order = {'small': 1, 'medium': 2, 'large': 3}
        role_tasks.sort(key=lambda x: effort_order.get(x.get('estimated_effort', 'medium'), 2))
        return role_tasks[0]

    # Fall back to general tasks if we're a dev role
    if general_tasks and role == 'dev':
        effort_order = {'small': 1, 'medium': 2, 'large': 3}
        general_tasks.sort(key=lambda x: effort_order.get(x.get('estimated_effort', 'medium'), 2))
        return general_tasks[0]

    return None


def claim_task(state, task, role):
    """Claim a task for an agent"""
    if 'active_work' not in state:
        state['active_work'] = {}

    # Generate agent ID
    agent_id = f"{role}_{uuid.uuid4().hex[:8]}"
    current_time = datetime.utcnow().isoformat()

    # Create work entry
    work_entry = {
        'agent_id': agent_id,
        'role': role,
        'task': task.copy(),
        'status': 'claimed',
        'claimed_at': current_time,
        'heartbeat': current_time,
        'worktree_path': f"./worktrees/agent-{role}-{task['id']}"
    }

    # Add to active work
    state['active_work'][agent_id] = work_entry

    # Remove from available tasks
    state['available_tasks'] = [t for t in state['available_tasks'] if t['id'] != task['id']]

    # Update system status
    if 'system_status' not in state:
        state['system_status'] = {}
    state['system_status']['last_updated'] = current_time

    return agent_id, work_entry


def main():
    parser = argparse.ArgumentParser(description="Claim a task for an agent")
    parser.add_argument("--role", required=True, help="Agent role (dev, devops, security, etc.)")
    parser.add_argument("--task-id", help="Specific task ID to claim (optional)")
    parser.add_argument("--json", action="store_true", help="Output JSON format")

    args = parser.parse_args()

    # Load current state
    state = load_state()

    # Check if specific task requested
    if args.task_id:
        # Find specific task
        target_task = None
        for task in state.get('available_tasks', []):
            if task['id'] == args.task_id:
                target_task = task
                break

        if not target_task:
            result = {
                "status": "ERROR",
                "message": f"Task {args.task_id} not found or already claimed"
            }
            print(json.dumps(result))
            sys.exit(1)
    else:
        # Find suitable task automatically
        target_task = find_suitable_task(state, args.role)

    if not target_task:
        result = {"status": "IDLE", "message": f"No tasks available for role: {args.role}"}
        print(json.dumps(result))
        sys.exit(0)

    # Claim the task
    try:
        agent_id, work_entry = claim_task(state, target_task, args.role)
        save_state(state)

        result = {
            "status": "claimed",
            "agent_id": agent_id,
            "task_id": target_task['id'],
            "task": target_task,
            "worktree_path": work_entry['worktree_path'],
            "claimed_at": work_entry['claimed_at']
        }
        print(json.dumps(result))

    except Exception as e:
        result = {
            "status": "ERROR",
            "message": f"Failed to claim task: {e}"
        }
        print(json.dumps(result))
        sys.exit(1)


if __name__ == "__main__":
    main()
