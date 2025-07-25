"""
GitHub Workflow Files Generator
Generates GitHub Actions workflow files from templates
"""

from pathlib import Path
from typing import Dict, Any


class WorkflowFileGenerator:
    """Generates GitHub Actions workflow files"""

    def __init__(self, project_root: Path, config: Dict[str, Any]):
        self.project_root = project_root
        self.config = config
        # Path to templates directory relative to this file
        self.templates_dir = Path(__file__).parent.parent / "templates" / "workflows"

    def create_github_workflows(self):
        """Create GitHub Actions workflows"""
        print("\n🤖 Creating GitHub Actions workflows...")

        workflows_dir = self.project_root / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)

        # Create main conductor workflow
        self._create_workflow_from_template(workflows_dir, "conductor.yml")

        # Create cleanup workflow
        self._create_workflow_from_template(workflows_dir, "conductor-cleanup.yml")

        # Create PR review workflow if code-reviewer role is enabled
        if "code-reviewer" in self.config["roles"]["specialized"]:
            self._create_workflow_from_template(workflows_dir, "pr-review.yml")

    def _create_workflow_from_template(self, workflows_dir: Path, template_name: str):
        """Create a workflow file from template"""
        template_file = self.templates_dir / template_name

        if not template_file.exists():
            print(f"⚠️  Warning: Template {template_name} not found")
            return

        # Read template content
        content = template_file.read_text()

        # Apply any necessary substitutions
        content = self._apply_substitutions(content)

        # Write workflow file
        output_file = workflows_dir / template_name
        with open(output_file, "w") as f:
            f.write(content)

        print(f"✅ Created workflow: {template_name}")

    def _apply_substitutions(self, content: str) -> str:
        """Apply configuration substitutions to workflow content"""
        # For now, workflows use GitHub's built-in tokens
        # Future: Could add project-specific substitutions here
        return content

    def get_workflow_descriptions(self) -> Dict[str, str]:
        """Return descriptions of each workflow"""
        return {
            "conductor.yml": "Main orchestration workflow for tasks and health checks",
            "conductor-cleanup.yml": "Automated cleanup of stale worktrees and tasks",
            "pr-review.yml": "AI-powered code review for pull requests",
        }
