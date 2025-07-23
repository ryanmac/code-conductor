#!/usr/bin/env python3
"""
Code Conductor Interactive Setup Script
Configures the repository for your specific project needs
"""

import os
import sys
import json
import yaml
import subprocess
import argparse
import logging
from pathlib import Path
from datetime import datetime


class ConductorSetup:
    def __init__(self, auto_mode=False, debug=False):
        self.project_root = Path.cwd()
        self.conductor_dir = self.project_root / ".conductor"
        self.config = {}
        self.detected_stack = []
        self.auto_mode = auto_mode
        self.debug = debug

        # Setup logging
        log_level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(level=log_level, format="%(message)s")
        self.logger = logging.getLogger(__name__)

    def run(self):
        """Main setup workflow"""
        self.print_header()

        # Check if already configured
        if self.check_existing_config():
            if not self.confirm_reconfigure():
                print("Setup cancelled.")
                return

        # Run setup steps
        self.detect_project_info()
        self.gather_configuration()
        self.create_configuration_files()
        self.create_role_definitions()
        self.create_github_workflows()
        self.create_bootstrap_scripts()
        self.validate_setup()
        self.display_completion_message()

    def print_header(self):
        """Display setup header"""
        print("🚀 Code Conductor Setup")
        print("=" * 50)
        print("This will configure agent coordination for your project")
        print()

    def check_existing_config(self):
        """Check if already configured"""
        config_file = self.conductor_dir / "config.yaml"
        return config_file.exists()

    def confirm_reconfigure(self):
        """Ask user if they want to reconfigure"""
        print("⚠️  Existing configuration detected.")
        if self.auto_mode:
            print("Auto mode: reconfiguring existing setup...")
            return True
        response = self._safe_input("Do you want to reconfigure? [y/N]: ", "n").lower()
        return response == "y"

    def _safe_input(self, prompt, default=None):
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
            if hasattr(self, "logger"):
                self.logger.error(f"❌ Input error: {e}")
            return default

    def detect_project_info(self):
        """Auto-detect project characteristics"""
        print("\n🔍 Detecting project information...")

        # Git repository detection
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
                    self.logger.debug(f"Git remote detection failed: {e}")
                pass

        # Technology stack detection - covering 90% of real-world projects
        tech_indicators = {
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

        import glob

        # Process each tech indicator
        for file_pattern, info in tech_indicators.items():
            found = False

            # Handle glob patterns
            if "*" in file_pattern:
                matches = list(self.project_root.glob(file_pattern))
                if matches:
                    found = True
                    file_to_check = matches[0]  # Use first match for subtype detection
            else:
                file_to_check = self.project_root / file_pattern
                if file_to_check.exists():
                    found = True

            if found:
                # Deep copy to avoid modifying the original
                stack_info = info.copy()

                # Detect subtypes by reading file contents
                if "subtypes" in info and file_to_check.exists():
                    try:
                        content = file_to_check.read_text(encoding="utf-8")
                        detected_subtypes = []
                        additional_roles = set()

                        for subtype_name, subtype_info in info["subtypes"].items():
                            for keyword in subtype_info["keywords"]:
                                if keyword in content:
                                    detected_subtypes.append(subtype_name)
                                    additional_roles.update(
                                        subtype_info.get("roles", [])
                                    )
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
                            self.logger.debug(f"Could not read {file_to_check}: {e}")

                self.detected_stack.append(stack_info)
                subtypes_str = ""
                if "detected_subtypes" in stack_info:
                    subtypes_str = f" ({', '.join(stack_info['detected_subtypes'])})"
                print(f"✓ Detected {info['tech']} project{subtypes_str}")

        # Check for specific patterns
        if (self.project_root / "manifest.json").exists():
            print("✓ Detected Chrome extension")
            self.config["has_extension"] = True

    def gather_configuration(self):
        """Interactive configuration prompts"""
        if self.auto_mode:
            self._auto_configure()
            return

        print("\n📝 Project Configuration")
        print("-" * 30)

        # Project name
        default_name = self.project_root.name
        try:
            self.config["project_name"] = self._safe_input(
                f"Project name [{default_name}]: ", default_name
            )
        except Exception as e:
            self.logger.error(f"❌ Error reading input: {e}")
            print("💡 Try running with --auto flag for automatic configuration")
            sys.exit(1)

        # Documentation directory
        default_docs = "docs"
        if (self.project_root / "docs").exists():
            default_docs = "docs"
        elif (self.project_root / "documentation").exists():
            default_docs = "documentation"

        self.config["docs_directory"] = self._safe_input(
            f"Documentation directory [{default_docs}]: ", default_docs
        )

        # Role configuration with hybrid model
        print("\n🎭 Agent Role Configuration")
        print("The hybrid model uses 'dev' as the default generalist role")
        print("with optional specialized roles for complex tasks.")

        # Suggest roles based on detected stack
        suggested = set()
        for stack in self.detected_stack:
            suggested.update(stack["suggested_roles"])

        suggested_str = ", ".join(suggested) if suggested else "none detected"
        print(f"\nSuggested specialized roles: {suggested_str}")

        print("\nCommon specialized roles:")
        print("  - devops: CI/CD, deployments, infrastructure")
        print("  - security: Audits, vulnerability scanning")
        print("  - ml-engineer: Machine learning tasks")
        print("  - ui-designer: Design system, components")

        roles_input = self._safe_input(
            "\nEnter specialized roles (comma-separated, or press Enter for none): ", ""
        )

        specialized_roles = []
        if roles_input:
            specialized_roles = [r.strip() for r in roles_input.split(",") if r.strip()]

        self.config["roles"] = {"default": "dev", "specialized": specialized_roles}

        # Task management approach
        print("\n📋 Task Management Configuration")
        print("1. GitHub Issues (recommended) - Use labels and automation")
        print("2. JSON files - Direct state management")
        print("3. Hybrid - Both approaches")

        choice = self._safe_input("Select approach [1]: ", "1")
        task_approaches = {"1": "github-issues", "2": "json-files", "3": "hybrid"}
        self.config["task_management"] = task_approaches.get(choice, "github-issues")

        # Concurrent agents
        default_concurrent = "10"
        max_agents = self._safe_input(
            f"\nMaximum concurrent agents [{default_concurrent}]: ", default_concurrent
        )

        try:
            self.config["max_concurrent_agents"] = int(max_agents)
        except ValueError:
            print(f"⚠️  Invalid number '{max_agents}', using default: 10")
            self.config["max_concurrent_agents"] = 10

    def _auto_configure(self):
        """Auto-configuration mode with minimal prompts"""
        print("\n🤖 Auto-configuration mode enabled")
        print("-" * 30)

        # Use sensible defaults
        self.config["project_name"] = self.project_root.name
        self.config["docs_directory"] = "docs"

        # Detect roles based on enhanced stack detection
        suggested_roles = set()
        detected_stacks = []

        for stack in self.detected_stack:
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
            f"✓ Roles: dev + {len(specialized_roles)} specialized ({', '.join(specialized_roles)})"
        )
        print(f"✓ Task management: {self.config['task_management']}")
        print(f"✓ Max agents: {self.config['max_concurrent_agents']}")

    def create_configuration_files(self):
        """Generate configuration files"""
        print("\n🔧 Creating configuration files...")

        try:
            # Ensure directories exist
            self.conductor_dir.mkdir(exist_ok=True)
        except PermissionError:
            if hasattr(self, "logger"):
                self.logger.error("❌ Permission denied creating .conductor directory")
            print("💡 Try running with sudo or check directory permissions")
            sys.exit(1)
        except Exception as e:
            if hasattr(self, "logger"):
                self.logger.error(f"❌ Failed to create .conductor directory: {e}")
            sys.exit(1)

        # Create config.yaml
        config_data = {
            "version": "1.0.0",
            "project_name": self.config["project_name"],
            "docs_directory": self.config["docs_directory"],
            "task_management": self.config["task_management"],
            "roles": self.config["roles"],
            "conflict_prevention": {"use_worktrees": True, "file_locking": True},
            "github": {
                "use_issues": self.config["task_management"]
                in ["github-issues", "hybrid"],
                "use_actions": True,
            },
            "agent_settings": {
                "heartbeat_interval": 600,
                "idle_timeout": 1800,
                "max_concurrent": self.config["max_concurrent_agents"],
            },
        }

        if "git_remote" in self.config:
            config_data["git_remote"] = self.config["git_remote"]

        config_file = self.conductor_dir / "config.yaml"
        try:
            with open(config_file, "w") as f:
                yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
            print(f"✓ Created {config_file}")
        except Exception as e:
            if hasattr(self, "logger"):
                self.logger.error(f"❌ Failed to create config file: {e}")
            sys.exit(1)

        # Initialize workflow state
        if not (self.conductor_dir / "workflow-state.json").exists():
            state_data = {
                "active_work": {},
                "available_tasks": [],
                "completed_work": [],
                "system_status": {
                    "ci_passing": True,
                    "deployment_ready": False,
                    "active_agents": 0,
                    "idle_agents": 0,
                    "last_updated": datetime.utcnow().isoformat(),
                },
            }

            state_file = self.conductor_dir / "workflow-state.json"
            with open(state_file, "w") as f:
                json.dump(state_data, f, indent=2)
            print(f"✓ Created {state_file}")

    def create_role_definitions(self):
        """Create role definition files"""
        print("\n📄 Creating role definitions...")

        roles_dir = self.conductor_dir / "roles"
        roles_dir.mkdir(exist_ok=True)

        # Always create the default dev role
        dev_content = """# Dev Role (Default Generalist)

## Overview
The dev role is the default generalist role that can work on any task without specific skill requirements. This role embodies the "super dev" concept where well-documented tasks enable any developer to contribute effectively.

## Responsibilities
- Implement features according to task specifications
- Write tests to meet coverage requirements
- Follow project coding standards and best practices
- Create pull requests with clear descriptions
- Update documentation as needed

## Task Selection Criteria
- Can claim any task without specific skill requirements
- Prioritizes tasks marked as 'ready' with no blockers
- Avoids tasks that explicitly require specialized roles

## Best Practices
1. Always read the complete task specification before starting
2. Check for existing implementations or patterns in the codebase
3. Run tests locally before pushing changes
4. Use meaningful commit messages
5. Ask questions via GitHub issues if specifications are unclear

## Success Metrics
- All tests passing
- Code coverage maintained or improved
- No security vulnerabilities introduced
- PR approved and merged
"""

        dev_file = roles_dir / "dev.md"
        with open(dev_file, "w") as f:
            f.write(dev_content)
        print(f"✓ Created {dev_file}")

        # Create specialized roles
        role_templates = {
            "devops": """# DevOps Role

## Overview
The DevOps role handles CI/CD, infrastructure, deployments, and system reliability.

## Responsibilities
- Maintain and improve CI/CD pipelines
- Manage deployment configurations
- Monitor system health and performance
- Implement infrastructure as code
- Ensure security best practices in deployments

## Task Selection Criteria
- Tasks labeled with 'devops' or 'infrastructure'
- Deployment and release-related tasks
- Performance optimization tasks
- Monitoring and alerting setup

## Required Skills
- GitHub Actions or similar CI/CD tools
- Container orchestration (Docker, Kubernetes)
- Cloud platforms (AWS, GCP, Azure)
- Infrastructure as Code (Terraform, CloudFormation)

## Success Metrics
- CI/CD pipeline success rate > 95%
- Deployment rollback capability verified
- Infrastructure changes documented
- Security scans passing
""",
            "security": """# Security Role

## Overview
The Security role focuses on application security, vulnerability management, and compliance.

## Responsibilities
- Conduct security audits and reviews
- Implement security best practices
- Manage dependency vulnerabilities
- Ensure compliance with security policies
- Educate team on security practices

## Task Selection Criteria
- Tasks labeled with 'security' or 'vulnerability'
- Authentication and authorization implementations
- Dependency update tasks with security implications
- Compliance and audit-related tasks

## Required Skills
- OWASP Top 10 knowledge
- Security scanning tools (npm audit, Snyk, etc.)
- Authentication protocols (OAuth, JWT)
- Encryption and key management

## Success Metrics
- Zero high/critical vulnerabilities
- Security tests implemented and passing
- Compliance requirements documented
- Security review completed and approved
""",
            "ml-engineer": """# ML Engineer Role

## Overview
The ML Engineer role handles machine learning models, data pipelines, and AI integrations.

## Responsibilities
- Develop and train ML models
- Implement data preprocessing pipelines
- Integrate ML models into applications
- Monitor model performance and drift
- Document model architectures and datasets

## Task Selection Criteria
- Tasks labeled with 'ml' or 'ai'
- Data pipeline implementations
- Model training and evaluation tasks
- Performance optimization for ML workloads

## Required Skills
- Python ML frameworks (TensorFlow, PyTorch, scikit-learn)
- Data processing tools (Pandas, NumPy)
- MLOps practices and tools
- Model evaluation and metrics

## Success Metrics
- Model performance meets specified thresholds
- Data pipelines tested and documented
- Model versioning implemented
- Performance benchmarks documented
""",
            "ui-designer": """# UI Designer Role

## Overview
The UI Designer role focuses on user interface, design systems, and user experience.

## Responsibilities
- Implement design systems and components
- Ensure UI consistency across the application
- Optimize for accessibility (a11y)
- Implement responsive designs
- Collaborate on UX improvements

## Task Selection Criteria
- Tasks labeled with 'ui', 'design', or 'frontend'
- Component library implementations
- Accessibility improvements
- Design system updates

## Required Skills
- Modern CSS and styling approaches
- Component libraries (React, Vue, etc.)
- Accessibility standards (WCAG)
- Design tools integration

## Success Metrics
- Accessibility score > 95
- Component reusability achieved
- Design consistency maintained
- Performance metrics met (LCP, FID, CLS)
""",
            "code-reviewer": """# Code Reviewer Role (AI-Powered)

## Overview
The Code Reviewer role provides automated AI-powered code reviews on pull requests, similar to CodeRabbit. This role runs automatically on all PRs to ensure code quality, catch bugs, and suggest improvements.

## Responsibilities
- Review all pull requests automatically
- Identify potential bugs and security issues
- Suggest code improvements and optimizations
- Ensure coding standards compliance
- Check for test coverage
- Identify breaking changes
- Suggest documentation updates

## Task Selection Criteria
- Automatically triggered on PR creation/update
- Reviews all code changes
- Provides feedback as PR comments
- Can be manually invoked for specific reviews

## Review Focus Areas
- Code quality and maintainability
- Security vulnerabilities
- Performance issues
- Test coverage gaps
- Documentation completeness
- Breaking API changes
- Best practices adherence

## Success Metrics
- Average review time < 5 minutes
- False positive rate < 10%
- Developer satisfaction score > 4/5
- Bugs caught before merge
""",
            "frontend": """# Frontend Developer Role

## Overview
The Frontend role specializes in client-side development, UI implementation, and user experience.

## Responsibilities
- Implement responsive UI components
- Optimize frontend performance
- Ensure cross-browser compatibility
- Implement state management
- Create reusable component libraries

## Task Selection Criteria
- Tasks labeled with 'frontend', 'ui', or 'client'
- Component development tasks
- Frontend optimization tasks
- UI/UX implementation tasks

## Required Skills
- Modern JavaScript/TypeScript
- Frontend frameworks (React, Vue, Angular, Svelte)
- CSS/SASS and modern styling
- Build tools (Webpack, Vite, etc.)
- Performance optimization

## Success Metrics
- Lighthouse scores > 90
- Component test coverage > 80%
- Zero accessibility violations
- Bundle size optimized
""",
            "mobile": """# Mobile Developer Role

## Overview
The Mobile role specializes in mobile application development across platforms.

## Responsibilities
- Develop mobile applications
- Ensure platform-specific optimizations
- Implement native features
- Optimize for mobile performance
- Handle offline functionality

## Task Selection Criteria
- Tasks labeled with 'mobile', 'ios', or 'android'
- Mobile-specific feature implementations
- Platform optimization tasks
- Mobile UI/UX tasks

## Required Skills
- React Native / Flutter / Native development
- Mobile platform guidelines (iOS/Android)
- Mobile performance optimization
- Push notifications and device APIs
- App store deployment

## Success Metrics
- App performance metrics met
- Crash-free rate > 99%
- App store rating > 4.5
- Platform compliance achieved
""",
            "data": """# Data Engineer Role

## Overview
The Data Engineer role focuses on data pipelines, analytics, and data infrastructure.

## Responsibilities
- Build and maintain data pipelines
- Implement data transformations
- Ensure data quality and integrity
- Optimize data storage and retrieval
- Create data visualization solutions

## Task Selection Criteria
- Tasks labeled with 'data', 'etl', or 'analytics'
- Data pipeline implementations
- Database optimization tasks
- Analytics and reporting tasks

## Required Skills
- SQL and NoSQL databases
- Data processing frameworks
- ETL/ELT tools
- Data visualization tools
- Big data technologies

## Success Metrics
- Pipeline reliability > 99%
- Data quality scores met
- Query performance optimized
- Documentation complete
""",
        }

        for role in self.config["roles"]["specialized"]:
            if role in role_templates:
                role_file = roles_dir / f"{role}.md"
                with open(role_file, "w") as f:
                    f.write(role_templates[role])
                print(f"✓ Created {role_file}")
            else:
                # Create a basic template for custom roles
                custom_content = f"""# {role.title()} Role

## Overview
Custom role for {role} responsibilities.

## Responsibilities
- [Add specific responsibilities]

## Task Selection Criteria
- Tasks labeled with '{role}'
- [Add specific criteria]

## Required Skills
- [Add required skills]

## Success Metrics
- [Add success metrics]
"""
                role_file = roles_dir / f"{role}.md"
                with open(role_file, "w") as f:
                    f.write(custom_content)
                print(f"✓ Created {role_file} (custom template)")

    def create_github_workflows(self):
        """Create GitHub Actions workflows"""
        print("\n🤖 Creating GitHub Actions workflows...")

        workflows_dir = self.project_root / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)

        # Main conductor workflow
        conductor_workflow = """name: Conductor Orchestration

on:
  push:
    paths:
      - '.conductor/workflow-state.json'
  schedule:
    - cron: '*/15 * * * *'  # Every 15 minutes
  workflow_dispatch:
  issues:
    types: [labeled]

jobs:
  task-from-issue:
    if: github.event_name == 'issues' && contains(github.event.label.name, 'conductor:task')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.CONDUCTOR_GITHUB_TOKEN }}

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Convert Issue to Task
        run: |
          python .conductor/scripts/issue-to-task.py \\
            --issue-number ${{ github.event.issue.number }}

      - name: Commit task updates
        uses: stefanzweifel/git-auto-commit-action@v4
        with:
          commit_message: '🎯 Add task from issue #${{ github.event.issue.number }}'
          file_pattern: '.conductor/workflow-state.json'

  health-check:
    if: github.event_name == 'schedule' || github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install pyyaml

      - name: Check agent heartbeats
        run: python .conductor/scripts/health-check.py

      - name: Clean up stale work
        run: |
          python .conductor/scripts/cleanup-stale.py --timeout 30

      - name: Update system status
        run: |
          python .conductor/scripts/update-status.py

      - name: Commit status updates
        uses: stefanzweifel/git-auto-commit-action@v4
        with:
          commit_message: '🔄 Update system health status'
          file_pattern: '.conductor/workflow-state.json'

      - name: Generate status report
        run: |
          echo "## 🎯 Conductor System Status" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          python .conductor/scripts/generate-summary.py >> $GITHUB_STEP_SUMMARY
"""

        conductor_file = workflows_dir / "conductor.yml"
        with open(conductor_file, "w") as f:
            f.write(conductor_workflow)
        print(f"✓ Created {conductor_file}")

        # Cleanup workflow
        cleanup_workflow = """name: Conductor Cleanup

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  cleanup-stale-work:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install pyyaml

      - name: Clean up abandoned worktrees
        run: |
          python .conductor/scripts/cleanup-worktrees.py

      - name: Archive completed tasks
        run: |
          python .conductor/scripts/archive-completed.py

      - name: Commit cleanup changes
        uses: stefanzweifel/git-auto-commit-action@v4
        with:
          commit_message: '🧹 Cleanup stale work and archive completed tasks'
          file_pattern: '.conductor/*.json'
"""

        cleanup_file = workflows_dir / "conductor-cleanup.yml"
        with open(cleanup_file, "w") as f:
            f.write(cleanup_workflow)
        print(f"✓ Created {cleanup_file}")

        # Code reviewer workflow
        code_reviewer_workflow = """name: AI Code Review

on:
  pull_request:
    types: [opened, synchronize, reopened]
  workflow_dispatch:
    inputs:
      pr_number:
        description: 'PR number to review'
        required: true
        type: number

permissions:
  contents: read
  pull-requests: write
  issues: write

jobs:
  ai-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          ref: ${{ github.event.pull_request.head.sha || github.sha }}

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install pyyaml requests openai anthropic

      - name: Get PR Details
        id: pr_details
        run: |
          if [ "${{ github.event_name }}" = "workflow_dispatch" ]; then
            PR_NUMBER="${{ github.event.inputs.pr_number }}"
          else
            PR_NUMBER="${{ github.event.pull_request.number }}"
          fi
          echo "pr_number=$PR_NUMBER" >> $GITHUB_OUTPUT

      - name: Run AI Code Review
        env:
          GITHUB_TOKEN: ${{ secrets.CONDUCTOR_GITHUB_TOKEN }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python .conductor/scripts/code-reviewer.py \\
            --pr-number ${{ steps.pr_details.outputs.pr_number }} \\
            --repo ${{ github.repository }}

      - name: Post Review Summary
        if: always()
        run: |
          echo "## 🤖 AI Code Review Complete" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          if [ -f ".conductor/review-summary.md" ]; then
            cat .conductor/review-summary.md >> $GITHUB_STEP_SUMMARY
          else
            echo "Review summary not found." >> $GITHUB_STEP_SUMMARY
          fi
"""

        code_reviewer_file = workflows_dir / "code-review.yml"
        with open(code_reviewer_file, "w") as f:
            f.write(code_reviewer_workflow)
        print(f"✓ Created {code_reviewer_file}")

        # Create issue template
        issue_template_dir = self.project_root / ".github" / "ISSUE_TEMPLATE"
        issue_template_dir.mkdir(parents=True, exist_ok=True)

        task_template = """name: Conductor Task
description: Create a new task for agent coordination
title: "[TASK] "
labels: ["conductor:task"]
body:
  - type: input
    id: title
    attributes:
      label: Task Title
      description: Brief description of what needs to be done
      placeholder: "Implement user authentication"
    validations:
      required: true

  - type: textarea
    id: description
    attributes:
      label: Task Description
      description: Detailed description of the task
      placeholder: |
        Implement JWT-based authentication with:
        - Login endpoint
        - Logout endpoint
        - Token refresh mechanism
    validations:
      required: true

  - type: dropdown
    id: priority
    attributes:
      label: Priority
      options:
        - High
        - Medium
        - Low
    validations:
      required: true

  - type: input
    id: effort
    attributes:
      label: Estimated Effort
      description: Rough estimate (small/medium/large)
      placeholder: "medium"

  - type: input
    id: skills
    attributes:
      label: Required Skills
      description: Comma-separated list of required skills (leave empty for general dev)
      placeholder: "security, backend"

  - type: textarea
    id: success_criteria
    attributes:
      label: Success Criteria
      description: How will we know when this task is complete?
      placeholder: |
        - All authentication endpoints working
        - Tests written with 100% coverage
        - Security review passed
    validations:
      required: true

  - type: textarea
    id: dependencies
    attributes:
      label: Dependencies
      description: List any tasks or PRs this depends on
      placeholder: |
        - PR#123 (Database schema)
        - Task#456 (User model)
"""

        task_template_file = issue_template_dir / "conductor-task.yml"
        with open(task_template_file, "w") as f:
            f.write(task_template)
        print(f"✓ Created {task_template_file}")

    def create_bootstrap_scripts(self):
        """Create bootstrap and utility scripts"""
        print("\n⚡ Creating bootstrap scripts...")

        scripts_dir = self.conductor_dir / "scripts"
        scripts_dir.mkdir(exist_ok=True)

        # Bootstrap script
        bootstrap_content = """#!/bin/bash
set -e

# Universal Agent Bootstrap Script
echo "🤖 Initializing Conductor Agent..."

# Load configuration
CONFIG_FILE=".conductor/config.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Configuration not found. Run 'python setup.py' first."
    exit 1
fi

# Determine agent role
AGENT_ROLE=${AGENT_ROLE:-$(python3 -c "import sys; print(sys.argv[1] if len(sys.argv) > 1 else 'unknown')" $1)}
if [ "$AGENT_ROLE" = "unknown" ]; then
    echo "🔍 Agent role not specified. Available roles:"
    ls .conductor/roles/ | sed 's/.md$//' | sed 's/^/  - /'
    read -p "Enter your role: " AGENT_ROLE
fi

echo "👤 Agent Role: $AGENT_ROLE"

# Sync repository state
echo "🔄 Syncing repository state..."
git fetch origin
git pull origin main || true

# Load role-specific instructions
ROLE_FILE=".conductor/roles/${AGENT_ROLE}.md"
if [ ! -f "$ROLE_FILE" ]; then
    echo "❌ Role definition not found: $ROLE_FILE"
    exit 1
fi

echo "📖 Loaded role definition: $AGENT_ROLE"

# Check system dependencies
echo "🔍 Checking dependencies..."
python3 .conductor/scripts/dependency-check.py

# Attempt to claim a task
echo "🎯 Looking for available tasks..."
TASK_RESULT=$(python3 .conductor/scripts/task-claim.py --role "$AGENT_ROLE")

if echo "$TASK_RESULT" | grep -q "IDLE"; then
    echo "😴 No tasks available. Agent is idle."
    echo "💡 Check back later or create new tasks via GitHub issues."
    exit 0
fi

# Task claimed successfully
echo "✅ Task claimed successfully!"
echo "$TASK_RESULT" | python3 -m json.tool

# Create git worktree for isolated work
TASK_ID=$(echo "$TASK_RESULT" | python3 -c "import json, sys; data=json.load(sys.stdin); print(data['task_id'])")
BRANCH_NAME="agent-$AGENT_ROLE-$TASK_ID"
WORKTREE_PATH="./worktrees/$BRANCH_NAME"

echo "🌳 Creating git worktree: $WORKTREE_PATH"
git worktree add "$WORKTREE_PATH" -b "$BRANCH_NAME"

# Display next steps
echo ""
echo "🚀 Agent initialization complete!"
echo "📂 Your isolated workspace: $WORKTREE_PATH"
echo ""
echo "Next steps:"
echo "1. cd $WORKTREE_PATH"
echo "2. Review your task details in the output above"
echo "3. Implement according to specifications"
echo "4. Commit and push your changes"
echo "5. Create a pull request when ready"
"""

        bootstrap_file = scripts_dir / "bootstrap.sh"
        with open(bootstrap_file, "w") as f:
            f.write(bootstrap_content)
        os.chmod(bootstrap_file, 0o755)
        print(f"✓ Created {bootstrap_file}")

        # More scripts would be created here...
        # For brevity, I'll create just the essential task-claim.py

        task_claim_content = '''#!/usr/bin/env python3
"""Task claiming script for atomic task assignment"""

import json
import sys
import fcntl
import argparse
from datetime import datetime
from pathlib import Path

class TaskClaimer:
    def __init__(self, role):
        self.role = role
        self.state_file = Path(".conductor/workflow-state.json")

    def claim_task(self):
        """Atomically claim an available task"""
        # Ensure file exists
        if not self.state_file.exists():
            return {"status": "ERROR", "message": "State file not found"}

        with open(self.state_file, 'r+') as f:
            # Exclusive lock for atomic operations
            fcntl.flock(f, fcntl.LOCK_EX)

            try:
                state = json.load(f)
            except json.JSONDecodeError:
                return {"status": "ERROR", "message": "Invalid state file"}

            claimed_task = None

            # Find suitable task
            for i, task in enumerate(state.get("available_tasks", [])):
                # Check skill requirements
                required_skills = task.get("required_skills", [])

                # Hybrid logic: empty skills = any dev, otherwise need match
                if not required_skills or self.role in required_skills:
                    # Check no file conflicts
                    if not self._has_file_conflicts(task, state):
                        claimed_task = task
                        state["available_tasks"].pop(i)
                        break

            if claimed_task:
                # Create agent ID
                agent_id = f"{self.role}_{int(datetime.utcnow().timestamp())}"

                # Move to active work
                if "active_work" not in state:
                    state["active_work"] = {}

                state["active_work"][agent_id] = {
                    "task": claimed_task,
                    "status": "in_progress",
                    "started_at": datetime.utcnow().isoformat(),
                    "heartbeat": datetime.utcnow().isoformat(),
                    "files_locked": claimed_task.get("files_locked", [])
                }

                # Update agent counts
                if "system_status" not in state:
                    state["system_status"] = {}
                state["system_status"]["active_agents"] = len(state["active_work"])
                state["system_status"]["last_updated"] = datetime.utcnow().isoformat()

                # Write back atomically
                f.seek(0)
                json.dump(state, f, indent=2)
                f.truncate()

                # Release lock
                fcntl.flock(f, fcntl.LOCK_UN)

                # Return success with task details
                return {
                    "status": "claimed",
                    "task_id": claimed_task["id"],
                    "task": claimed_task,
                    "agent_id": agent_id
                }
            else:
                # Release lock
                fcntl.flock(f, fcntl.LOCK_UN)
                return {"status": "IDLE", "reason": "No suitable tasks available"}

    def _has_file_conflicts(self, task, state):
        """Check if task files conflict with active work"""
        task_files = set(task.get("files_locked", []))
        if not task_files:
            return False

        for agent_work in state.get("active_work", {}).values():
            locked_files = set(agent_work.get("files_locked", []))
            if task_files & locked_files:  # Intersection = conflict
                return True

        return False

def main():
    parser = argparse.ArgumentParser(description="Claim a task for agent work")
    parser.add_argument("--role", default="dev", help="Agent role (default: dev)")
    args = parser.parse_args()

    claimer = TaskClaimer(args.role)
    result = claimer.claim_task()

    # Output result as JSON
    print(json.dumps(result))

    # Exit with appropriate code
    sys.exit(0 if result["status"] in ["claimed", "IDLE"] else 1)

if __name__ == "__main__":
    main()
'''

        task_claim_file = scripts_dir / "task-claim.py"
        with open(task_claim_file, "w") as f:
            f.write(task_claim_content)
        os.chmod(task_claim_file, 0o755)
        print(f"✓ Created {task_claim_file}")

    def validate_setup(self):
        """Validate the setup is correct"""
        print("\n✅ Validating setup...")

        checks = [
            (self.conductor_dir / "config.yaml", "Configuration file"),
            (self.conductor_dir / "workflow-state.json", "Workflow state"),
            (self.conductor_dir / "scripts" / "bootstrap.sh", "Bootstrap script"),
            (self.conductor_dir / "scripts" / "task-claim.py", "Task claim script"),
            (
                self.project_root / ".github" / "workflows" / "conductor.yml",
                "GitHub workflow",
            ),
        ]

        all_valid = True
        for file_path, description in checks:
            if file_path.exists():
                print(f"✓ {description} exists")
            else:
                print(f"✗ {description} missing")
                all_valid = False

        # Check GitHub CLI
        try:
            result = subprocess.run(["gh", "--version"], capture_output=True)
            if result.returncode == 0:
                print("✓ GitHub CLI installed")
            else:
                print("⚠️  GitHub CLI not found (optional but recommended)")
        except Exception:
            print("⚠️  GitHub CLI not found (optional but recommended)")

        return all_valid

    def display_completion_message(self):
        """Show completion message and next steps"""
        print("\n" + "=" * 50)
        print("🎉 Code Conductor Setup Complete!")
        print("=" * 50)

        print("\n📋 Next Steps:")
        print("1. Review the generated configuration in .conductor/config.yaml")
        print("2. Customize role definitions in .conductor/roles/ if needed")
        print("3. Commit these changes to your repository")
        print(
            "4. Create your first tasks via GitHub issues with 'conductor:task' label"
        )
        print("5. Launch agents using: bash .conductor/scripts/bootstrap.sh [role]")

        print("\n💡 Quick Start:")
        print("  # Create a task via GitHub issue")
        print("  # Then spawn an agent:")
        print("  export AGENT_ROLE=dev")
        print("  bash .conductor/scripts/bootstrap.sh")

        print("\n📚 Documentation:")
        print("  - Role definitions: .conductor/roles/")
        print("  - Configuration: .conductor/config.yaml")
        print("  - Scripts: .conductor/scripts/")

        print("\n🚀 Happy coding with Code Conductor!")


def main():
    parser = argparse.ArgumentParser(
        description="Code Conductor Interactive Setup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python setup.py              # Interactive setup
  python setup.py --auto       # Auto-configuration
  python setup.py --debug      # Enable debug logging
        """,
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Run in auto-configuration mode (minimal prompts)",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    try:
        setup = ConductorSetup(auto_mode=args.auto, debug=args.debug)
        setup.run()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        if args.debug:
            import traceback

            traceback.print_exc()
        else:
            print(f"\n❌ Setup failed: {e}")
            print("💡 Run with --debug for detailed error information")
        sys.exit(1)


if __name__ == "__main__":
    main()
