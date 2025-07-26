#!/usr/bin/env python3
"""
Code Conductor Uninstall Script

Safely removes Code Conductor from a project, preserving user files.
"""

import sys
import shutil
import argparse
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional
import re

# ANSI color codes for better UX
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"


class ConductorUninstaller:
    """Handles the removal of Code Conductor from a project."""

    def __init__(
        self, force: bool = False, dry_run: bool = False, verbose: bool = False
    ):
        self.force = force
        self.dry_run = dry_run
        self.verbose = verbose
        self.project_root = Path.cwd()
        self.items_to_remove = []
        self.warnings = []

    def log(self, message: str, color: str = ""):
        """Print a message with optional color."""
        print(f"{color}{message}{RESET}")

    def log_verbose(self, message: str):
        """Print verbose output if enabled."""
        if self.verbose:
            self.log(f"  {message}", BLUE)

    def check_git_repo(self) -> bool:
        """Check if we're in a git repository."""
        try:
            subprocess.run(
                ["git", "rev-parse", "--git-dir"], capture_output=True, check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def find_conductor_files(self) -> List[Tuple[Path, str]]:
        """Find all Code Conductor files and directories."""
        items = []

        # Core conductor directory
        conductor_dir = self.project_root / ".conductor"
        if conductor_dir.exists():
            items.append((conductor_dir, "Core configuration directory"))

        # Conductor wrapper script
        conductor_script = self.project_root / "conductor"
        if conductor_script.exists():
            items.append((conductor_script, "Conductor wrapper script"))

        # GitHub workflows
        workflows_dir = self.project_root / ".github" / "workflows"
        if workflows_dir.exists():
            conductor_workflows = [
                "conductor.yml",
                "conductor-cleanup.yml",
                "pr-review.yml",
            ]
            for workflow in conductor_workflows:
                workflow_path = workflows_dir / workflow
                if workflow_path.exists():
                    items.append((workflow_path, f"GitHub workflow: {workflow}"))

        # GitHub issue template
        template_path = (
            self.project_root / ".github" / "ISSUE_TEMPLATE" / "conductor-task.yml"
        )
        if template_path.exists():
            items.append((template_path, "Conductor task issue template"))

        # Worktrees directory
        worktrees_dir = self.project_root / "worktrees"
        if worktrees_dir.exists():
            # Check if it contains conductor worktrees
            conductor_worktrees = list(worktrees_dir.glob("agent-*"))
            if conductor_worktrees:
                items.append(
                    (
                        worktrees_dir,
                        f"Worktrees directory "
                        f"({len(conductor_worktrees)} agent worktrees)",
                    )
                )

        return items

    def find_claude_md_section(self) -> Optional[Path]:
        """Check if CLAUDE.md has conductor section."""
        claude_md = self.project_root / "CLAUDE.md"
        if claude_md.exists():
            content = claude_md.read_text()
            if (
                "<!-- CONDUCTOR:START -->" in content
                and "<!-- CONDUCTOR:END -->" in content
            ):
                return claude_md
        return None

    def list_git_worktrees(self) -> List[str]:
        """List all git worktrees created by conductor."""
        try:
            result = subprocess.run(
                ["git", "worktree", "list", "--porcelain"],
                capture_output=True,
                text=True,
                check=True,
            )
            worktrees = []
            lines = result.stdout.strip().split("\n")

            i = 0
            while i < len(lines):
                if lines[i].startswith("worktree "):
                    path = lines[i].split(" ", 1)[1]
                    if "/worktrees/agent-" in path:
                        worktrees.append(path)
                i += 1

            return worktrees
        except subprocess.CalledProcessError:
            return []

    def remove_git_worktree(self, path: str) -> bool:
        """Remove a git worktree safely."""
        try:
            self.log_verbose(f"Removing git worktree: {path}")
            subprocess.run(
                ["git", "worktree", "remove", path, "--force"],
                capture_output=True,
                check=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            self.warnings.append(f"Failed to remove worktree {path}: {e}")
            return False

    def remove_claude_md_section(self, path: Path) -> bool:
        """Remove conductor section from CLAUDE.md."""
        try:
            content = path.read_text()
            pattern = r"<!-- CONDUCTOR:START -->.*?<!-- CONDUCTOR:END -->"
            new_content = re.sub(pattern, "", content, flags=re.DOTALL)

            # Clean up extra newlines
            new_content = re.sub(r"\n{3,}", "\n\n", new_content)

            if self.dry_run:
                self.log_verbose("Would update CLAUDE.md to remove conductor section")
            else:
                path.write_text(new_content)
                self.log_verbose("Updated CLAUDE.md to remove conductor section")
            return True
        except Exception as e:
            self.warnings.append(f"Failed to update CLAUDE.md: {e}")
            return False

    def check_github_items(self) -> Tuple[int, int]:
        """Check for GitHub issues and labels (requires gh CLI)."""
        issues_count = 0
        labels = []

        try:
            # Check for conductor issues
            result = subprocess.run(
                [
                    "gh",
                    "issue",
                    "list",
                    "--label",
                    "conductor:task",
                    "--state",
                    "open",
                    "--json",
                    "number",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            import json

            issues = json.loads(result.stdout)
            issues_count = len(issues)

            # Check for conductor labels
            result = subprocess.run(
                ["gh", "label", "list", "--json", "name"],
                capture_output=True,
                text=True,
                check=True,
            )
            all_labels = json.loads(result.stdout)
            conductor_labels = [
                label["name"]
                for label in all_labels
                if label["name"].startswith("conductor:")
            ]
            labels = conductor_labels

        except (subprocess.CalledProcessError, ImportError, KeyError):
            # gh CLI not available or command failed
            pass

        return issues_count, len(labels)

    def confirm_removal(self) -> bool:
        """Ask user to confirm removal."""
        print(f"\n{BOLD}Code Conductor Uninstall Summary{RESET}")
        print("=" * 50)

        if not self.items_to_remove:
            self.log("No Code Conductor files found to remove.", GREEN)
            return False

        print(f"\n{BOLD}Files and directories to be removed:{RESET}")
        for item, description in self.items_to_remove:
            print(f"  • {item.relative_to(self.project_root)} - {description}")

        # Check for git worktrees
        worktrees = self.list_git_worktrees()
        if worktrees:
            print(f"\n{BOLD}Git worktrees to be removed:{RESET}")
            for worktree in worktrees:
                print(f"  • {worktree}")

        # Check for CLAUDE.md section
        claude_md = self.find_claude_md_section()
        if claude_md:
            print(f"\n{BOLD}Files to be modified:{RESET}")
            print("  • CLAUDE.md - Remove conductor section")

        # Check GitHub items
        issues_count, labels_count = self.check_github_items()
        if issues_count > 0 or labels_count > 0:
            print(f"\n{BOLD}GitHub items (for information only):{RESET}")
            if issues_count > 0:
                print(f"  • {issues_count} open conductor task issues")
            if labels_count > 0:
                print(f"  • {labels_count} conductor labels")
            print(
                f"  {YELLOW}Note: GitHub items must be cleaned up "
                f"manually if desired{RESET}"
            )

        if self.dry_run:
            print(f"\n{YELLOW}DRY RUN: No files will be removed{RESET}")
            return False

        if self.force:
            return True

        print(f"\n{YELLOW}This action cannot be undone!{RESET}")
        response = input(
            f"\n{BOLD}Remove Code Conductor from this project? [y/N]:{RESET} "
        )
        return response.lower() in ["y", "yes"]

    def remove_items(self) -> bool:
        """Remove all conductor files and directories."""
        success = True

        # Remove git worktrees first
        worktrees = self.list_git_worktrees()
        for worktree in worktrees:
            if not self.dry_run:
                if not self.remove_git_worktree(worktree):
                    success = False

        # Remove files and directories
        for item, description in self.items_to_remove:
            try:
                if self.dry_run:
                    self.log(
                        f"Would remove: {item.relative_to(self.project_root)}", BLUE
                    )
                else:
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
                    self.log(f"Removed: {item.relative_to(self.project_root)}", GREEN)
            except Exception as e:
                self.log(f"Failed to remove {item}: {e}", RED)
                success = False

        # Update CLAUDE.md
        claude_md = self.find_claude_md_section()
        if claude_md and not self.dry_run:
            if not self.remove_claude_md_section(claude_md):
                success = False

        return success

    def cleanup_empty_dirs(self):
        """Remove empty directories left behind."""
        dirs_to_check = [
            self.project_root / ".github" / "ISSUE_TEMPLATE",
            self.project_root / ".github" / "workflows",
            self.project_root / ".github",
        ]

        for dir_path in dirs_to_check:
            if dir_path.exists() and not any(dir_path.iterdir()):
                try:
                    if not self.dry_run:
                        dir_path.rmdir()
                        self.log_verbose(
                            f"Removed empty directory: "
                            f"{dir_path.relative_to(self.project_root)}"
                        )
                except Exception:
                    pass

    def run(self) -> int:
        """Run the uninstall process."""
        print(f"{BOLD}Code Conductor Uninstaller{RESET}")
        print("=" * 50)

        # Check if we're in a git repo
        if not self.check_git_repo():
            self.log(
                "Warning: Not in a git repository. Some features may not work.", YELLOW
            )

        # Find all conductor files
        self.items_to_remove = self.find_conductor_files()

        # Confirm removal
        if not self.confirm_removal():
            self.log("\nUninstall cancelled.", YELLOW)
            return 0

        # Remove items
        print(f"\n{BOLD}Removing Code Conductor...{RESET}")
        if self.remove_items():
            self.cleanup_empty_dirs()

            if not self.dry_run:
                self.log(
                    f"\n{GREEN}✓ Code Conductor has been successfully "
                    f"removed from your project!{RESET}"
                )

                # Post-removal instructions
                print(f"\n{BOLD}Post-removal notes:{RESET}")
                print("• Any open conductor task issues remain in GitHub")
                print(
                    "• Conductor labels remain in GitHub (remove manually if desired)"
                )
                print("• Any active conductor branches should be cleaned up manually")

                if self.warnings:
                    print(f"\n{YELLOW}Warnings:{RESET}")
                    for warning in self.warnings:
                        print(f"  • {warning}")
        else:
            self.log(
                f"\n{RED}Some items could not be removed. "
                f"Please check the errors above.{RESET}",
                RED,
            )
            return 1

        return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Safely remove Code Conductor from a project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python uninstall.py              # Interactive removal
  python uninstall.py --force      # Remove without confirmation
  python uninstall.py --dry-run    # Show what would be removed
  python uninstall.py --verbose    # Show detailed output
        """,
    )

    parser.add_argument(
        "--force", "-f", action="store_true", help="Remove without confirmation prompt"
    )

    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Show what would be removed without actually removing",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed output"
    )

    args = parser.parse_args()

    # Create and run uninstaller
    uninstaller = ConductorUninstaller(
        force=args.force, dry_run=args.dry_run, verbose=args.verbose
    )

    try:
        return uninstaller.run()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Uninstall cancelled by user.{RESET}")
        return 1
    except Exception as e:
        print(f"\n{RED}Error: {e}{RESET}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
