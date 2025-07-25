"""
GitHub Integration Module
Handles GitHub CLI operations and label management
"""

import json
import subprocess
from pathlib import Path
from typing import List, Dict


class GitHubIntegration:
    """Manages GitHub integration including labels and CLI operations"""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def ensure_github_labels(self):
        """Ensure required GitHub labels exist"""
        print("\n🏷️  Ensuring GitHub labels exist...")

        labels = self._get_label_definitions()

        # Check if gh CLI is available
        if not self._check_github_cli():
            print("⚠️  GitHub CLI not found. Labels will need to be created manually.")
            print("   Install from: https://cli.github.com/")
            return

        # Check if we're authenticated
        if not self._check_github_auth():
            print(
                "⚠️  GitHub CLI not authenticated. "
                "Labels will need to be created manually."
            )
            print("   Run: gh auth login")
            return

        # Try to create labels
        created_count = self._create_labels(labels)

        if created_count > 0:
            print(f"✓ Created {created_count} GitHub labels")
        else:
            print("✓ All required labels already exist")

    def _get_label_definitions(self) -> List[Dict[str, str]]:
        """Get all label definitions"""
        return [
            {
                "name": "conductor:task",
                "color": "0e8a16",
                "description": "Tasks for AI agents",
            },
            {
                "name": "conductor:status",
                "color": "1d76db",
                "description": "System status tracking",
            },
            {
                "name": "conductor:in-progress",
                "color": "fbca04",
                "description": "Task being worked on",
            },
            {
                "name": "conductor:blocked",
                "color": "d93f0b",
                "description": "Task is blocked",
            },
            {
                "name": "conductor:archived",
                "color": "c5def5",
                "description": "Completed and archived",
            },
            {
                "name": "conductor:alert",
                "color": "e11d21",
                "description": "System health alert",
            },
            {
                "name": "conductor:init",
                "color": "7057ff",
                "description": "Initialization task for discovery",
            },
            {
                "name": "effort:small",
                "color": "76d7c4",
                "description": "Small effort task",
            },
            {
                "name": "effort:medium",
                "color": "f39c12",
                "description": "Medium effort task",
            },
            {
                "name": "effort:large",
                "color": "e74c3c",
                "description": "Large effort task",
            },
            {"name": "priority:low", "color": "c5def5", "description": "Low priority"},
            {
                "name": "priority:medium",
                "color": "fbca04",
                "description": "Medium priority",
            },
            {
                "name": "priority:high",
                "color": "e11d21",
                "description": "High priority",
            },
            {
                "name": "priority:critical",
                "color": "b60205",
                "description": "Critical priority - urgent",
            },
            {
                "name": "skill:frontend",
                "color": "7057ff",
                "description": "Frontend development",
            },
            {
                "name": "skill:backend",
                "color": "008672",
                "description": "Backend development",
            },
            {
                "name": "skill:devops",
                "color": "0052cc",
                "description": "DevOps and infrastructure",
            },
            {"name": "skill:ml", "color": "ff6b6b", "description": "Machine learning"},
            {
                "name": "skill:security",
                "color": "e11d21",
                "description": "Security tasks",
            },
            {
                "name": "skill:mobile",
                "color": "4e9a06",
                "description": "Mobile development",
            },
            {
                "name": "skill:data",
                "color": "c7def8",
                "description": "Data engineering",
            },
            {"name": "skill:design", "color": "fbca04", "description": "UI/UX design"},
        ]

    def _check_github_cli(self) -> bool:
        """Check if GitHub CLI is available"""
        try:
            subprocess.run(["gh", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _check_github_auth(self) -> bool:
        """Check if GitHub CLI is authenticated"""
        try:
            subprocess.run(["gh", "auth", "status"], capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def _create_labels(self, labels: List[Dict[str, str]]) -> int:
        """Create labels that don't exist"""
        created_count = 0

        # Get existing labels
        existing_labels = self._get_existing_labels()

        for label in labels:
            if label["name"] not in existing_labels:
                if self._create_single_label(label):
                    print(f"✓ Created label: {label['name']}")
                    created_count += 1

        return created_count

    def _get_existing_labels(self) -> List[str]:
        """Get list of existing label names"""
        try:
            result = subprocess.run(
                ["gh", "label", "list", "--json", "name"],
                capture_output=True,
                text=True,
                check=True,
            )
            labels_data = json.loads(result.stdout)
            return [label["name"] for label in labels_data]
        except Exception:
            return []

    def _create_single_label(self, label: Dict[str, str]) -> bool:
        """Create a single label"""
        try:
            subprocess.run(
                [
                    "gh",
                    "label",
                    "create",
                    label["name"],
                    "--color",
                    label["color"],
                    "--description",
                    label["description"],
                ],
                capture_output=True,
                check=True,
            )
            return True
        except Exception:
            # Silently continue if label creation fails
            return False
