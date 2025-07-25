"""
Interactive configuration gathering
"""

from pathlib import Path
from typing import Dict, Any, List, Optional


class InteractiveConfigurator:
    """Handles interactive configuration prompts"""

    def __init__(self, project_root: Path, debug: bool = False):
        self.project_root = project_root
        self.debug = debug
        self.config = {}

    def configure(self, detected_stack: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run interactive configuration"""
        print("\n" + "=" * 60)
        print("🎼 Code Conductor Interactive Setup")
        print("=" * 60)

        # Basic configuration
        self.config["project_name"] = self._safe_input(
            "\n📝 Project name", default=self.project_root.name
        )

        # Documentation
        self.config["docs_directory"] = self._get_docs_directory()

        # Agent roles
        self._configure_roles(detected_stack)

        # Task management
        self._configure_task_management()

        # Concurrent agents
        self._configure_concurrent_agents()

        return self.config

    def _safe_input(self, prompt: str, default: Optional[str] = None) -> str:
        """Get user input with a default value"""
        if default:
            prompt = f"{prompt} [{default}]"
        prompt += ": "

        value = input(prompt).strip()
        if not value and default:
            return default
        return value

    def _get_docs_directory(self) -> str:
        """Ask for documentation directory"""
        docs_default = self._find_docs_directory()
        docs_prompt = "\n📚 Documentation directory"
        if docs_default:
            return self._safe_input(docs_prompt, default=docs_default)
        else:
            docs_dir = self._safe_input(docs_prompt + " (or 'none')", default="docs")
            return docs_dir if docs_dir.lower() != "none" else ""

    def _find_docs_directory(self) -> str:
        """Auto-detect documentation directory"""
        common_docs_dirs = ["docs", "documentation", "doc", "README.md"]
        for doc_dir in common_docs_dirs:
            if (self.project_root / doc_dir).exists():
                return doc_dir
        return ""

    def _configure_roles(self, detected_stack: List[Dict[str, Any]]):
        """Configure agent roles based on detected stack"""
        print("\n🤖 Agent Roles Configuration")
        print("-" * 40)

        # Suggest roles based on detected stack
        suggested_roles = ["dev", "code-reviewer"]  # Always include these
        stack_flat = []
        for item in detected_stack:
            if isinstance(item, dict):
                stack_flat.extend(item.values())
            else:
                stack_flat.append(item)

        # Add specialized roles based on detection
        if any("react" in str(tech).lower() for tech in stack_flat):
            suggested_roles.append("frontend")
        if any(
            tech in str(stack_flat).lower()
            for tech in ["django", "flask", "fastapi", "express"]
        ):
            suggested_roles.append("backend")
        if any("mobile" in str(tech).lower() for tech in stack_flat):
            suggested_roles.append("mobile")

        print(f"Suggested roles: {', '.join(suggested_roles)}")
        custom_roles = self._safe_input(
            "Additional roles (comma-separated) or Enter to accept", default=""
        )

        if custom_roles:
            additional = [r.strip() for r in custom_roles.split(",") if r.strip()]
            suggested_roles.extend(additional)

        # Remove duplicates while preserving order
        seen = set()
        unique_roles = []
        for role in suggested_roles:
            if role not in seen:
                seen.add(role)
                unique_roles.append(role)

        self.config["roles"] = {
            "default": "dev",
            "specialized": [r for r in unique_roles if r != "dev"],
        }

    def _configure_task_management(self):
        """Configure task management preferences"""
        print("\n📋 Task Management")
        print("-" * 40)
        print("How should tasks be managed?")
        print("1. GitHub Issues (recommended)")
        print("2. Local task files only")

        choice = self._safe_input("Choice [1]", default="1")
        if choice == "2":
            self.config["github_integration"] = {
                "issue_to_task": False,
                "pr_reviews": False,
            }
            self.config["task_management"] = "local"
        else:
            self.config["github_integration"] = {
                "issue_to_task": True,
                "pr_reviews": True,
            }
            self.config["task_management"] = "github-issues"

    def _configure_concurrent_agents(self):
        """Configure concurrent agent limits"""
        default_agents = "5"
        agent_count = self._safe_input(
            "\n🔀 Maximum concurrent agents", default=default_agents
        )

        try:
            self.config["max_concurrent_agents"] = int(agent_count)
        except ValueError:
            print(f"Invalid number, using default: {default_agents}")
            self.config["max_concurrent_agents"] = int(default_agents)
