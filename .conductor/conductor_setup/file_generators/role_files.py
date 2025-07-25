"""
Role Files Generator
Generates role definition markdown files from templates
"""

from pathlib import Path
from typing import Dict, Any


class RoleFileGenerator:
    """Generates role definition files for AI agents"""

    def __init__(self, project_root: Path, config: Dict[str, Any]):
        self.project_root = project_root
        self.conductor_dir = project_root / ".conductor"
        self.config = config
        # Path to templates directory relative to this file
        self.templates_dir = Path(__file__).parent.parent / "templates" / "roles"

    def create_role_definitions(self):
        """Create role definition files"""
        print("\n📄 Creating role definitions...")

        roles_dir = self.conductor_dir / "roles"
        roles_dir.mkdir(exist_ok=True)

        # Always create the default dev role
        self._create_role_from_template(roles_dir, "dev")

        # Create specialized roles
        for role in self.config["roles"]["specialized"]:
            self._create_role_from_template(roles_dir, role)

    def _create_role_from_template(self, roles_dir: Path, role_name: str):
        """Create a role file from template"""
        # Map role names to template files
        template_mapping = {
            "dev": "dev.md",
            "devops": "devops.md",
            "security": "security.md",
            "ml-engineer": "ml-engineer.md",
            "ui-designer": "ui-designer.md",
            "code-reviewer": "code-reviewer.md",
            "frontend": "frontend.md",
            "mobile": "mobile.md",
            "data": "data.md",
            "backend": "backend.md",  # Can use dev.md as fallback
        }

        # Get template filename
        template_file = template_mapping.get(role_name)

        if template_file and (self.templates_dir / template_file).exists():
            # Read template content
            content = (self.templates_dir / template_file).read_text()
        else:
            # Fallback for unknown roles
            content = self._generate_custom_role_content(role_name)

        # Write role file
        role_file = roles_dir / f"{role_name}.md"
        with open(role_file, "w") as f:
            f.write(content)

    def _generate_custom_role_content(self, role_name: str) -> str:
        """Generate content for custom roles not in templates"""
        return f"""# {role_name.title().replace('-', ' ')} Role

## Overview
This is a specialized role for {role_name.replace('-', ' ')} tasks.

## Responsibilities
- Work on tasks labeled with '{role_name}'
- Follow project standards and best practices
- Collaborate with other agents as needed
- Create high-quality pull requests

## Task Selection Criteria
- Tasks should be labeled with '{role_name}' or related tags
- Prioritize tasks that match this role's expertise
- Coordinate with other agents to avoid conflicts

## Best Practices
1. Read task specifications thoroughly
2. Check existing codebase for patterns
3. Test all changes before submitting
4. Document your implementation
5. Communicate through GitHub issues

## Success Metrics
- Task completed according to specifications
- All tests passing
- Code review approved
- No regressions introduced
"""

    def get_role_examples(self) -> Dict[str, str]:
        """Return examples of task issues for each role type"""
        return {
            "dev": "General development tasks without specific role requirements",
            "devops": "CI/CD setup, deployment configurations, infrastructure as code",
            "security": "Security audits, vulnerability fixes, authentication setup",
            "ml-engineer": "ML model integration, data pipeline setup, workflows",
            "ui-designer": "Component design systems, accessibility improvements",
            "code-reviewer": "Automated PR reviews (system-generated)",
            "frontend": "React/Vue components, UI state management, styling",
            "mobile": "iOS/Android features, React Native development",
            "data": "ETL pipelines, data warehouse setup, analytics",
            "backend": "API development, database design, server-side logic",
        }
