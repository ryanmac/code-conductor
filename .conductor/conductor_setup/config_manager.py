"""
Configuration Management Module
Handles gathering and managing project configuration through interactive prompts
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional


class ConfigurationManager:
    """Manages project configuration through interactive or automatic setup"""

    def __init__(
        self, project_root: Path, auto_mode: bool = False, debug: bool = False
    ):
        self.project_root = project_root
        self.auto_mode = auto_mode
        self.debug = debug
        self.config = {}

    def gather_configuration(
        self, detected_stack: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Gather configuration through interactive prompts or auto-configuration"""
        if self.auto_mode:
            self._auto_configure(detected_stack)
        else:
            self._interactive_configure(detected_stack)
        return self.config

    def _safe_input(self, prompt: str, default: Optional[str] = None) -> str:
        """Safe input with error handling"""
        try:
            response = input(prompt).strip()
            return response or default
        except KeyboardInterrupt:
            print("\n\n❌ Setup cancelled by user.")
            sys.exit(1)
        except EOFError:
            return default
        except Exception as e:
            if self.debug:
                print(f"❌ Input error: {e}")
            return default

    def _interactive_configure(self, detected_stack: List[Dict[str, Any]]):
        """Interactive configuration prompts"""
        print("\n📝 Project Configuration")
        print("-" * 30)

        # Project name
        default_name = self.project_root.name
        try:
            self.config["project_name"] = self._safe_input(
                f"Project name [{default_name}]: ", default_name
            )
        except Exception as e:
            print(f"❌ Error reading input: {e}")
            print("💡 Try running with --auto flag for automatic configuration")
            sys.exit(1)

        # Documentation directory
        self.config["docs_directory"] = self._get_docs_directory()

        # Role configuration
        self._configure_roles(detected_stack)

        # Task management approach
        self._configure_task_management()

        # Concurrent agents
        self._configure_concurrent_agents()

    def _get_docs_directory(self) -> str:
        """Determine documentation directory"""
        default_docs = "docs"
        if (self.project_root / "docs").exists():
            default_docs = "docs"
        elif (self.project_root / "documentation").exists():
            default_docs = "documentation"

        return self._safe_input(
            f"Documentation directory [{default_docs}]: ", default_docs
        )

    def _configure_roles(self, detected_stack: List[Dict[str, Any]]):
        """Configure agent roles based on detected stack"""
        print("\n🎭 Agent Role Configuration")
        print("The hybrid model uses 'dev' as the default generalist role")
        print("with optional specialized roles for complex tasks.")

        # Suggest roles based on detected stack
        suggested = set()
        for stack in detected_stack:
            suggested.update(stack.get("suggested_roles", []))

        suggested_str = ", ".join(suggested) if suggested else "none detected"
        print(f"\nSuggested specialized roles: {suggested_str}")

        print("\nCommon specialized roles:")
        print("  - devops: CI/CD, deployments, infrastructure")
        print("  - security: Audits, vulnerability scanning")
        print("  - ml-engineer: Machine learning tasks")
        print("  - ui-designer: Design system, components")

        roles_input = self._safe_input(
            "\nEnter specialized roles (comma-separated, or press Enter for none): ",
            "",
        )

        specialized_roles = []
        if roles_input:
            specialized_roles = [r.strip() for r in roles_input.split(",") if r.strip()]

        self.config["roles"] = {"default": "dev", "specialized": specialized_roles}

    def _configure_task_management(self):
        """Configure task management approach"""
        print("\n📋 Task Management Configuration")
        print("1. GitHub Issues (recommended) - Use labels and automation")
        print("2. JSON files - Direct state management")
        print("3. Hybrid - Both approaches")

        choice = self._safe_input("Select approach [1]: ", "1")
        task_approaches = {"1": "github-issues", "2": "json-files", "3": "hybrid"}
        self.config["task_management"] = task_approaches.get(choice, "github-issues")

    def _configure_concurrent_agents(self):
        """Configure maximum concurrent agents"""
        default_concurrent = "10"
        max_agents = self._safe_input(
            f"\nMaximum concurrent agents [{default_concurrent}]: ", default_concurrent
        )

        try:
            self.config["max_concurrent_agents"] = int(max_agents)
        except ValueError:
            print(f"⚠️  Invalid number '{max_agents}', using default: 10")
            self.config["max_concurrent_agents"] = 10

    def _auto_configure(self, detected_stack: List[Dict[str, Any]]):
        """Auto-configuration mode with minimal prompts"""
        print("\n🤖 Auto-configuration mode enabled")
        print("-" * 30)

        # Use sensible defaults
        self.config["project_name"] = self.project_root.name
        self.config["docs_directory"] = "docs"

        # Detect roles based on enhanced stack detection
        suggested_roles = set()
        detected_stacks = []

        for stack in detected_stack:
            suggested_roles.update(stack.get("suggested_roles", []))
            if "detected_subtypes" in stack:
                detected_stacks.append(
                    f"{stack['tech']} ({', '.join(stack['detected_subtypes'])})"
                )
            else:
                detected_stacks.append(stack["tech"])

        # Always include code-reviewer role for AI-powered PR reviews
        specialized_roles = ["code-reviewer"]

        # Add roles based on detected stack
        specialized_roles.extend(list(suggested_roles))

        # Additional heuristics
        if any("docker" in str(f).lower() for f in self.project_root.glob("*")):
            if "devops" not in specialized_roles:
                specialized_roles.append("devops")
        if any("security" in str(f).lower() for f in self.project_root.glob("*")):
            if "security" not in specialized_roles:
                specialized_roles.append("security")

        # Remove duplicates while preserving order
        specialized_roles = list(dict.fromkeys(specialized_roles))

        self.config["roles"] = {"default": "dev", "specialized": specialized_roles}
        self.config["detected_stacks"] = detected_stacks

        # Smart task management detection
        if (self.project_root / ".github").exists():
            self.config["task_management"] = "github-issues"
        else:
            self.config["task_management"] = "hybrid"

        # Conservative agent count
        self.config["max_concurrent_agents"] = 5

        print(f"✓ Project: {self.config['project_name']}")
        if detected_stacks:
            print(f"✓ Detected stacks: {', '.join(detected_stacks)}")
        print(
            f"✓ Roles: dev + {len(specialized_roles)} specialized "
            f"({', '.join(specialized_roles)})"
        )
        print(f"✓ Task management: {self.config['task_management']}")
        print(f"✓ Max agents: {self.config['max_concurrent_agents']}")
