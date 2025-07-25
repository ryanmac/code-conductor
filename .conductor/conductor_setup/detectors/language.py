"""
Programming language detection
"""

from typing import List
from .base import BaseDetector


class LanguageDetector(BaseDetector):
    """Detects programming languages used in the project"""

    def detect(self) -> List[str]:
        """Detect programming languages based on file patterns"""
        languages = []

        # Python
        if self.file_exists(
            "setup.py",
            "requirements.txt",
            "Pipfile",
            "pyproject.toml",
            "poetry.lock",
            "setup.cfg",
        ) or self.glob_exists("**/*.py"):
            languages.append("python")

        # JavaScript/TypeScript
        if self.file_exists("package.json") or self.glob_exists("**/*.js"):
            languages.append("javascript")
        if self.file_exists("tsconfig.json") or self.glob_exists("**/*.ts"):
            languages.append("typescript")

        # Go
        if self.file_exists("go.mod", "go.sum") or self.glob_exists("**/*.go"):
            languages.append("go")

        # Rust
        if self.file_exists("Cargo.toml", "Cargo.lock") or self.glob_exists("**/*.rs"):
            languages.append("rust")

        # Ruby
        if self.file_exists("Gemfile", "Gemfile.lock") or self.glob_exists("**/*.rb"):
            languages.append("ruby")

        # Java
        if self.file_exists("pom.xml", "build.gradle") or self.glob_exists("**/*.java"):
            languages.append("java")

        # C#
        if self.glob_exists("**/*.csproj") or self.glob_exists("**/*.cs"):
            languages.append("csharp")

        # Swift
        if self.file_exists("Package.swift") or self.glob_exists("**/*.swift"):
            languages.append("swift")

        # Kotlin
        if self.glob_exists("**/*.kt") or self.glob_exists("**/*.kts"):
            languages.append("kotlin")

        # Dart
        if self.file_exists("pubspec.yaml") or self.glob_exists("**/*.dart"):
            languages.append("dart")

        # PHP
        if self.file_exists("composer.json") or self.glob_exists("**/*.php"):
            languages.append("php")

        # C/C++
        if self.file_exists("CMakeLists.txt", "Makefile") or (
            self.glob_exists("**/*.c")
            or self.glob_exists("**/*.cpp")
            or self.glob_exists("**/*.h")
        ):
            languages.append("c/c++")

        # Scala
        if self.file_exists("build.sbt") or self.glob_exists("**/*.scala"):
            languages.append("scala")

        # Elixir
        if self.file_exists("mix.exs") or self.glob_exists("**/*.ex"):
            languages.append("elixir")

        return languages

    def detect_package_managers(self) -> List[str]:
        """Detect package managers in use"""
        managers = []

        # JavaScript/Node.js
        if self.file_exists("package-lock.json"):
            managers.append("npm")
        if self.file_exists("yarn.lock"):
            managers.append("yarn")
        if self.file_exists("pnpm-lock.yaml"):
            managers.append("pnpm")
        if self.file_exists("bun.lockb"):
            managers.append("bun")

        # Python
        if self.file_exists("requirements.txt", "setup.py"):
            managers.append("pip")
        if self.file_exists("Pipfile", "Pipfile.lock"):
            managers.append("pipenv")
        if self.file_exists("poetry.lock", "pyproject.toml"):
            # Check if pyproject.toml has poetry config
            lines = self.read_file_lines("pyproject.toml", 50)
            if any("poetry" in line.lower() for line in lines):
                managers.append("poetry")

        # Ruby
        if self.file_exists("Gemfile", "Gemfile.lock"):
            managers.append("bundler")

        # Go
        if self.file_exists("go.mod"):
            managers.append("go modules")

        # Rust
        if self.file_exists("Cargo.toml"):
            managers.append("cargo")

        # PHP
        if self.file_exists("composer.json"):
            managers.append("composer")

        return managers
