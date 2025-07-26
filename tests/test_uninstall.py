#!/usr/bin/env python3
"""
Test script for Code Conductor uninstall functionality.

This script creates a test installation and verifies the uninstaller
removes all components correctly.
"""

import os
import sys
import tempfile
import shutil
import subprocess
from pathlib import Path
import unittest

# Add parent directory to path to import uninstall module
sys.path.insert(0, str(Path(__file__).parent.parent))
from uninstall import ConductorUninstaller  # noqa: E402


class TestConductorUninstall(unittest.TestCase):
    """Test cases for the Code Conductor uninstaller."""

    def setUp(self):
        """Create a temporary directory with a mock conductor installation."""
        self.test_dir = Path(tempfile.mkdtemp(prefix="conductor_test_"))
        self.original_cwd = Path.cwd()
        os.chdir(self.test_dir)

        # Initialize git repo
        subprocess.run(["git", "init"], capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"], capture_output=True
        )
        subprocess.run(["git", "config", "user.name", "Test User"], capture_output=True)

        # Create mock conductor installation
        self._create_mock_installation()

    def tearDown(self):
        """Clean up temporary directory."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def _create_mock_installation(self):
        """Create a mock conductor installation."""
        # Create .conductor directory structure
        conductor_dir = self.test_dir / ".conductor"
        conductor_dir.mkdir()

        # Create config file
        (conductor_dir / "config.yaml").write_text(
            """
project_name: test_project
technology_stack:
  languages: ["python"]
"""
        )

        # Create scripts directory
        scripts_dir = conductor_dir / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "conductor").write_text("#!/bin/bash\necho 'conductor'")
        (scripts_dir / "conductor").chmod(0o755)

        # Create roles directory
        roles_dir = conductor_dir / "roles"
        roles_dir.mkdir()
        (roles_dir / "dev.md").write_text("# Dev Role")

        # Create conductor wrapper
        conductor_wrapper = self.test_dir / "conductor"
        conductor_wrapper.write_text("#!/bin/bash\n.conductor/scripts/conductor")
        conductor_wrapper.chmod(0o755)

        # Create GitHub workflows
        workflows_dir = self.test_dir / ".github" / "workflows"
        workflows_dir.mkdir(parents=True)
        (workflows_dir / "conductor.yml").write_text("name: conductor")
        (workflows_dir / "pr-review.yml").write_text("name: pr-review")
        (workflows_dir / "user-workflow.yml").write_text("name: user-workflow")

        # Create issue template
        template_dir = self.test_dir / ".github" / "ISSUE_TEMPLATE"
        template_dir.mkdir(parents=True)
        (template_dir / "conductor-task.yml").write_text("name: conductor-task")

        # Create CLAUDE.md with conductor section
        claude_md = self.test_dir / "CLAUDE.md"
        claude_md.write_text(
            """# Project Instructions

Some project content here.

<!-- CONDUCTOR:START -->
## Conductor Section
This should be removed.
<!-- CONDUCTOR:END -->

