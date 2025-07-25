"""
Technology Stack Detection Module
Detects programming languages, frameworks, and tools used in a project
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from .cache_manager import get_cache


class TechnologyDetector:
    """Detects technology stack for 95%+ coverage of real-world projects"""

    def __init__(self, project_root: Path, debug: bool = False):
        self.project_root = project_root
        self.debug = debug
        self.detected_stack = []
        self.config = {}
        self.cache = get_cache()
        self.project_hash = self.cache.get_project_hash(project_root)

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

    def _detect_git_remote(self):
        """Detect git remote URL"""
        if (self.project_root / ".git").exists():
            try:
                result = subprocess.run(
                    ["git", "remote", "get-url", "origin"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode == 0:
                    self.config["git_remote"] = result.stdout.strip()
                    print(f"✓ Git repository: {self.config['git_remote']}")
            except Exception as e:
                if self.debug:
                    print(f"Git remote detection failed: {e}")

    def _detect_technology_stack(self):
        """Detect technology stack based on file indicators"""
        tech_indicators = self._get_tech_indicators()

        for file_pattern, info in tech_indicators.items():
            found = False
            file_to_check = None

            # Handle glob patterns
            if "*" in file_pattern:
                matches = list(self.project_root.glob(file_pattern))
                if matches:
                    found = True
                    file_to_check = matches[0]
            else:
                file_to_check = self.project_root / file_pattern
                if file_to_check.exists():
                    found = True

            if found:
                self._process_tech_indicator(info, file_to_check)

    def _get_tech_indicators(self) -> Dict[str, Dict[str, Any]]:
        """Get technology indicators configuration"""
        return {
            "package.json": {
                "tech": "nodejs",
                "suggested_roles": ["devops"],
                "common_patterns": ["frontend", "backend", "extension"],
                "subtypes": {
                    "react": {
                        "keywords": ["react", "react-dom"],
                        "roles": ["frontend", "ui-designer"],
                    },
                    "nextjs": {"keywords": ["next"], "roles": ["frontend", "devops"]},
                    "vue": {
                        "keywords": ["vue", "@vue/"],
                        "roles": ["frontend", "ui-designer"],
                    },
                    "angular": {
                        "keywords": ["@angular/"],
                        "roles": ["frontend", "ui-designer"],
                    },
                    "svelte": {
                        "keywords": ["svelte", "@sveltejs/"],
                        "roles": ["frontend", "ui-designer"],
                    },
                    "express": {
                        "keywords": ["express"],
                        "roles": ["devops", "security"],
                    },
                    "nest": {"keywords": ["@nestjs/"], "roles": ["devops", "security"]},
                    "electron": {
                        "keywords": ["electron"],
                        "roles": ["frontend", "devops"],
                    },
                    "react-native": {
                        "keywords": ["react-native"],
                        "roles": ["mobile", "frontend"],
                    },
                },
            },
            "requirements.txt": {
                "tech": "python",
                "suggested_roles": ["devops"],
                "common_patterns": ["api", "ml", "automation"],
                "subtypes": {
                    "django": {"keywords": ["django"], "roles": ["devops", "security"]},
                    "flask": {"keywords": ["flask"], "roles": ["devops", "security"]},
                    "fastapi": {
                        "keywords": ["fastapi"],
                        "roles": ["devops", "security"],
                    },
                    "ml": {
                        "keywords": ["tensorflow", "torch", "scikit-learn"],
                        "roles": ["ml-engineer", "data"],
                    },
                    "data": {
                        "keywords": ["pandas", "numpy", "jupyter"],
                        "roles": ["data", "ml-engineer"],
                    },
                },
            },
            "Cargo.toml": {
                "tech": "rust",
                "suggested_roles": ["devops", "security"],
                "common_patterns": ["tauri", "wasm", "cli"],
                "subtypes": {
                    "tauri": {
                        "keywords": ["tauri"],
                        "roles": ["frontend", "devops", "security"],
                    },
                },
            },
            "pom.xml": {
                "tech": "java",
                "suggested_roles": ["devops"],
                "common_patterns": ["spring", "microservice"],
                "subtypes": {
                    "spring": {
                        "keywords": ["spring-boot", "springframework"],
                        "roles": ["devops", "security"],
                    },
                },
            },
            "go.mod": {
                "tech": "go",
                "suggested_roles": ["devops"],
                "common_patterns": ["api", "cli", "microservice"],
                "subtypes": {
                    "gin": {
                        "keywords": ["gin-gonic/gin"],
                        "roles": ["devops", "security"],
                    },
                    "echo": {
                        "keywords": ["labstack/echo"],
                        "roles": ["devops", "security"],
                    },
                    "fiber": {
                        "keywords": ["gofiber/fiber"],
                        "roles": ["devops", "security"],
                    },
                },
            },
            "composer.json": {
                "tech": "php",
                "suggested_roles": ["devops", "security"],
                "common_patterns": ["laravel", "symfony", "wordpress"],
                "subtypes": {
                    "laravel": {
                        "keywords": ["laravel/"],
                        "roles": ["devops", "security"],
                    },
                    "symfony": {
                        "keywords": ["symfony/"],
                        "roles": ["devops", "security"],
                    },
                },
            },
            "*.csproj": {
                "tech": "dotnet",
                "suggested_roles": ["devops", "security"],
                "common_patterns": ["aspnet", "blazor"],
                "subtypes": {
                    "aspnet": {
                        "keywords": ["Microsoft.AspNetCore"],
                        "roles": ["devops", "security"],
                    },
                    "blazor": {
                        "keywords": ["Microsoft.AspNetCore.Components"],
                        "roles": ["frontend", "devops"],
                    },
                },
            },
            "pubspec.yaml": {
                "tech": "flutter",
                "suggested_roles": ["mobile", "frontend"],
                "common_patterns": ["flutter", "dart"],
            },
            "build.gradle": {
                "tech": "kotlin",
                "suggested_roles": ["mobile", "devops"],
                "common_patterns": ["android", "spring"],
            },
        }

    def _process_tech_indicator(self, info: Dict[str, Any], file_to_check: Path):
        """Process a detected technology indicator"""
        # Deep copy to avoid modifying the original
        stack_info = info.copy()

        # Detect subtypes by reading file contents
        if "subtypes" in info and file_to_check and file_to_check.exists():
            try:
                content = file_to_check.read_text(encoding="utf-8")
                detected_subtypes = []
                additional_roles = set()

                for subtype_name, subtype_info in info["subtypes"].items():
                    for keyword in subtype_info["keywords"]:
                        if keyword in content:
                            detected_subtypes.append(subtype_name)
                            additional_roles.update(subtype_info.get("roles", []))
                            break

                if detected_subtypes:
                    stack_info["detected_subtypes"] = detected_subtypes
                    # Merge additional roles from subtypes
                    existing_roles = set(stack_info.get("suggested_roles", []))
                    stack_info["suggested_roles"] = list(
                        existing_roles | additional_roles
                    )

            except Exception as e:
                if self.debug:
                    print(f"Could not read {file_to_check}: {e}")

        self.detected_stack.append(stack_info)
        subtypes_str = ""
        if "detected_subtypes" in stack_info:
            subtypes_str = f" ({', '.join(stack_info['detected_subtypes'])})"
        print(f"✓ Detected {info['tech']} project{subtypes_str}")

    def _detect_special_patterns(self):
        """Detect special project patterns"""
        if (self.project_root / "manifest.json").exists():
            print("✓ Detected Chrome extension")
            self.config["has_extension"] = True

    def detect_technology_stack(self, ui: Optional[Any] = None) -> Dict[str, Any]:
        """Enhanced detection with caching and UI support"""
        # Check cache first
        cache_key = f"stack_{self.project_hash}"
        cached_result = self.cache.get(cache_key)
        if cached_result:
            if ui:
                ui.console.print(
                    "[conductor.info]Using cached detection results[/conductor.info]"
                )
            return cached_result

        result = {}

        if ui:
            with ui.create_progress() as progress:
                # Total of 6 detection phases
                task = progress.add_task("Analyzing project", total=6)

                # Phase 1: Package managers
                progress.update(
                    task, advance=1, description="Detecting package managers..."
                )
                result["package_managers"] = self._detect_package_managers()

                # Phase 2: Traditional frameworks
                progress.update(
                    task, advance=1, description="Identifying frameworks..."
                )
                result["frameworks"] = self._detect_frameworks()

                # Phase 3: Modern tools
                progress.update(
                    task, advance=1, description="Checking modern tooling..."
                )
                result["modern_tools"] = self._detect_modern_frameworks()

                # Phase 4: Test frameworks
                progress.update(
                    task, advance=1, description="Finding test frameworks..."
                )
                result["test_frameworks"] = self._detect_test_frameworks()

                # Phase 5: Monorepo setup
                progress.update(
                    task, advance=1, description="Analyzing project structure..."
                )
                result["monorepo"] = self._detect_monorepo_setup()

                # Phase 6: Compile results
                progress.update(task, advance=1, description="Finalizing detection...")
                result["summary"] = self._compile_detection_summary(result)
        else:
            # No UI, just run detection
            result["package_managers"] = self._detect_package_managers()
            result["frameworks"] = self._detect_frameworks()
            result["modern_tools"] = self._detect_modern_frameworks()
            result["test_frameworks"] = self._detect_test_frameworks()
            result["monorepo"] = self._detect_monorepo_setup()
            result["summary"] = self._compile_detection_summary(result)

        # Cache for next time (24 hour TTL)
        self.cache.set(cache_key, result, ttl=86400)

        return result

    def _detect_package_managers(self) -> List[str]:
        """Detect package managers in use"""
        managers = []

        if (self.project_root / "package.json").exists():
            managers.append("npm")
            if (self.project_root / "yarn.lock").exists():
                managers.append("yarn")
            if (self.project_root / "pnpm-lock.yaml").exists():
                managers.append("pnpm")

        if (self.project_root / "requirements.txt").exists():
            managers.append("pip")
        if (self.project_root / "Pipfile").exists():
            managers.append("pipenv")
        if (self.project_root / "poetry.lock").exists():
            managers.append("poetry")

        if (self.project_root / "Cargo.toml").exists():
            managers.append("cargo")

        if (self.project_root / "go.mod").exists():
            managers.append("go modules")

        if (self.project_root / "pom.xml").exists():
            managers.append("maven")
        if (self.project_root / "build.gradle").exists():
            managers.append("gradle")

        return managers

    def _detect_frameworks(self) -> List[str]:
        """Detect traditional frameworks"""
        frameworks = []

        # Run existing detection logic
        self._detect_technology_stack()

        # Extract frameworks from detected stack
        for item in self.detected_stack:
            if "detected_subtypes" in item:
                frameworks.extend(item["detected_subtypes"])
            frameworks.append(item["tech"])

        return list(set(frameworks))

    def _detect_modern_frameworks(self) -> Dict[str, Any]:
        """Detect modern web frameworks and tools"""
        detections = {}

        # Vite-based projects
        vite_config_files = ["vite.config.js", "vite.config.ts", "vite.config.mjs"]
        for config_file in vite_config_files:
            if (self.project_root / config_file).exists():
                detections["build_tool"] = "vite"
                detections["modern_tooling"] = True

                # Read config to detect framework
                try:
                    config_content = (self.project_root / config_file).read_text()
                    if "@vitejs/plugin-react" in config_content:
                        detections["framework_plugin"] = "react"
                    elif "@vitejs/plugin-vue" in config_content:
                        detections["framework_plugin"] = "vue"
                    elif "@sveltejs/vite-plugin-svelte" in config_content:
                        detections["framework_plugin"] = "svelte"
                except Exception:
                    pass
                break

        # Remix detection
        if (self.project_root / "remix.config.js").exists():
            detections["framework"] = "remix"
            detections["fullstack"] = True

        # Astro detection
        if (self.project_root / "astro.config.mjs").exists():
            detections["framework"] = "astro"
            detections["static_site_generator"] = True

        # SvelteKit detection
        if (self.project_root / "svelte.config.js").exists():
            try:
                config_content = (self.project_root / "svelte.config.js").read_text()
                if "@sveltejs/kit" in config_content:
                    detections["framework"] = "sveltekit"
                    detections["fullstack"] = True
            except Exception:
                pass

        # Nuxt 3 detection
        if (self.project_root / "nuxt.config.ts").exists():
            detections["framework"] = "nuxt3"
            detections["fullstack"] = True

        # Qwik detection
        if (self.project_root / "qwik.config.ts").exists():
            detections["framework"] = "qwik"
            detections["modern_tooling"] = True

        # Bun detection
        if (self.project_root / "bun.lockb").exists():
            detections["runtime"] = "bun"
            detections["package_manager"] = "bun"

        # Turbopack/Turborepo detection
        if (self.project_root / "turbo.json").exists():
            detections["build_tool"] = "turborepo"
            detections["monorepo_tool"] = True

        return detections

    def _detect_test_frameworks(self) -> List[str]:
        """Detect testing frameworks in use"""
        test_frameworks = []

        # JavaScript/TypeScript testing
        if (self.project_root / "jest.config.js").exists() or (
            self.project_root / "jest.config.ts"
        ).exists():
            test_frameworks.append("jest")

        if (self.project_root / "vitest.config.ts").exists():
            test_frameworks.append("vitest")

        if (self.project_root / "cypress.config.js").exists() or (
            self.project_root / "cypress.config.ts"
        ).exists():
            test_frameworks.append("cypress")

        if (self.project_root / "playwright.config.ts").exists():
            test_frameworks.append("playwright")

        # Python testing
        if (self.project_root / "pytest.ini").exists():
            test_frameworks.append("pytest")
        elif (self.project_root / "setup.cfg").exists():
            try:
                content = (self.project_root / "setup.cfg").read_text()
                if "[tool:pytest]" in content:
                    test_frameworks.append("pytest")
            except Exception:
                pass

        # Check package.json for test runners
        if (self.project_root / "package.json").exists():
            try:
                package_json = json.loads(
                    (self.project_root / "package.json").read_text()
                )
                dev_deps = package_json.get("devDependencies", {})
                deps = package_json.get("dependencies", {})
                all_deps = {**deps, **dev_deps}

                test_runners = {
                    "@testing-library/react": "testing-library",
                    "@testing-library/vue": "testing-library",
                    "@testing-library/angular": "testing-library",
                    "mocha": "mocha",
                    "jasmine": "jasmine",
                    "ava": "ava",
                    "tape": "tape",
                    "qunit": "qunit",
                }

                for package, framework in test_runners.items():
                    if package in all_deps:
                        test_frameworks.append(framework)
            except Exception:
                pass

        # Rust testing (built-in)
        if (self.project_root / "Cargo.toml").exists():
            test_frameworks.append("rust-test")

        # Go testing (built-in)
        if (self.project_root / "go.mod").exists():
            test_frameworks.append("go-test")

        return list(set(test_frameworks))

    def _detect_monorepo_setup(self) -> Dict[str, Any]:
        """Detect monorepo tools and structure"""
        monorepo_info = {}

        # pnpm workspaces
        if (self.project_root / "pnpm-workspace.yaml").exists():
            monorepo_info["tool"] = "pnpm"
            try:
                # Simple workspace count - just count directories in common patterns
                workspace_count = 0
                for pattern in ["packages/*", "apps/*", "libs/*"]:
                    workspace_count += len(list(self.project_root.glob(pattern)))
                monorepo_info["workspace_count"] = workspace_count
            except Exception:
                monorepo_info["workspace_count"] = 0

        # Nx monorepo
        elif (self.project_root / "nx.json").exists():
            monorepo_info["tool"] = "nx"
            try:
                nx_config = json.loads((self.project_root / "nx.json").read_text())
                monorepo_info["workspace_count"] = len(nx_config.get("projects", {}))
            except Exception:
                monorepo_info["workspace_count"] = 0

        # Lerna
        elif (self.project_root / "lerna.json").exists():
            monorepo_info["tool"] = "lerna"
            try:
                lerna_config = json.loads(
                    (self.project_root / "lerna.json").read_text()
                )
                monorepo_info["workspace_count"] = len(lerna_config.get("packages", []))
            except Exception:
                monorepo_info["workspace_count"] = 0

        # Rush
        elif (self.project_root / "rush.json").exists():
            monorepo_info["tool"] = "rush"

        # Yarn workspaces
        elif (self.project_root / "package.json").exists():
            try:
                package_json = json.loads(
                    (self.project_root / "package.json").read_text()
                )
                if "workspaces" in package_json:
                    monorepo_info["tool"] = "yarn"
                    workspaces = package_json["workspaces"]
                    if isinstance(workspaces, list):
                        monorepo_info["workspace_count"] = len(workspaces)
                    elif isinstance(workspaces, dict) and "packages" in workspaces:
                        monorepo_info["workspace_count"] = len(workspaces["packages"])
            except Exception:
                pass

        return monorepo_info

    def _compile_detection_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Compile a summary of all detections"""
        summary = {
            "languages": [],
            "frameworks": [],
            "tools": [],
            "primary_stack": None,
            "complexity": "simple",
        }

        # Extract languages from frameworks
        framework_to_language = {
            "nodejs": "JavaScript",
            "react": "JavaScript",
            "vue": "JavaScript",
            "angular": "TypeScript",
            "python": "Python",
            "django": "Python",
            "flask": "Python",
            "fastapi": "Python",
            "rust": "Rust",
            "go": "Go",
            "java": "Java",
            "dotnet": "C#",
            "php": "PHP",
            "flutter": "Dart",
            "kotlin": "Kotlin",
        }

        for framework in result.get("frameworks", []):
            if framework in framework_to_language:
                summary["languages"].append(framework_to_language[framework])

        summary["languages"] = list(set(summary["languages"]))
        summary["frameworks"] = result.get("frameworks", [])

        # Add modern tools
        if result.get("modern_tools", {}).get("build_tool"):
            summary["tools"].append(result["modern_tools"]["build_tool"])

        # Determine complexity
        if result.get("monorepo"):
            summary["complexity"] = "monorepo"
        elif len(summary["frameworks"]) > 3:
            summary["complexity"] = "complex"
        elif len(summary["frameworks"]) > 1:
            summary["complexity"] = "moderate"

        # Determine primary stack
        if "react" in summary["frameworks"] or "nextjs" in summary["frameworks"]:
            summary["primary_stack"] = "react-typescript"
        elif "vue" in summary["frameworks"] or "nuxt3" in result.get(
            "modern_tools", {}
        ).get("framework", ""):
            summary["primary_stack"] = "vue-javascript"
        elif "fastapi" in summary["frameworks"]:
            summary["primary_stack"] = "python-fastapi"
        elif "django" in summary["frameworks"]:
            summary["primary_stack"] = "python-django"
        elif "express" in summary["frameworks"]:
            summary["primary_stack"] = "node-express"
        elif summary["languages"]:
            summary["primary_stack"] = summary["languages"][0].lower()

        return summary
