"""
Setup Validation Module
Validates that the setup completed successfully
"""

import subprocess
from pathlib import Path
from typing import List, Tuple, Optional


class SetupValidator:
    """Validates Code Conductor setup"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.conductor_dir = project_root / ".conductor"

    def validate_setup(self) -> bool:
        """Validate the setup is correct"""
        print("\n✅ Validating setup...")

        checks = self._get_validation_checks()
        all_valid = True

        for file_path, description in checks:
            if file_path.exists():
                print(f"✓ {description} exists")
            else:
                print(f"✗ {description} missing")
                all_valid = False

        # Check GitHub CLI
        self._check_github_cli()

        return all_valid

    def _get_validation_checks(self) -> List[Tuple[Path, str]]:
        """Get list of files to validate"""
        return [
            (self.conductor_dir / "config.yaml", "Configuration file"),
            (self.conductor_dir / "scripts" / "conductor", "Conductor script"),
            (self.conductor_dir / "scripts" / "task-claim.py", "Task claim script"),
            (
                self.project_root / ".github" / "workflows" / "conductor.yml",
                "GitHub workflow",
            ),
            (
                self.project_root / ".github" / "ISSUE_TEMPLATE" / "conductor-task.yml",
                "GitHub issue template",
            ),
        ]

    def _check_github_cli(self):
        """Check GitHub CLI availability"""
        try:
            result = subprocess.run(["gh", "--version"], capture_output=True)
            if result.returncode == 0:
                print("✓ GitHub CLI installed")
            else:
                print("⚠️  GitHub CLI not found (optional but recommended)")
        except Exception:
            print("⚠️  GitHub CLI not found (optional but recommended)")

    def display_completion_message(self, discovery_task_number: Optional[str] = None):
        """Show completion message and next steps"""
        print("\n" + "=" * 50)
        print("🎉 Code Conductor Setup Complete!")
        print("=" * 50)

        # AI-First Quick Start
        print("\n🤖 AI Agent Quick Start")
        print("-" * 30)
        print("For Claude Code or other AI agents, simply run:")
        print()
        print("  ./conductor start [role]")
        print()
        print("This ONE command automatically:")
        print("  ✓ Shows role description")
        print("  ✓ Lists available tasks")
        print("  ✓ Claims best matching task")
        print("  ✓ Creates isolated workspace")
        print("  ✓ Provides all context needed")

        if discovery_task_number:
            self._display_discovery_task_message(discovery_task_number)
        else:
            self._display_general_startup_message()

        self._display_traditional_setup_steps()
        self._display_examples()
        self._display_key_files()

        print("\n🚀 Happy coding with Code Conductor!")

    def _display_discovery_task_message(self, discovery_task_number: str):
        """Display message when discovery task exists"""
        print()
        print(f"📚 First Task Available: #{discovery_task_number}")
        print(
            "This special task will help map your project and create all other tasks."
        )
        print()
        print("Suggested first agent prompt:")
        print("```")
        print("I'm a new agent in a Code Conductor project. Please help me:")
        print("1. Run './conductor status' to check system health")
        print("2. If tasks exist, run './conductor start dev' to claim one")
        print("3. If no tasks show, check 'gh issue list -l conductor:task' to debug")
        print("4. Review CLAUDE.md for my instructions")
        print("")
        print(f"I see initialization task #{discovery_task_number} is available.")
        print("```")

    def _display_general_startup_message(self):
        """Display general startup message"""
        print()
        print("🤖 Suggested AI agent prompt:")
        print("```")
        print("I'm a new agent in a Code Conductor project. Please help me:")
        print("1. Run './conductor status' to check system health")
        print("2. Run './conductor diagnose' if there are any issues")
        print("3. If tasks exist, run './conductor start dev' to claim one")
        print("4. If no tasks show, check 'gh issue list -l conductor:task' to debug")
        print("5. Review CLAUDE.md for my instructions")
        print("```")

    def _display_traditional_setup_steps(self):
        """Display traditional setup steps"""
        print("\n📋 Traditional Setup Steps:")
        print("1. Review the generated configuration in .conductor/config.yaml")
        print("2. Customize role definitions in .conductor/roles/ if needed")
        print("3. Commit these changes to your repository")
        print("4. Create tasks via GitHub issues with 'conductor:task' label")

    def _display_examples(self):
        """Display usage examples"""
        print("\n💡 Examples:")
        print("  # AI agent workflow:")
        print("  ./conductor start frontend    # Start as frontend agent")
        print("  cd worktrees/agent-frontend-123  # Enter workspace")
        print("  # ... implement feature ...")
        print("  ./conductor complete          # Finish and get next task")
        print()
        print("  # Create tasks manually:")
        print(
            "  gh issue create --label 'conductor:task' --title 'Implement user auth'"
        )

    def _display_key_files(self):
        """Display key files information"""
        print("\n📚 Key Files:")
        print("  - CLAUDE.md - AI agent instructions (auto-created)")
        print("  - .conductor/config.yaml - Main configuration")
        print("  - .conductor/roles/ - Role definitions")
        print("  - .conductor/scripts/conductor - Universal agent command")