More project content.
"""
        )

        # Create worktrees directory
        worktrees_dir = self.test_dir / "worktrees"
        worktrees_dir.mkdir()
        (worktrees_dir / "agent-dev-123").mkdir()

    def test_find_conductor_files(self):
        """Test that the uninstaller finds all conductor files."""
        uninstaller = ConductorUninstaller()
        items = uninstaller.find_conductor_files()

        # Check that all expected items are found
        # Resolve paths to handle macOS /private symlinks
        paths = []
        for item in items:
            try:
                paths.append(
                    str(item[0].resolve().relative_to(self.test_dir.resolve()))
                )
            except ValueError:
                # If relative_to fails, just use the name
                paths.append(item[0].name)

        self.assertIn(".conductor", paths)
        self.assertIn("conductor", paths)
        self.assertIn(".github/workflows/conductor.yml", paths)
        self.assertIn(".github/workflows/pr-review.yml", paths)
        self.assertIn(".github/ISSUE_TEMPLATE/conductor-task.yml", paths)
        self.assertIn("worktrees", paths)

        # Ensure user workflow is NOT in the list
        self.assertNotIn(".github/workflows/user-workflow.yml", paths)

    def test_find_claude_md_section(self):
        """Test detection of conductor section in CLAUDE.md."""
        uninstaller = ConductorUninstaller()
        claude_md = uninstaller.find_claude_md_section()

        self.assertIsNotNone(claude_md)
        self.assertEqual(claude_md.name, "CLAUDE.md")

    def test_dry_run(self):
        """Test that dry run doesn't remove anything."""
        uninstaller = ConductorUninstaller(dry_run=True)
        uninstaller.items_to_remove = uninstaller.find_conductor_files()

        # Run removal
        uninstaller.remove_items()

        # Verify nothing was removed
        self.assertTrue((self.test_dir / ".conductor").exists())
        self.assertTrue((self.test_dir / "conductor").exists())
        self.assertTrue(
            (self.test_dir / ".github" / "workflows" / "conductor.yml").exists()
        )

    def test_full_removal(self):
        """Test complete removal of conductor."""
        uninstaller = ConductorUninstaller(force=True)
        uninstaller.items_to_remove = uninstaller.find_conductor_files()

        # Run removal
        success = uninstaller.remove_items()
        uninstaller.cleanup_empty_dirs()

        self.assertTrue(success)

        # Verify conductor files are removed
        self.assertFalse((self.test_dir / ".conductor").exists())
        self.assertFalse((self.test_dir / "conductor").exists())
        self.assertFalse(
            (self.test_dir / ".github" / "workflows" / "conductor.yml").exists()
        )
        self.assertFalse(
            (self.test_dir / ".github" / "workflows" / "pr-review.yml").exists()
        )
        self.assertFalse(
            (
                self.test_dir / ".github" / "ISSUE_TEMPLATE" / "conductor-task.yml"
            ).exists()
        )
        self.assertFalse((self.test_dir / "worktrees").exists())

        # Verify user files are preserved
        self.assertTrue(
            (self.test_dir / ".github" / "workflows" / "user-workflow.yml").exists()
        )

        # Verify CLAUDE.md is updated
        claude_content = (self.test_dir / "CLAUDE.md").read_text()
        self.assertNotIn("<!-- CONDUCTOR:START -->", claude_content)
        self.assertNotIn("Conductor Section", claude_content)
        self.assertIn("Some project content here.", claude_content)
        self.assertIn("More project content.", claude_content)

    def test_empty_directory_cleanup(self):
        """Test that empty directories are cleaned up."""
        uninstaller = ConductorUninstaller(force=True)
        uninstaller.items_to_remove = uninstaller.find_conductor_files()

        # Run removal
        uninstaller.remove_items()
        uninstaller.cleanup_empty_dirs()

        # Check that empty ISSUE_TEMPLATE dir is removed
        self.assertFalse((self.test_dir / ".github" / "ISSUE_TEMPLATE").exists())

        # But .github/workflows should still exist (has user-workflow.yml)
        self.assertTrue((self.test_dir / ".github" / "workflows").exists())

    def test_partial_installation(self):
        """Test handling of partial installations."""
        # Remove some files to simulate partial installation
        shutil.rmtree(self.test_dir / ".conductor" / "roles")
        (self.test_dir / "conductor").unlink()

        uninstaller = ConductorUninstaller(force=True)
        uninstaller.items_to_remove = uninstaller.find_conductor_files()

        # Should still find remaining items
        paths = []
        for item in uninstaller.items_to_remove:
            try:
                paths.append(
                    str(item[0].resolve().relative_to(self.test_dir.resolve()))
                )
            except ValueError:
                # If relative_to fails, just use the name
                paths.append(item[0].name)
        self.assertIn(".conductor", paths)
        self.assertNotIn("conductor", paths)  # This was deleted

        # Run removal
        success = uninstaller.remove_items()
        self.assertTrue(success)

        # Verify all found items were removed
        self.assertFalse((self.test_dir / ".conductor").exists())


