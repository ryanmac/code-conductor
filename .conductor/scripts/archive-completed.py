#!/usr/bin/env python3
"""Archive completed tasks and clean up workflow state"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta


def load_state():
    """Load workflow state"""
    state_file = Path(".conductor/workflow-state.json")
    if not state_file.exists():
        print("❌ Workflow state file not found")
        sys.exit(1)

    try:
        with open(state_file, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("❌ Invalid workflow state file")
        sys.exit(1)


def save_state(state):
    """Save workflow state"""
    state_file = Path(".conductor/workflow-state.json")
    try:
        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"❌ Failed to save state: {e}")
        sys.exit(1)


def archive_completed_tasks(state, max_age_days=30):
    """Archive completed tasks older than max_age_days"""
    if "completed_work" not in state:
        state["completed_work"] = []

    current_time = datetime.utcnow()
    cutoff_date = current_time - timedelta(days=max_age_days)

    # Separate recent and old completed work
    recent_completed = []
    archived_count = 0

    for work in state["completed_work"]:
        completed_at_str = work.get("completed_at")
        if completed_at_str:
            try:
                completed_at = datetime.fromisoformat(
                    completed_at_str.replace("Z", "+00:00")
                )
                if completed_at >= cutoff_date:
                    recent_completed.append(work)
                else:
                    archived_count += 1
            except ValueError:
                # Keep items with invalid dates
                recent_completed.append(work)
        else:
            # Keep items without completion dates
            recent_completed.append(work)

    # Update completed work to only include recent items
    state["completed_work"] = recent_completed

    if archived_count > 0:
        print(
            f"📦 Archived {archived_count} completed task(s) older than {max_age_days} days"
        )
    else:
        print("ℹ️  No old completed tasks to archive")

    return archived_count


def clean_stale_active_work(state, stale_timeout_minutes=30):
    """Move stale active work to completed with appropriate status"""
    if "active_work" not in state:
        state["active_work"] = {}

    if "completed_work" not in state:
        state["completed_work"] = []

    current_time = datetime.utcnow()
    stale_cutoff = current_time - timedelta(minutes=stale_timeout_minutes)

    active_work = state["active_work"]
    stale_agents = []

    for agent_id, work in list(active_work.items()):
        heartbeat_str = work.get("heartbeat")
        if heartbeat_str:
            try:
                heartbeat = datetime.fromisoformat(heartbeat_str.replace("Z", "+00:00"))
                if heartbeat < stale_cutoff:
                    stale_agents.append(agent_id)
            except ValueError:
                # Consider items with invalid heartbeat as stale
                stale_agents.append(agent_id)
        else:
            # Consider items without heartbeat as stale
            stale_agents.append(agent_id)

    # Move stale work to completed
    cleaned_count = 0
    for agent_id in stale_agents:
        work = active_work.pop(agent_id)

        # Mark as abandoned
        work["status"] = "abandoned"
        work["completed_at"] = current_time.isoformat()
        work["abandonment_reason"] = "stale_heartbeat"

        state["completed_work"].append(work)
        cleaned_count += 1

    if cleaned_count > 0:
        print(f"🧹 Moved {cleaned_count} stale agent(s) to completed work")
    else:
        print("ℹ️  No stale active work found")

    return cleaned_count


def optimize_state_file(state):
    """Optimize state file by removing redundant data and organizing"""
    # Ensure all required sections exist
    if "active_work" not in state:
        state["active_work"] = {}
    if "available_tasks" not in state:
        state["available_tasks"] = []
    if "completed_work" not in state:
        state["completed_work"] = []
    if "system_status" not in state:
        state["system_status"] = {}

    # Sort tasks by creation date (newest first)
    for task_list in [state["available_tasks"], state["completed_work"]]:
        if isinstance(task_list, list):
            task_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    # Update system status
    state["system_status"]["last_cleanup"] = datetime.utcnow().isoformat()

    print("✨ Optimized state file structure")


def generate_cleanup_report(state, archived_count, cleaned_count):
    """Generate a summary report of cleanup actions"""
    print("\n📊 Cleanup Summary")
    print("=" * 30)

    current_metrics = {
        "active_agents": len(state.get("active_work", {})),
        "available_tasks": len(state.get("available_tasks", [])),
        "completed_tasks": len(state.get("completed_work", [])),
        "archived_tasks": archived_count,
        "cleaned_stale": cleaned_count,
    }

    for metric, value in current_metrics.items():
        print(f"{metric.replace('_', ' ').title()}: {value}")

    print(f"\nCleanup completed at: {datetime.utcnow().isoformat()}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Archive completed tasks and clean up state"
    )
    parser.add_argument(
        "--max-age",
        type=int,
        default=30,
        help="Maximum age in days for completed tasks (default: 30)",
    )
    parser.add_argument(
        "--stale-timeout",
        type=int,
        default=30,
        help="Stale timeout in minutes for active work (default: 30)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )

    args = parser.parse_args()

    print("🧹 Starting cleanup and archival process...")

    # Load current state
    state = load_state()

    if args.dry_run:
        print("(DRY RUN - no changes will be made)")

    # Archive old completed tasks
    archived_count = 0 if args.dry_run else archive_completed_tasks(state, args.max_age)

    # Clean stale active work
    cleaned_count = (
        0 if args.dry_run else clean_stale_active_work(state, args.stale_timeout)
    )

    # Optimize state file
    if not args.dry_run:
        optimize_state_file(state)
        save_state(state)

    # Generate report
    generate_cleanup_report(state, archived_count, cleaned_count)

    if args.dry_run:
        print("\nRun without --dry-run to perform cleanup")
    else:
        print("\n✅ Cleanup completed successfully")


if __name__ == "__main__":
    main()
