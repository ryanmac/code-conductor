"""
Configuration Management Module
Handles gathering and managing project configuration through interactive prompts
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

from .cache_manager import get_cache
from .ui_manager import UIManager


# Express configurations for common project types
EXPRESS_CONFIGS = {
    "react-typescript": {
        "patterns": ["react", "typescript", "tsx", "jsx"],
        "roles": {"default": "dev", "specialized": ["frontend", "code-reviewer"]},
        "github_integration": {"issue_to_task": True, "pr_reviews": True},
        "build_validation": ["npm test", "npm run build"],
        "suggested_tasks": [
            {
                "title": "Set up component testing with React Testing Library",
                "labels": ["conductor:task", "testing", "frontend"],
            },
            {
                "title": "Add Storybook for component development",
                "labels": ["conductor:task", "enhancement", "frontend"],
            },
            {
                "title": "Configure ESLint and Prettier",
                "labels": ["conductor:task", "code-quality", "dev-experience"],
            },
        ],
    },
    "python-fastapi": {
        "patterns": ["fastapi", "python", "uvicorn", "pydantic"],
        "roles": {"default": "dev", "specialized": ["backend", "code-reviewer"]},
        "github_integration": {"issue_to_task": True, "pr_reviews": True},
        "build_validation": ["pytest", "black --check ."],
        "suggested_tasks": [
            {
                "title": "Add API documentation with OpenAPI",
                "labels": ["conductor:task", "documentation", "backend"],
            },
            {
                "title": "Set up database migrations with Alembic",
                "labels": ["conductor:task", "database", "backend"],
            },
            {
                "title": "Add integration tests for endpoints",
                "labels": ["conductor:task", "testing", "backend"],
            },
        ],
    },
    "nextjs-fullstack": {
        "patterns": ["next", "react", "vercel"],
        "roles": {
            "default": "dev",
            "specialized": ["frontend", "backend", "code-reviewer"],
        },
        "github_integration": {"issue_to_task": True, "pr_reviews": True},
        "build_validation": ["npm test", "npm run build", "npm run lint"],
        "suggested_tasks": [
            {
                "title": "Set up authentication with NextAuth.js",
                "labels": ["conductor:task", "auth", "fullstack"],
            },
            {
                "title": "Configure Prisma for database access",
                "labels": ["conductor:task", "database", "backend"],
            },
            {
                "title": "Add E2E tests with Playwright",
                "labels": ["conductor:task", "testing", "e2e"],
            },
        ],
    },
    "vue-javascript": {
        "patterns": ["vue", "nuxt", "vite"],
        "roles": {"default": "dev", "specialized": ["frontend", "code-reviewer"]},
        "github_integration": {"issue_to_task": True, "pr_reviews": True},
        "build_validation": ["npm test", "npm run build"],
        "suggested_tasks": [
            {
                "title": "Set up Pinia for state management",
                "labels": ["conductor:task", "state-management", "frontend"],
            },
            {
                "title": "Add component testing with Vitest",
                "labels": ["conductor:task", "testing", "frontend"],
            },
            {
                "title": "Configure Vue Router for navigation",
                "labels": ["conductor:task", "routing", "frontend"],
            },
        ],
    },
    "python-django": {
        "patterns": ["django", "python", "wsgi"],
        "roles": {"default": "dev", "specialized": ["backend", "code-reviewer"]},
        "github_integration": {"issue_to_task": True, "pr_reviews": True},
        "build_validation": ["python manage.py test", "black --check ."],
        "suggested_tasks": [
            {
                "title": "Set up Django REST framework",
                "labels": ["conductor:task", "api", "backend"],
            },
            {
                "title": "Configure Celery for async tasks",
                "labels": ["conductor:task", "async", "backend"],
            },
            {
                "title": "Add Django Debug Toolbar",
                "labels": ["conductor:task", "dev-experience", "backend"],
            },
        ],
    },
}


class ConfigurationManager:
    """Manages project configuration through interactive or automatic setup"""

    def __init__(
        self, project_root: Path, auto_mode: bool = False, debug: bool = False
    ):
        self.project_root = project_root
        self.auto_mode = auto_mode
        self.debug = debug
        self.config = {}
        self.cache = get_cache()

    def gather_configuration(
        self,
        detected_stack: List[Dict[str, Any]],
        enhanced_stack: Optional[Dict[str, Any]] = None,
        ui: Optional[UIManager] = None,
    ) -> Dict[str, Any]:
        """Gather configuration with express-by-default approach"""
        # Try express config first if we have enhanced stack info
        if enhanced_stack and ui:
            express_config = self.get_express_config(enhanced_stack)
            if express_config:
                return self.apply_express_config(express_config, enhanced_stack, ui)

        # Fall back to legacy modes
        if self.auto_mode:
            self._auto_configure(detected_stack)
        else:
            self._interactive_configure(detected_stack)
        return self.config

    def get_express_config(
        self, stack_info: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Match detected stack to express config"""
        # Use the primary stack from summary if available
        if stack_info.get("summary", {}).get("primary_stack"):
            stack_name = stack_info["summary"]["primary_stack"]
            if stack_name in EXPRESS_CONFIGS:
                return EXPRESS_CONFIGS[stack_name]

        # Otherwise try pattern matching
        detected_items = set()
        detected_items.update(stack_info.get("frameworks", []))
        detected_items.update(stack_info.get("summary", {}).get("languages", []))
        detected_items.update(stack_info.get("summary", {}).get("tools", []))

        # Add items from modern tools
        modern = stack_info.get("modern_tools", {})
        if modern.get("framework"):
            detected_items.add(modern["framework"])
        if modern.get("build_tool"):
            detected_items.add(modern["build_tool"])

        # Find best match
        best_match = None
        best_score = 0

        for stack_name, config in EXPRESS_CONFIGS.items():
            score = len(detected_items.intersection(config["patterns"]))
            if score > best_score:
                best_match = stack_name
                best_score = score

        return (
            EXPRESS_CONFIGS.get(best_match) if best_match and best_score > 0 else None
        )

    def apply_express_config(
        self, express_config: Dict[str, Any], stack_info: Dict[str, Any], ui: UIManager
    ) -> Dict[str, Any]:
        """Apply express configuration without prompts"""
        primary_stack = stack_info.get("summary", {}).get("primary_stack", "project")
        ui.console.print(
            f"\nDetected {primary_stack} - applying optimal configuration..."
        )

        with ui.create_progress() as progress:
            task = progress.add_task("Configuring", total=4)

            progress.update(task, advance=1, description="Setting project defaults...")
            self.config["project_name"] = self._infer_project_name()
            self.config["docs_directory"] = self._infer_docs_directory()

            progress.update(task, advance=1, description="Configuring agent roles...")
            self.config["roles"] = express_config["roles"]

            progress.update(task, advance=1, description="Enabling integrations...")
            self.config["github_integration"] = express_config["github_integration"]
            self.config["task_management"] = "github-issues"
            self.config["max_concurrent_agents"] = 5

            progress.update(task, advance=1, description="Preparing starter tasks...")
            self.config["suggested_tasks"] = express_config["suggested_tasks"]
            self.config["build_validation"] = express_config.get("build_validation", [])

        # Add metadata
        self.config["setup_mode"] = "express"
        self.config["stack_info"] = stack_info
        self.config["stack_summary"] = stack_info.get("summary", {}).get(
            "primary_stack", "Unknown"
        )
        self.config["task_count"] = len(express_config["suggested_tasks"])

        return self.config

    def _infer_project_name(self) -> str:
        """Infer project name from directory or package files"""
        # Try package.json first
        if (self.project_root / "package.json").exists():
            try:
                import json

                package = json.loads((self.project_root / "package.json").read_text())
                if package.get("name"):
                    return package["name"]
            except Exception:
                pass

        # Try pyproject.toml
        if (self.project_root / "pyproject.toml").exists():
            try:
                content = (self.project_root / "pyproject.toml").read_text()
                for line in content.split("\n"):
                    if line.strip().startswith("name"):
                        name = line.split("=")[1].strip().strip("\"'")
                        if name:
                            return name
            except Exception:
                pass

        # Default to directory name
        return self.project_root.name

    def _infer_docs_directory(self) -> str:
        """Infer documentation directory"""
        if (self.project_root / "docs").exists():
            return "docs"
        elif (self.project_root / "documentation").exists():
            return "documentation"
        elif (self.project_root / "doc").exists():
            return "doc"
        return "docs"

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