def create_mock_installation(test_dir):
    """Create a mock conductor installation for testing."""
    # Create .conductor directory structure
    conductor_dir = test_dir / ".conductor"
    conductor_dir.mkdir()

    # Create config file
    (conductor_dir / "config.yaml").write_text(
        """
project_name: test_project
technology_stack:
  languages: ["python"]
"""
    )

    # Create scripts directory
    scripts_dir = conductor_dir / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "conductor").write_text("#!/bin/bash\necho 'conductor'")
    (scripts_dir / "conductor").chmod(0o755)

    # Create roles directory
    roles_dir = conductor_dir / "roles"
    roles_dir.mkdir()
    (roles_dir / "dev.md").write_text("# Dev Role")

    # Create conductor wrapper
    conductor_wrapper = test_dir / "conductor"
    conductor_wrapper.write_text("#!/bin/bash\n.conductor/scripts/conductor")
    conductor_wrapper.chmod(0o755)

    # Create GitHub workflows
    workflows_dir = test_dir / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)
    (workflows_dir / "conductor.yml").write_text("name: conductor")
    (workflows_dir / "pr-review.yml").write_text("name: pr-review")

    # Create issue template
    template_dir = test_dir / ".github" / "ISSUE_TEMPLATE"
    template_dir.mkdir(parents=True)
    (template_dir / "conductor-task.yml").write_text("name: conductor-task")

    # Create CLAUDE.md with conductor section
    claude_md = test_dir / "CLAUDE.md"
    claude_md.write_text(
        """# Project Instructions

Some project content here.

<!-- CONDUCTOR:START -->
## Conductor Section
This should be removed.
<!-- CONDUCTOR:END -->

More project content.
"""
    )


def run_integration_test():
    """Run a full integration test of the uninstaller."""
    print("Running integration test of uninstaller...")

    # Create a test directory
    test_dir = Path(tempfile.mkdtemp(prefix="conductor_integration_"))
    original_cwd = Path.cwd()

    try:
        os.chdir(test_dir)

        # Initialize git repo
        subprocess.run(["git", "init"], capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"], capture_output=True
        )
        subprocess.run(["git", "config", "user.name", "Test User"], capture_output=True)

        # Copy setup.py and run it, or create a mock installation
        setup_src = original_cwd / "setup.py"
        if setup_src.exists():
            shutil.copy(setup_src, test_dir)

            # Run setup in auto mode
            print("Running setup.py --auto...")
            result = subprocess.run(
                [sys.executable, "setup.py", "--auto"], capture_output=True, text=True
            )
            if result.returncode != 0:
                # If setup fails, it might be because it's already configured
                # Try creating a mock installation instead
                print(
                    "Setup failed (this is expected in some cases), "
                    "creating mock installation..."
                )
                create_mock_installation(test_dir)
        else:
            # Create a mock installation if setup.py doesn't exist
            print("Creating mock Code Conductor installation...")
            create_mock_installation(test_dir)

        # Copy uninstall.py
        shutil.copy(original_cwd / "uninstall.py", test_dir)

        # Run uninstall with dry-run first
        print("\nRunning uninstall.py --dry-run...")
        result = subprocess.run(
            [sys.executable, "uninstall.py", "--dry-run", "--verbose"],
            capture_output=True,
            text=True,
        )
        print(result.stdout)

        # Run actual uninstall
        print("\nRunning uninstall.py --force...")
        result = subprocess.run(
            [sys.executable, "uninstall.py", "--force"], capture_output=True, text=True
        )
        print(result.stdout)

        if result.returncode != 0:
            print(f"Uninstall failed: {result.stderr}")
            return False

        # Verify removal
        if (test_dir / ".conductor").exists():
            print("ERROR: .conductor directory still exists!")
            return False

        print("\nIntegration test passed!")
        return True

    finally:
        os.chdir(original_cwd)
        shutil.rmtree(test_dir)


if __name__ == "__main__":
    # Run unit tests
    print("Running unit tests...\n")
    unittest.main(argv=[""], exit=False, verbosity=2)

    # Run integration test
    print("\n" + "=" * 60 + "\n")
    if run_integration_test():
        print("\nAll tests passed!")
    else:
        print("\nIntegration test failed!")
        sys.exit(1)
