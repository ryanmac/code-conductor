"""
Configuration Management Module - Main Orchestrator
Coordinates configuration gathering through express or interactive modes
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from .cache_manager import get_cache
from .ui_manager import UIManager
from .config import get_express_config, InteractiveConfigurator


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
        """Gather project configuration based on detected stack"""
        # Try express configuration first if we have enhanced stack
        if enhanced_stack and ui:
            express_config = get_express_config(enhanced_stack)
            if express_config:
                return self.apply_express_config(express_config, enhanced_stack, ui)

        # Fallback to interactive or auto mode
        if self.auto_mode:
            self._auto_configure(detected_stack)
        else:
            interactive = InteractiveConfigurator(self.project_root, self.debug)
            self.config = interactive.configure(detected_stack)

        # Add timestamp
        self.config["created_at"] = datetime.now().isoformat()

        return self.config

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
        self.config["created_at"] = datetime.now().isoformat()

        return self.config

    def _infer_project_name(self) -> str:
        """Infer project name from directory or package files"""
        # Try package.json first
        if (self.project_root / "package.json").exists():
            try:
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

        # Fallback to directory name
        return self.project_root.name

    def _infer_docs_directory(self) -> str:
        """Infer documentation directory"""
        common_docs_dirs = ["docs", "documentation", "doc"]
        for doc_dir in common_docs_dirs:
            if (self.project_root / doc_dir).exists():
                return doc_dir

        # Check if README.md exists as minimal docs
        if (self.project_root / "README.md").exists():
            return "."

        return "docs"  # Default

    def _auto_configure(self, detected_stack: List[Dict[str, Any]]):
        """Auto-configure based on detected stack"""
        print("\n🤖 Auto-configuring based on detected technology stack...")

        # Basic configuration
        self.config["project_name"] = self._infer_project_name()
        self.config["docs_directory"] = self._infer_docs_directory()

        # Determine roles based on stack
        roles = ["dev", "code-reviewer"]  # Always include these

        # Flatten detected stack for analysis
        stack_flat = []
        for item in detected_stack:
            if isinstance(item, dict):
                stack_flat.extend(item.values())
            else:
                stack_flat.append(item)

        # Add specialized roles
        stack_str = str(stack_flat).lower()
        if any(tech in stack_str for tech in ["react", "vue", "angular", "svelte"]):
            roles.append("frontend")
        if any(
            tech in stack_str
            for tech in ["django", "flask", "fastapi", "express", "rails"]
        ):
            roles.append("backend")
        if any(tech in stack_str for tech in ["ios", "android", "react-native"]):
            roles.append("mobile")
        if any(tech in stack_str for tech in ["tensorflow", "pytorch", "scikit-learn"]):
            roles.append("ml-engineer")

        # Remove duplicates while preserving order
        seen = set()
        unique_roles = []
        for role in roles:
            if role not in seen:
                seen.add(role)
                unique_roles.append(role)

        self.config["roles"] = {
            "default": "dev",
            "specialized": [r for r in unique_roles if r != "dev"],
        }

        # Enable GitHub integration by default
        self.config["github_integration"] = {
            "issue_to_task": True,
            "pr_reviews": True,
        }
        self.config["task_management"] = "github-issues"
        self.config["max_concurrent_agents"] = 5

        print(f"✅ Configured project: {self.config['project_name']}")
        print(f"✅ Detected roles: {', '.join(unique_roles)}")
        print("✅ GitHub integration enabled")
