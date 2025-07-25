#!/usr/bin/env python3
"""
Code Conductor Interactive Setup Script
Configures the repository for your specific project needs
"""

import sys
import argparse
import logging
from pathlib import Path

# Ensure the .conductor/setup package is in the Python path
conductor_path = Path(__file__).parent / ".conductor"
if conductor_path.exists():
    sys.path.insert(0, str(conductor_path))
    try:
        # Import from the conductor setup package
        from conductor_setup.detector import TechnologyDetector  # noqa: E402
        from conductor_setup.config_manager import ConfigurationManager  # noqa: E402
        from conductor_setup.file_generators.config_files import ConfigFileGenerator  # noqa: E402
        from conductor_setup.file_generators.role_files import RoleFileGenerator  # noqa: E402
        from conductor_setup.file_generators.workflow_files import WorkflowFileGenerator  # noqa: E402
        from conductor_setup.file_generators.script_files import ScriptFileGenerator  # noqa: E402
        from conductor_setup.github_integration import GitHubIntegration  # noqa: E402
        from conductor_setup.discovery_task import DiscoveryTaskCreator  # noqa: E402
        from conductor_setup.validator import SetupValidator  # noqa: E402
    except ImportError as e:
        # This might happen in test environments
        if __name__ == "__main__":
            print(f"Error: Could not import setup modules: {e}")
            print("Please ensure the .conductor/setup package is properly configured.")
            sys.exit(1)
        else:
            # Re-raise for tests to handle
            raise
else:
    # For testing or when .conductor doesn't exist yet
    if __name__ == "__main__":
        print("Error: .conductor/setup package not found")
        print("This script requires the Code Conductor setup modules.")
        sys.exit(1)


class ConductorSetup:
    """Main setup orchestrator that coordinates all setup modules"""

    def __init__(self, auto_mode=False, debug=False):
        self.project_root = Path.cwd()
        self.conductor_dir = self.project_root / ".conductor"
        self.config = {}
        self.detected_stack = []
        self.auto_mode = auto_mode
        self.debug = debug

        # Setup logging
        log_level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(level=log_level, format="%(message)s")
        self.logger = logging.getLogger(__name__)

    def run(self):
        """Main setup workflow"""
        self.print_header()

        # Check if already configured
        if self.check_existing_config():
            if not self.confirm_reconfigure():
                print("Setup cancelled.")
                return

        # Run setup steps using modular components
        self._detect_project_info()
        self._gather_configuration()
        self._create_configuration_files()
        self._create_role_definitions()
        self._create_github_workflows()
        self._ensure_github_labels()
        self._create_bootstrap_scripts()
        self._validate_setup()
        discovery_task_number = self._create_discovery_task()
        self._display_completion_message(discovery_task_number)

    def print_header(self):
        """Display setup header"""
        print("🚀 Code Conductor Setup")
        print("=" * 50)
        print("This will configure agent coordination for your project")
        print()

    def check_existing_config(self):
        """Check if already configured"""
        config_file = self.conductor_dir / "config.yaml"
        return config_file.exists()

    def confirm_reconfigure(self):
        """Ask user if they want to reconfigure"""
        print("⚠️  Existing configuration detected.")
        if self.auto_mode:
            print("Auto mode: reconfiguring existing setup...")
            return True

        # Use the same safe input logic as ConfigurationManager
        config_mgr = ConfigurationManager(self.project_root, self.auto_mode, self.debug)
        response = config_mgr._safe_input("Do you want to reconfigure? [y/N]: ", "n")
        return response.lower() == "y"

    def _detect_project_info(self):
        """Use TechnologyDetector to detect project characteristics"""
        detector = TechnologyDetector(self.project_root, self.debug)
        detection_result = detector.detect_project_info()
        self.detected_stack = detection_result["detected_stack"]
        self.config.update(detection_result["config"])

    def _gather_configuration(self):
        """Use ConfigurationManager to gather configuration"""
        config_mgr = ConfigurationManager(self.project_root, self.auto_mode, self.debug)
        self.config.update(config_mgr.gather_configuration(self.detected_stack))

    def _create_configuration_files(self):
        """Use ConfigFileGenerator to create configuration files"""
        generator = ConfigFileGenerator(self.project_root, self.config, self.debug)
        generator.create_configuration_files()

    def _create_role_definitions(self):
        """Use RoleFileGenerator to create role definitions"""
        generator = RoleFileGenerator(self.project_root, self.config)
        generator.create_role_definitions()

    def _create_github_workflows(self):
        """Use WorkflowFileGenerator to create GitHub workflows"""
        generator = WorkflowFileGenerator(self.project_root, self.config)
        generator.create_github_workflows()

    def _ensure_github_labels(self):
        """Use GitHubIntegration to ensure labels exist"""
        github = GitHubIntegration(self.project_root)
        github.ensure_github_labels()

    def _create_bootstrap_scripts(self):
        """Use ScriptFileGenerator to create bootstrap scripts"""
        generator = ScriptFileGenerator(self.project_root, self.config)
        generator.create_bootstrap_scripts()

    def _validate_setup(self):
        """Use SetupValidator to validate the setup"""
        validator = SetupValidator(self.project_root)
        return validator.validate_setup()

    def _create_discovery_task(self):
        """Use DiscoveryTaskCreator to create discovery task if needed"""
        creator = DiscoveryTaskCreator(self.project_root)
        return creator.create_discovery_task_if_needed()

    def _display_completion_message(self, discovery_task_number=None):
        """Use SetupValidator to display completion message"""
        validator = SetupValidator(self.project_root)
        validator.display_completion_message(discovery_task_number)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Code Conductor Interactive Setup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python setup.py              # Interactive setup
  python setup.py --auto       # Auto-configuration
  python setup.py --debug      # Enable debug logging
        """,
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Run in auto-configuration mode (minimal prompts)",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    try:
        setup = ConductorSetup(auto_mode=args.auto, debug=args.debug)
        setup.run()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        if args.debug:
            import traceback

            traceback.print_exc()
        else:
            print(f"\n❌ Setup failed: {e}")
            print("💡 Run with --debug for detailed error information")
        sys.exit(1)


if __name__ == "__main__":
    main()
