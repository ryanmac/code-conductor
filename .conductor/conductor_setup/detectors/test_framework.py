"""
Test framework detection
"""

from typing import List
from .base import BaseDetector


class TestFrameworkDetector(BaseDetector):
    """Detects testing frameworks and tools"""

    def detect(self) -> List[str]:
        """Detect test frameworks in use"""
        test_frameworks = []

        # JavaScript/TypeScript test frameworks
        if self.file_exists("jest.config.js", "jest.config.ts", "jest.config.json"):
            test_frameworks.append("jest")
        elif self._check_package_json_script("jest"):
            test_frameworks.append("jest")

        if self.file_exists("vitest.config.js", "vitest.config.ts"):
            test_frameworks.append("vitest")
        elif self._check_package_json_script("vitest"):
            test_frameworks.append("vitest")

        if self.file_exists("cypress.json", "cypress.config.js", "cypress.config.ts"):
            test_frameworks.append("cypress")
        elif self.glob_exists("cypress/**"):
            test_frameworks.append("cypress")

        if self.file_exists("playwright.config.js", "playwright.config.ts"):
            test_frameworks.append("playwright")

        if self.file_exists(".mocharc.json", ".mocharc.js", "mocha.opts"):
            test_frameworks.append("mocha")
        elif self._check_package_json_script("mocha"):
            test_frameworks.append("mocha")

        if self.file_exists("karma.conf.js"):
            test_frameworks.append("karma")

        if self._check_package_json_dep("ava"):
            test_frameworks.append("ava")

        if self._check_package_json_dep("tape"):
            test_frameworks.append("tape")

        if self._check_package_json_dep("qunit"):
            test_frameworks.append("qunit")

        # Python test frameworks
        if self.file_exists("pytest.ini", "pyproject.toml", "setup.cfg"):
            # Check for pytest configuration
            if self._check_file_contains("pytest.ini", "[pytest]"):
                test_frameworks.append("pytest")
            elif self._check_file_contains("pyproject.toml", "[tool.pytest"):
                test_frameworks.append("pytest")
            elif self._check_file_contains("setup.cfg", "[tool:pytest]"):
                test_frameworks.append("pytest")
        elif self.glob_exists("test_*.py", "tests/test_*.py"):
            test_frameworks.append("pytest/unittest")

        if self.file_exists("tox.ini"):
            test_frameworks.append("tox")

        if self.file_exists(".coveragerc") or self._check_file_contains(
            "pyproject.toml", "[tool.coverage"
        ):
            test_frameworks.append("coverage.py")

        # Ruby test frameworks
        if self.glob_exists("spec/**/*_spec.rb"):
            test_frameworks.append("rspec")
        if self.glob_exists("test/**/*_test.rb"):
            test_frameworks.append("minitest")

        # Go test frameworks
        if self.glob_exists("**/*_test.go"):
            test_frameworks.append("go test")
        if self._check_go_imports("github.com/stretchr/testify"):
            test_frameworks.append("testify")

        # Java test frameworks
        if self._check_maven_dep("junit"):
            test_frameworks.append("junit")
        if self._check_gradle_dep("testng"):
            test_frameworks.append("testng")

        # .NET test frameworks
        if self.glob_exists("**/*.Tests.csproj"):
            test_frameworks.append("dotnet test")
        if self._check_csproj_package("xunit"):
            test_frameworks.append("xunit")
        if self._check_csproj_package("nunit"):
            test_frameworks.append("nunit")

        # PHP test frameworks
        if self.file_exists("phpunit.xml", "phpunit.xml.dist"):
            test_frameworks.append("phpunit")

        # Rust test frameworks
        if self.glob_exists("tests/**/*.rs") or self.glob_exists("src/**/*test*.rs"):
            test_frameworks.append("cargo test")

        return test_frameworks

    def _check_package_json_script(self, keyword: str) -> bool:
        """Check if package.json scripts contain a keyword"""
        try:
            import json

            with open(self.project_root / "package.json", "r") as f:
                data = json.load(f)
                scripts = data.get("scripts", {})
                return any(keyword in script for script in scripts.values())
        except Exception:
            return False

    def _check_package_json_dep(self, package: str) -> bool:
        """Check if package.json contains a dependency"""
        try:
            import json

            with open(self.project_root / "package.json", "r") as f:
                data = json.load(f)
                deps = data.get("dependencies", {})
                dev_deps = data.get("devDependencies", {})
                return package in deps or package in dev_deps
        except Exception:
            return False

    def _check_file_contains(self, filename: str, text: str) -> bool:
        """Check if a file contains specific text"""
        lines = self.read_file_lines(filename, 100)
        return any(text in line for line in lines)

    def _check_go_imports(self, import_path: str) -> bool:
        """Check Go files for specific import"""
        for go_file in self.project_root.glob("**/*.go"):
            if "vendor" in str(go_file):
                continue
            lines = self.read_file_lines(
                str(go_file.relative_to(self.project_root)), 50
            )
            if any(import_path in line for line in lines):
                return True
        return False

    def _check_maven_dep(self, artifact: str) -> bool:
        """Check Maven pom.xml for dependency"""
        if not self.file_exists("pom.xml"):
            return False
        lines = self.read_file_lines("pom.xml", 500)
        return any(artifact in line for line in lines)

    def _check_gradle_dep(self, dep: str) -> bool:
        """Check Gradle build file for dependency"""
        for gradle_file in ["build.gradle", "build.gradle.kts"]:
            if self.file_exists(gradle_file):
                lines = self.read_file_lines(gradle_file, 200)
                if any(dep in line for line in lines):
                    return True
        return False

    def _check_csproj_package(self, package: str) -> bool:
        """Check .NET csproj files for package reference"""
        for csproj in self.project_root.glob("**/*.csproj"):
            lines = self.read_file_lines(
                str(csproj.relative_to(self.project_root)), 100
            )
            if any(f'Include="{package}"' in line for line in lines):
                return True
        return False
