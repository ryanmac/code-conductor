"""
Monorepo and workspace detection
"""

import json
from typing import Dict, Any, List
from .base import BaseDetector


class MonorepoDetector(BaseDetector):
    """Detects monorepo setups and workspace configurations"""

    def detect(self) -> Dict[str, Any]:
        """Detect monorepo tools and workspace structure"""
        monorepo_info = {"tool": None, "workspaces": [], "config_files": []}

        # Nx monorepo
        if self.file_exists("nx.json"):
            monorepo_info["tool"] = "nx"
            monorepo_info["config_files"].append("nx.json")
            monorepo_info["workspaces"] = self._detect_nx_projects()

        # Lerna
        elif self.file_exists("lerna.json"):
            monorepo_info["tool"] = "lerna"
            monorepo_info["config_files"].append("lerna.json")
            monorepo_info["workspaces"] = self._detect_lerna_packages()

        # Rush
        elif self.file_exists("rush.json"):
            monorepo_info["tool"] = "rush"
            monorepo_info["config_files"].append("rush.json")

        # Turborepo
        elif self.file_exists("turbo.json"):
            monorepo_info["tool"] = "turborepo"
            monorepo_info["config_files"].append("turbo.json")

        # pnpm workspaces
        elif self.file_exists("pnpm-workspace.yaml"):
            monorepo_info["tool"] = "pnpm-workspaces"
            monorepo_info["config_files"].append("pnpm-workspace.yaml")
            monorepo_info["workspaces"] = self._detect_pnpm_workspaces()

        # Yarn workspaces
        elif self._has_yarn_workspaces():
            monorepo_info["tool"] = "yarn-workspaces"
            monorepo_info["workspaces"] = self._detect_yarn_workspaces()

        # npm workspaces
        elif self._has_npm_workspaces():
            monorepo_info["tool"] = "npm-workspaces"
            monorepo_info["workspaces"] = self._detect_npm_workspaces()

        # Bazel
        elif self.file_exists("WORKSPACE", "WORKSPACE.bazel"):
            monorepo_info["tool"] = "bazel"
            monorepo_info["config_files"].append("WORKSPACE")

        # Additional checks for workspace patterns
        if not monorepo_info["tool"]:
            # Check for common monorepo patterns
            if self.glob_exists("packages/*/package.json"):
                monorepo_info["tool"] = "custom"
                monorepo_info["workspaces"] = ["packages/*"]
            elif self.glob_exists("apps/*/package.json") and self.glob_exists(
                "libs/*/package.json"
            ):
                monorepo_info["tool"] = "custom"
                monorepo_info["workspaces"] = ["apps/*", "libs/*"]

        return monorepo_info

    def _detect_nx_projects(self) -> List[str]:
        """Detect Nx workspace projects"""
        projects = []

        # Check workspace.json or project.json files
        if self.file_exists("workspace.json"):
            try:
                with open(self.project_root / "workspace.json", "r") as f:
                    data = json.load(f)
                    projects = list(data.get("projects", {}).keys())
            except (json.JSONDecodeError, FileNotFoundError):
                pass

        # Modern Nx uses project.json in each project
        for project_json in self.project_root.glob("**/project.json"):
            if "node_modules" not in str(project_json):
                projects.append(project_json.parent.name)

        return projects

    def _detect_lerna_packages(self) -> List[str]:
        """Detect Lerna packages"""
        try:
            with open(self.project_root / "lerna.json", "r") as f:
                data = json.load(f)
                return data.get("packages", [])
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _detect_pnpm_workspaces(self) -> List[str]:
        """Detect pnpm workspace packages"""
        # Simple YAML parsing for workspace paths
        lines = self.read_file_lines("pnpm-workspace.yaml", 50)
        workspaces = []
        in_packages = False

        for line in lines:
            if "packages:" in line:
                in_packages = True
                continue
            if in_packages and line.strip().startswith("-"):
                workspace = line.strip().lstrip("- ").strip("'\"")
                workspaces.append(workspace)
            elif in_packages and not line.strip():
                break

        return workspaces

    def _has_yarn_workspaces(self) -> bool:
        """Check if yarn workspaces are configured"""
        if not self.file_exists("package.json"):
            return False

        try:
            with open(self.project_root / "package.json", "r") as f:
                data = json.load(f)
                return "workspaces" in data
        except (json.JSONDecodeError, FileNotFoundError):
            return False

    def _detect_yarn_workspaces(self) -> List[str]:
        """Detect yarn workspace packages"""
        try:
            with open(self.project_root / "package.json", "r") as f:
                data = json.load(f)
                workspaces = data.get("workspaces", [])
                if isinstance(workspaces, dict):
                    return workspaces.get("packages", [])
                return workspaces
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _has_npm_workspaces(self) -> bool:
        """Check if npm workspaces are configured (npm 7+)"""
        return self._has_yarn_workspaces()  # Same structure in package.json

    def _detect_npm_workspaces(self) -> List[str]:
        """Detect npm workspace packages"""
        return self._detect_yarn_workspaces()  # Same implementation
