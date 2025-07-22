#!/usr/bin/env python3
"""Clean up stale work and abandoned tasks"""

import json
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path


class StaleCleaner:
    def __init__(self, timeout_minutes=30):
        self.state_file = Path(".conductor/workflow-state.json")
        self.timeout = timedelta(minutes=timeout_minutes)
        self.cleaned_agents = []

    def clean_stale_work(self):
        """Remove stale agent work"""
        if not self.state_file.exists():
            print("❌ State file not found")
            return False

        try:
            with open(self.state_file, "r") as f:
                state = json.load(f)
        except Exception as e:
            print(f"❌ Failed to read state file: {e}")
            return False

        current_time = datetime.utcnow()
        active_work = state.get("active_work", {})
        available_tasks = state.get("available_tasks", [])

        # Find stale agents
        agents_to_remove = []
        for agent_id, work in active_work.items():
            heartbeat_str = work.get("heartbeat")
            if heartbeat_str:
                heartbeat = datetime.fromisoformat(heartbeat_str.replace("Z", "+00:00"))
                if current_time - heartbeat > self.timeout:
                    agents_to_remove.append(agent_id)

        # Clean up stale agents
        for agent_id in agents_to_remove:
            work = active_work[agent_id]
            task = work.get("task")

            # Return task to available queue
            if task and task not in available_tasks:
                # Reset task status
                task["returned_at"] = current_time.isoformat()
                task["previous_agent"] = agent_id
                available_tasks.append(task)

            # Remove agent work
            del active_work[agent_id]
            self.cleaned_agents.append(
                {
                    "agent_id": agent_id,
                    "task": task.get("title") if task else "Unknown",
                    "last_heartbeat": work.get("heartbeat"),
                }
            )

        # Update state
        if agents_to_remove:
            state["available_tasks"] = available_tasks
            state["active_work"] = active_work
            state["system_status"]["active_agents"] = len(active_work)
            state["system_status"]["last_cleanup"] = current_time.isoformat()

            # Write back
            with open(self.state_file, "w") as f:
                json.dump(state, f, indent=2)

            print(f"🧹 Cleaned up {len(agents_to_remove)} stale agents")
            for agent in self.cleaned_agents:
                print(f"  - {agent['agent_id']}: {agent['task']}")
        else:
            print("✅ No stale agents found")

        return True

    def clean_old_completed(self, days=7):
        """Archive old completed tasks"""
        try:
            with open(self.state_file, "r") as f:
                state = json.load(f)
        except Exception as e:
            print(f"❌ Failed to read state file: {e}")
            return False

        completed = state.get("completed_work", [])
        if isinstance(completed, list) and len(completed) > 100:
            # Keep only recent 100 completed tasks
            state["completed_work"] = completed[-100:]

            with open(self.state_file, "w") as f:
                json.dump(state, f, indent=2)

            print(f"📦 Archived {len(completed) - 100} old completed tasks")

        return True


def main():
    parser = argparse.ArgumentParser(description="Clean up stale conductor work")
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Timeout in minutes for stale agents (default: 30)",
    )
    parser.add_argument(
        "--archive-days",
        type=int,
        default=7,
        help="Days to keep completed tasks (default: 7)",
    )

    args = parser.parse_args()

    cleaner = StaleCleaner(timeout_minutes=args.timeout)

    # Run cleanup
    success = cleaner.clean_stale_work()
    if success:
        cleaner.clean_old_completed(days=args.archive_days)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
