"""
Technology Stack Detection Module - Main Orchestrator
Coordinates sub-detectors for comprehensive project analysis
"""

import subprocess
from pathlib import Path
from typing import Dict, Any

from .cache_manager import get_cache
from .detectors import (
    LanguageDetector,
    FrameworkDetector,
    MonorepoDetector,
    TestFrameworkDetector,
)


class TechnologyDetector:
    """Main orchestrator for technology stack detection"""

    def __init__(self, project_root: Path, debug: bool = False):
        self.project_root = project_root
        self.debug = debug
        self.detected_stack = []
        self.config = {}
        self.cache = get_cache()
        self.project_hash = self.cache.get_project_hash(project_root)

        # Initialize sub-detectors
        self.language_detector = LanguageDetector(project_root, debug)
        self.framework_detector = FrameworkDetector(project_root, debug)
        self.monorepo_detector = MonorepoDetector(project_root, debug)
        self.test_framework_detector = TestFrameworkDetector(project_root, debug)

    def detect_project_info(self) -> Dict[str, Any]:
        """Auto-detect project characteristics"""
        print("\n🔍 Detecting project information...")

        # Git repository detection
        self._detect_git_remote()

        # Technology stack detection
        self._detect_technology_stack()

        # Check for specific patterns
        self._detect_special_patterns()

        return {
            "detected_stack": self.detected_stack,
            "config": self.config,
        }

    def detect_technology_stack(self, ui=None) -> Dict[str, Any]:
        """Enhanced technology stack detection with caching and progress feedback"""
        cache_key = f"tech_stack_{self.project_hash}"

        # Try cache first
        cached_result = self.cache.get(cache_key)
        if cached_result and not self.debug:
            if ui:
                ui.console.print("[dim]Using cached technology detection[/dim]")
            return cached_result

        # Create progress bar if UI is available
        progress = None
        if ui:
            progress = ui.create_progress()
            task = progress.add_task("Analyzing project structure...", total=6)
            progress.start()

        try:
            result = {
                "languages": [],
                "frameworks": [],
                "build_tools": [],
                "package_managers": [],
                "test_frameworks": [],
                "monorepo": {},
                "special_patterns": {},
            }

            # Step 1: Detect languages
            if progress:
                progress.update(task, description="Detecting programming languages...")
            result["languages"] = self.language_detector.detect()
            if progress:
                progress.advance(task)

            # Step 2: Detect package managers
            if progress:
                progress.update(task, description="Detecting package managers...")
            result["package_managers"] = (
                self.language_detector.detect_package_managers()
            )
            if progress:
                progress.advance(task)

            # Step 3: Detect frameworks
            if progress:
                progress.update(task, description="Detecting frameworks...")
            result["frameworks"] = self.framework_detector.detect()
            modern = self.framework_detector.detect_modern_frameworks()
            result["frameworks"].extend(modern.get("frameworks", []))
            result["build_tools"] = modern.get("build_tools", [])
            result["meta_frameworks"] = modern.get("meta_frameworks", [])
            result["ui_libraries"] = modern.get("ui_libraries", [])
            if progress:
                progress.advance(task)

            # Step 4: Detect test frameworks
            if progress:
                progress.update(task, description="Detecting test frameworks...")
            result["test_frameworks"] = self.test_framework_detector.detect()
            if progress:
                progress.advance(task)

            # Step 5: Detect monorepo setup
            if progress:
                progress.update(task, description="Checking for monorepo setup...")
            result["monorepo"] = self.monorepo_detector.detect()
            if progress:
                progress.advance(task)

            # Step 6: Special patterns
            if progress:
                progress.update(task, description="Analyzing special patterns...")
            result["special_patterns"] = self._detect_special_patterns_enhanced()
            if progress:
                progress.advance(task)

            # Cache the result
            self.cache.set(cache_key, result, ttl=300)  # 5 minute cache

            return result

        finally:
            if progress:
                progress.stop()

    def _detect_git_remote(self):
        """Detect git remote URL"""
        if (self.project_root / ".git").exists():
            try:
                result = subprocess.run(
                    ["git", "remote", "get-url", "origin"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                )
                if result.returncode == 0:
                    self.config["git_remote"] = result.stdout.strip()
            except Exception:
                pass

    def _detect_technology_stack(self):
        """Basic technology stack detection for backward compatibility"""
        # Use the enhanced method
        enhanced_result = self.detect_technology_stack()

        # Map to legacy format
        self.detected_stack = []
        for lang in enhanced_result.get("languages", []):
            if lang not in self.detected_stack:
                self.detected_stack.append(lang)
        for fw in enhanced_result.get("frameworks", []):
            if fw not in self.detected_stack:
                self.detected_stack.append(fw)

    def _detect_special_patterns(self):
        """Detect special project patterns for backward compatibility"""
        patterns = self._detect_special_patterns_enhanced()

        # Mobile app detection
        if patterns.get("has_mobile_app"):
            self.config["has_mobile_app"] = True

        # Documentation site
        if patterns.get("has_docs_site"):
            self.config["has_docs_site"] = True

    def _detect_special_patterns_enhanced(self) -> Dict[str, Any]:
        """Enhanced special pattern detection"""
        patterns = {}

        # Mobile app patterns
        if (self.project_root / "ios").exists() and (
            self.project_root / "android"
        ).exists():
            patterns["has_mobile_app"] = True
            patterns["mobile_type"] = "react-native"
        elif (self.project_root / "App.xcodeproj").exists():
            patterns["has_mobile_app"] = True
            patterns["mobile_type"] = "ios"
        elif (
            self.project_root / "app" / "src" / "main" / "AndroidManifest.xml"
        ).exists():
            patterns["has_mobile_app"] = True
            patterns["mobile_type"] = "android"

        # Documentation patterns
        doc_dirs = ["docs", "documentation", "doc"]
        for doc_dir in doc_dirs:
            doc_path = self.project_root / doc_dir
            if doc_path.exists():
                # Check for documentation generators
                if (doc_path / "mkdocs.yml").exists():
                    patterns["has_docs_site"] = True
                    patterns["docs_generator"] = "mkdocs"
                elif (doc_path / "conf.py").exists():
                    patterns["has_docs_site"] = True
                    patterns["docs_generator"] = "sphinx"
                elif any(doc_path.glob("*.md")) or any(doc_path.glob("*.mdx")):
                    patterns["has_docs_site"] = True
                    if (self.project_root / "docusaurus.config.js").exists():
                        patterns["docs_generator"] = "docusaurus"
                    elif (self.project_root / ".vuepress").exists():
                        patterns["docs_generator"] = "vuepress"

        # CI/CD patterns
        if (self.project_root / ".github" / "workflows").exists():
            patterns["ci_cd"] = "github-actions"
        elif (self.project_root / ".gitlab-ci.yml").exists():
            patterns["ci_cd"] = "gitlab"
        elif (self.project_root / "Jenkinsfile").exists():
            patterns["ci_cd"] = "jenkins"
        elif (self.project_root / ".circleci").exists():
            patterns["ci_cd"] = "circleci"

        # Container patterns
        if (self.project_root / "Dockerfile").exists() or any(
            self.project_root.glob("*.dockerfile")
        ):
            patterns["has_docker"] = True
        if (self.project_root / "docker-compose.yml").exists():
            patterns["has_docker_compose"] = True
        if (self.project_root / "kubernetes").exists() or any(
            self.project_root.glob("k8s/**/*.yaml")
        ):
            patterns["has_kubernetes"] = True

        # Infrastructure as Code
        if any(self.project_root.glob("**/*.tf")):
            patterns["iac"] = "terraform"
        elif (self.project_root / "template.yaml").exists() or (
            self.project_root / "serverless.yml"
        ).exists():
            patterns["iac"] = "serverless"
        elif any(self.project_root.glob("**/*.bicep")):
            patterns["iac"] = "bicep"

        return patterns
