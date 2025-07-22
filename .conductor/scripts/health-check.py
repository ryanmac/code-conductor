#!/usr/bin/env python3
"""System health monitoring script"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path


class HealthChecker:
    def __init__(self):
        self.state_file = Path(".conductor/workflow-state.json")
        self.config_file = Path(".conductor/config.yaml")
        self.issues = []
        self.warnings = []

    def check_agent_heartbeats(self, state):
        """Check for stale agent heartbeats"""
        if "agent_settings" in state:
            timeout = state["agent_settings"].get("heartbeat_interval", 600) * 2
        else:
            timeout = 1200  # Default 20 minutes

        current_time = datetime.utcnow()
        stale_agents = []

        for agent_id, work in state.get("active_work", {}).items():
            heartbeat_str = work.get("heartbeat")
            if heartbeat_str:
                heartbeat = datetime.fromisoformat(heartbeat_str.replace('Z', '+00:00'))
                if (current_time - heartbeat).total_seconds() > timeout:
                    stale_agents.append({
                        "agent_id": agent_id,
                        "last_seen": heartbeat_str,
                        "task": work.get("task", {}).get("title", "Unknown")
                    })

        if stale_agents:
            self.issues.append({
                "type": "stale_agents",
                "severity": "warning",
                "agents": stale_agents
            })

        return len(stale_agents) == 0

    def check_blocked_tasks(self, state):
        """Check for tasks blocked too long"""
        blocked_threshold = timedelta(hours=4)
        current_time = datetime.utcnow()
        blocked_tasks = []

        for agent_id, work in state.get("active_work", {}).items():
            if work.get("status") == "blocked":
                started = work.get("started_at")
                if started:
                    started_time = datetime.fromisoformat(started.replace('Z', '+00:00'))
                    if current_time - started_time > blocked_threshold:
                        blocked_tasks.append({
                            "agent_id": agent_id,
                            "task": work.get("task", {}).get("title", "Unknown"),
                            "blocked_since": started
                        })

        if blocked_tasks:
            self.issues.append({
                "type": "blocked_tasks",
                "severity": "warning",
                "tasks": blocked_tasks
            })

        return len(blocked_tasks) == 0

    def check_task_queue_health(self, state):
        """Check if task queue is healthy"""
        available = len(state.get("available_tasks", []))
        active = len(state.get("active_work", {}))

        # Warning if too many tasks queued
        if available > 50:
            self.warnings.append(f"Large task queue: {available} tasks pending")

        # Warning if no tasks available but agents idle
        if available == 0 and active == 0:
            self.warnings.append("No tasks available and no active work")

        return True

    def check_file_conflicts(self, state):
        """Check for potential file conflicts"""
        file_locks = {}
        conflicts = []

        for agent_id, work in state.get("active_work", {}).items():
            locked_files = work.get("files_locked", [])
            for file in locked_files:
                if file in file_locks:
                    conflicts.append({
                        "file": file,
                        "agents": [file_locks[file], agent_id]
                    })
                else:
                    file_locks[file] = agent_id

        if conflicts:
            self.issues.append({
                "type": "file_conflicts",
                "severity": "error",
                "conflicts": conflicts
            })

        return len(conflicts) == 0

    def generate_report(self, state):
        """Generate health report"""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "healthy",
            "metrics": {
                "active_agents": len(state.get("active_work", {})),
                "available_tasks": len(state.get("available_tasks", [])),
                "completed_tasks": len(state.get("completed_work", [])),
            },
            "issues": self.issues,
            "warnings": self.warnings
        }

        if self.issues:
            report["status"] = "unhealthy" if any(
                i["severity"] == "error" for i in self.issues
            ) else "degraded"

        return report

    def run_checks(self):
        """Run all health checks"""
        if not self.state_file.exists():
            print("❌ State file not found")
            return False

        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)
        except Exception as e:
            print(f"❌ Failed to read state file: {e}")
            return False

        # Run all checks
        _ = [
            self.check_agent_heartbeats(state),
            self.check_blocked_tasks(state),
            self.check_task_queue_health(state),
            self.check_file_conflicts(state)
        ]

        # Generate and display report
        report = self.generate_report(state)

        print(f"🏥 System Health: {report['status'].upper()}")
        print("📊 Metrics:")
        print(f"  - Active Agents: {report['metrics']['active_agents']}")
        print(f"  - Available Tasks: {report['metrics']['available_tasks']}")
        print(f"  - Completed Tasks: {report['metrics']['completed_tasks']}")

        if report["issues"]:
            print("\n⚠️  Issues:")
            for issue in report["issues"]:
                print(f"  - {issue['type']}: {issue['severity']}")

        if report["warnings"]:
            print("\n💡 Warnings:")
            for warning in report["warnings"]:
                print(f"  - {warning}")

        # Update system status in state file
        state["system_status"]["health_check"] = report
        state["system_status"]["last_updated"] = datetime.utcnow().isoformat()

        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

        return report["status"] != "unhealthy"


def main():
    checker = HealthChecker()
    success = checker.run_checks()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
