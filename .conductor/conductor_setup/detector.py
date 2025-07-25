"""
Technology Stack Detection Module
Detects programming languages, frameworks, and tools used in a project
"""

import subprocess
from pathlib import Path
from typing import Dict, Any


class TechnologyDetector:
    """Detects technology stack for 90% coverage of real-world projects"""

    def __init__(self, project_root: Path, debug: bool = False):
        self.project_root = project_root
        self.debug = debug
        self.detected_stack = []
        self.config = {}

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
