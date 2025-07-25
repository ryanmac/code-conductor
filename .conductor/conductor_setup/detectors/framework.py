"""
Framework detection including modern frameworks
"""

import json
from typing import List, Dict, Any
from .base import BaseDetector


class FrameworkDetector(BaseDetector):
    """Detects web frameworks and modern build tools"""

    def detect(self) -> List[str]:
        """Detect traditional frameworks"""
        frameworks = []

        # Python frameworks
        if self.file_exists("manage.py") and self.glob_exists("*/settings.py"):
            frameworks.append("django")
        if self._check_requirements_for_package("flask"):
            frameworks.append("flask")
        if self._check_requirements_for_package("fastapi"):
            frameworks.append("fastapi")

        # JavaScript frameworks (traditional)
        if self._check_package_json_for_dep("express"):
            frameworks.append("express")
        if self._check_package_json_for_dep("@angular/core"):
            frameworks.append("angular")
        if self.file_exists("ember-cli-build.js"):
            frameworks.append("ember")

        # Ruby frameworks
        if self.file_exists("config.ru") and self.glob_exists("config/application.rb"):
            frameworks.append("rails")

        # PHP frameworks
        if self.file_exists("artisan"):
            frameworks.append("laravel")
        if self.file_exists("bin/console") and self.glob_exists("config/bundles.php"):
            frameworks.append("symfony")

        # .NET
        if self.glob_exists("**/*.csproj"):
            content = self.read_file_lines(
                list(self.project_root.glob("**/*.csproj"))[0]
            )
            if any("Microsoft.AspNetCore" in line for line in content):
                frameworks.append("asp.net")

        return frameworks

    def detect_modern_frameworks(self) -> Dict[str, Any]:
        """Enhanced detection for modern frameworks with better accuracy"""
        modern = {
            "frameworks": [],
            "build_tools": [],
            "meta_frameworks": [],
            "ui_libraries": [],
        }

        # Modern React-based frameworks
        if self._check_package_json_for_dep("next"):
            modern["meta_frameworks"].append("nextjs")
        if self._check_package_json_for_dep("gatsby"):
            modern["meta_frameworks"].append("gatsby")
        if self._check_package_json_for_dep("@remix-run/react"):
            modern["meta_frameworks"].append("remix")

        # Modern Vue frameworks
        if self.file_exists("nuxt.config.js", "nuxt.config.ts"):
            modern["meta_frameworks"].append("nuxt")

        # Modern build tools
        if self.file_exists("vite.config.js", "vite.config.ts"):
            modern["build_tools"].append("vite")
        if self.file_exists("webpack.config.js"):
            modern["build_tools"].append("webpack")
        if self._check_package_json_for_dep("parcel"):
            modern["build_tools"].append("parcel")
        if self._check_package_json_for_dep("@turbo/pack"):
            modern["build_tools"].append("turbopack")
        if self.file_exists(".swcrc") or self._check_package_json_for_dep("@swc/core"):
            modern["build_tools"].append("swc")
        if self.file_exists("rollup.config.js"):
            modern["build_tools"].append("rollup")

        # Newer frameworks
        if self.file_exists("astro.config.mjs", "astro.config.js"):
            modern["meta_frameworks"].append("astro")
        if self._check_package_json_for_dep("solid-js"):
            modern["ui_libraries"].append("solidjs")
        if self._check_package_json_for_dep("svelte"):
            modern["ui_libraries"].append("svelte")
        if self._check_package_json_for_dep("@sveltejs/kit"):
            modern["meta_frameworks"].append("sveltekit")
        if self._check_package_json_for_dep("qwik"):
            modern["ui_libraries"].append("qwik")

        # Mobile frameworks
        if self.file_exists("app.json") and self._check_package_json_for_dep(
            "react-native"
        ):
            modern["frameworks"].append("react-native")
        if self.file_exists("ionic.config.json"):
            modern["frameworks"].append("ionic")
        if self.file_exists("capacitor.config.json"):
            modern["frameworks"].append("capacitor")

        # Desktop frameworks
        if self._check_package_json_for_dep("electron"):
            modern["frameworks"].append("electron")
        if self.file_exists("tauri.conf.json"):
            modern["frameworks"].append("tauri")

        # CSS frameworks (important for agent role assignment)
        if self._check_package_json_for_dep("tailwindcss"):
            modern["ui_libraries"].append("tailwind")
        if self._check_package_json_for_dep("@mui/material"):
            modern["ui_libraries"].append("material-ui")
        if self._check_package_json_for_dep("antd"):
            modern["ui_libraries"].append("ant-design")
        if self._check_package_json_for_dep("@chakra-ui/react"):
            modern["ui_libraries"].append("chakra-ui")

        # Check for UI libraries
        if self._check_package_json_for_dep("react"):
            modern["ui_libraries"].append("react")
        if self._check_package_json_for_dep("vue"):
            modern["ui_libraries"].append("vue")

        return modern

    def _check_package_json_for_dep(self, package: str) -> bool:
        """Check if package.json contains a specific dependency"""
        if not self.file_exists("package.json"):
            return False

        try:
            with open(self.project_root / "package.json", "r") as f:
                data = json.load(f)
                deps = data.get("dependencies", {})
                dev_deps = data.get("devDependencies", {})
                return package in deps or package in dev_deps
        except (json.JSONDecodeError, FileNotFoundError):
            return False

    def _check_requirements_for_package(self, package: str) -> bool:
        """Check Python requirements files for a package"""
        req_files = ["requirements.txt", "requirements.in", "setup.py", "setup.cfg"]

        for req_file in req_files:
            if self.file_exists(req_file):
                lines = self.read_file_lines(req_file, 200)
                if any(package.lower() in line.lower() for line in lines):
                    return True

        # Check pyproject.toml
        if self.file_exists("pyproject.toml"):
            lines = self.read_file_lines("pyproject.toml", 200)
            if any(f'"{package}"' in line or f"'{package}'" in line for line in lines):
                return True

        return False
