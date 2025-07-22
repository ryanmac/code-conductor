#!/usr/bin/env python3
"""Check system dependencies before claiming tasks"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path


class DependencyChecker:
    def __init__(self):
        self.results = {
            "status": "UNKNOWN",
            "checks_performed": [],
            "dependencies_satisfied": [],
            "blockers": [],
            "timestamp": datetime.utcnow().isoformat(),
        }

    def check_github_api_status(self):
        """Verify GitHub API connectivity"""
        try:
            result = subprocess.run(
                ["gh", "api", "user"], capture_output=True, text=True
            )
            if result.returncode == 0:
                self.results["dependencies_satisfied"].append("GitHub API accessible")
                return True
            else:
                self.results["blockers"].append(
                    "GitHub API authentication failed - run 'gh auth login'"
                )
                return False
        except FileNotFoundError:
            self.results["blockers"].append(
                "GitHub CLI not installed - visit https://cli.github.com"
            )
            return False
        except Exception as e:
            self.results["blockers"].append(f"GitHub CLI error: {e}")
            return False

    def check_git_status(self):
        """Check git repository status"""
        try:
            # Check if we're in a git repo
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"], capture_output=True, text=True
            )
            if result.returncode != 0:
                self.results["blockers"].append("Not in a git repository")
                return False

            # Check for uncommitted changes
            result = subprocess.run(
                ["git", "status", "--porcelain"], capture_output=True, text=True
            )
            if result.stdout.strip():
                self.results["blockers"].append(
                    "Uncommitted changes detected - commit or stash first"
                )
                return False

            self.results["dependencies_satisfied"].append("Git repository clean")
            return True

        except Exception as e:
            self.results["blockers"].append(f"Git check failed: {e}")
            return False

    def check_worktree_support(self):
        """Verify git worktree support"""
        try:
            result = subprocess.run(
                ["git", "worktree", "list"], capture_output=True, text=True
            )
            if result.returncode == 0:
                self.results["dependencies_satisfied"].append(
                    "Git worktree support available"
                )
                return True
            else:
                self.results["blockers"].append("Git worktree not supported")
                return False
        except Exception as e:
            self.results["blockers"].append(f"Worktree check failed: {e}")
            return False

    def check_python_dependencies(self):
        """Check required Python packages"""
        required_packages = ["yaml"]
        missing = []

        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing.append(package)

        if missing:
            self.results["blockers"].append(
                f"Missing Python packages: {', '.join(missing)} - run 'pip install pyyaml'"
            )
            return False
        else:
            self.results["dependencies_satisfied"].append(
                "Python dependencies satisfied"
            )
            return True

    def check_conductor_config(self):
        """Verify conductor configuration exists"""
        config_file = Path(".conductor/config.yaml")
        if not config_file.exists():
            self.results["blockers"].append(
                "Conductor not configured - run 'python setup.py'"
            )
            return False

        self.results["dependencies_satisfied"].append("Conductor configuration found")
        return True

    def run_all_checks(self):
        """Execute all dependency checks"""
        checks = [
            ("Conductor Config", self.check_conductor_config),
            ("Git Status", self.check_git_status),
            ("Git Worktree", self.check_worktree_support),
            ("Python Dependencies", self.check_python_dependencies),
            ("GitHub API", self.check_github_api_status),
        ]

        all_passed = True
        for check_name, check_func in checks:
            self.results["checks_performed"].append(check_name)
            passed = check_func()
            all_passed = all_passed and passed

        self.results["status"] = "READY" if all_passed else "BLOCKED"
        return self.results


def main():
    checker = DependencyChecker()
    result = checker.run_all_checks()

    # Display results
    print(f"Dependency Check: {result['status']}")
    print()

    if result["dependencies_satisfied"]:
        print("✅ Satisfied:")
        for item in result["dependencies_satisfied"]:
            print(f"  - {item}")
        print()

    if result["blockers"]:
        print("❌ Blockers:")
        for item in result["blockers"]:
            print(f"  - {item}")
        print()

    # Exit with appropriate code
    sys.exit(0 if result["status"] == "READY" else 1)


if __name__ == "__main__":
    main()
