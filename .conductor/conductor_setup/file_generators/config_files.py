"""
Configuration Files Generator
Generates YAML configuration files and CLAUDE.md instructions
"""

import re
import sys
import yaml
from pathlib import Path
from typing import Dict, Any


class ConfigFileGenerator:
    """Generates configuration files for Code Conductor"""

    def __init__(self, project_root: Path, config: Dict[str, Any], debug: bool = False):
        self.project_root = project_root
        self.conductor_dir = project_root / ".conductor"
        self.config = config
        self.debug = debug

    def create_configuration_files(self):
        """Generate all configuration files"""
        print("\n🔧 Creating configuration files...")

        try:
            # Ensure directories exist
            self.conductor_dir.mkdir(exist_ok=True)
        except PermissionError:
            print("❌ Permission denied creating .conductor directory")
            print("💡 Try running with sudo or check directory permissions")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Failed to create .conductor directory: {e}")
            sys.exit(1)

        # Create config.yaml
        self._create_config_yaml()

        # Create or update CLAUDE.md
        self._manage_claude_instructions()

        # Create GitHub issue templates
        self._create_issue_templates()

    def _create_config_yaml(self):
        """Create the main configuration YAML file"""
        config_data = {
            "version": "1.0.0",
            "project_name": self.config["project_name"],
            "docs_directory": self.config["docs_directory"],
            "task_management": self.config["task_management"],
            "roles": self.config["roles"],
            "conflict_prevention": {"use_worktrees": True, "file_locking": True},
            "github_integration": {
                "enabled": True,
                "issue_to_task": True,
                "pr_reviews": True,
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
            print(f"❌ Failed to create config file: {e}")
            sys.exit(1)

    def _manage_claude_instructions(self):
        """Intelligently manage CLAUDE.md for AI agent context"""
        claude_file = self.project_root / "CLAUDE.md"

        conductor_section = """<!-- CONDUCTOR:START -->
# 🤖 Code Conductor Agent Instructions

You are operating in a Code Conductor orchestrated project with automated task
management via GitHub Issues.

## Quick Start
To begin work as an agent, simply run:
```bash
./conductor start [role]
```

This single command will:
1. Show your role definition and capabilities
2. List available tasks appropriate for your role
3. Claim a task atomically
4. Set up your isolated workspace
5. Provide task context and success criteria

## Available Roles
{roles_list}

## Core Commands
- `./conductor status` - View system status and your current task
- `./conductor tasks` - List all available tasks
- `./conductor complete` - Mark current task complete and get next
- `./conductor help` - Show role-specific guidance

## Workflow
1. Start: `./conductor start [role]`
2. Work in the created worktree following task specifications
3. Commit with conventional commits: `feat:`, `fix:`, `test:`, etc.
4. Run: `./conductor complete` when done
5. The system handles PR creation and moves you to the next task

<!-- CONDUCTOR:END -->"""

        try:
            if claude_file.exists():
                content = claude_file.read_text()

                # Check if conductor section exists
                if "<!-- CONDUCTOR:START -->" in content:
                    # Update existing section
                    pattern = r"<!-- CONDUCTOR:START -->.*?<!-- CONDUCTOR:END -->"
                    new_content = re.sub(
                        pattern, conductor_section, content, flags=re.DOTALL
                    )
                else:
                    # Prepend to existing file
                    new_content = conductor_section + "\n\n---\n\n" + content
            else:
                # Create new file
                new_content = conductor_section

            # Fill in dynamic content
            roles_list = "\n".join(
                [
                    f"- `{role}`: {self._get_role_summary(role)}"
                    for role in ["dev"] + self.config["roles"].get("specialized", [])
                ]
            )
            new_content = new_content.replace("{roles_list}", roles_list)

            claude_file.write_text(new_content)
            print(f"✓ Created/Updated {claude_file}")

        except Exception as e:
            if self.debug:
                print(f"Failed to create CLAUDE.md: {e}")
            print(f"⚠️  Could not create CLAUDE.md: {e}")

    def _get_role_summary(self, role: str) -> str:
        """Get a brief summary for a role"""
        role_summaries = {
            "dev": "Default generalist developer role",
            "devops": "CI/CD, infrastructure, deployments",
            "security": "Security audits and vulnerability management",
            "ml-engineer": "Machine learning and AI tasks",
            "ui-designer": "UI/UX design and frontend components",
            "code-reviewer": "Automated AI-powered PR reviews",
            "frontend": "Client-side development and UI",
            "mobile": "Mobile application development",
            "data": "Data pipelines and analytics",
            "backend": "Server-side development and APIs",
        }
        return role_summaries.get(role, f"Specialized {role} tasks")

    def _create_issue_templates(self):
        """Create GitHub issue templates"""
        issue_templates_dir = self.project_root / ".github" / "ISSUE_TEMPLATE"
        issue_templates_dir.mkdir(parents=True, exist_ok=True)

        # Create conductor task template
        task_template = {
            "name": "Conductor Task",
            "description": "Create a new task for AI agents to work on",
            "title": "[Task] ",
            "labels": ["conductor:task"],
            "body": [
                {
                    "type": "markdown",
                    "attributes": {
                        "value": (
                            "## Task Details\n\n"
                            "Please provide clear specifications for this task."
                        )
                    },
                },
                {
                    "type": "textarea",
                    "id": "description",
                    "attributes": {
                        "label": "Description",
                        "description": "What needs to be done?",
                        "placeholder": "Provide a clear description of the task...",
                    },
                    "validations": {"required": True},
                },
                {
                    "type": "textarea",
                    "id": "specifications",
                    "attributes": {
                        "label": "Specifications",
                        "description": "Detailed technical specifications",
                        "placeholder": (
                            "- [ ] Requirement 1\n"
                            "- [ ] Requirement 2\n"
                            "- [ ] Requirement 3"
                        ),
                    },
                },
                {
                    "type": "textarea",
                    "id": "success_criteria",
                    "attributes": {
                        "label": "Success Criteria",
                        "description": (
                            "How will we know when this task is complete?"
                        ),
                        "placeholder": (
                            "- All tests pass\n"
                            "- Code follows project conventions\n"
                            "- Feature works as described"
                        ),
                    },
                },
                {
                    "type": "dropdown",
                    "id": "effort",
                    "attributes": {
                        "label": "Estimated Effort",
                        "options": ["small", "medium", "large"],
                    },
                    "validations": {"required": True},
                },
                {
                    "type": "dropdown",
                    "id": "priority",
                    "attributes": {
                        "label": "Priority",
                        "options": ["low", "medium", "high"],
                    },
                    "validations": {"required": True},
                },
                {
                    "type": "input",
                    "id": "skills",
                    "attributes": {
                        "label": "Required Skills",
                        "description": (
                            "Comma-separated list of required skills "
                            "(e.g., python, react, devops)"
                        ),
                        "placeholder": "Leave blank for general dev tasks",
                    },
                },
            ],
        }

        template_file = issue_templates_dir / "conductor-task.yml"
        with open(template_file, "w") as f:
            yaml.dump(task_template, f, default_flow_style=False, sort_keys=False)
        print(f"✓ Created {template_file}")
