"""
GitHub Workflow Files Generator
Generates GitHub Actions workflow files
"""

from pathlib import Path
from typing import Dict, Any


class WorkflowFileGenerator:
    """Generates GitHub Actions workflow files"""

    def __init__(self, project_root: Path, config: Dict[str, Any]):
        self.project_root = project_root
        self.config = config

    def create_github_workflows(self):
        """Create GitHub Actions workflows"""
        print("\n🤖 Creating GitHub Actions workflows...")

        workflows_dir = self.project_root / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)

        # Create main conductor workflow
        self._create_conductor_workflow(workflows_dir)

        # Create cleanup workflow
        self._create_cleanup_workflow(workflows_dir)

        # Create PR review workflow
        self._create_pr_review_workflow(workflows_dir)

        # Create issue template
        self._create_issue_template()

    def _create_conductor_workflow(self, workflows_dir: Path):
        """Create the main conductor orchestration workflow"""
        conductor_workflow = """name: Conductor Orchestration

on:
  schedule:
    - cron: '*/15 * * * *'  # Every 15 minutes for health checks
  workflow_dispatch:
  issues:
    types: [opened, labeled, closed]
  issue_comment:
    types: [created]

jobs:
  format-task-issue:
    if: github.event_name == 'issues' && github.event.action == 'opened' && !contains(github.event.issue.labels.*.name, 'conductor:task')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Check if issue should be a task
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          # Auto-detect potential tasks based on keywords
          if echo "${{ github.event.issue.title }}" | grep -iE "implement|add|fix|update|create|refactor"; then
            gh issue edit ${{ github.event.issue.number }} --add-label "conductor:task"
            python .conductor/scripts/issue-to-task.py ${{ github.event.issue.number }}
          fi

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

      - name: Run health check
        env:
          GH_TOKEN: ${{ github.token }}
        run: python .conductor/scripts/health-check.py

      - name: Generate status summary
        env:
          GH_TOKEN: ${{ github.token }}
        run: python .conductor/scripts/generate-summary.py >> $GITHUB_STEP_SUMMARY

  cleanup-stale:
    if: github.event_name == 'schedule'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Clean up stale work
        env:
          GH_TOKEN: ${{ github.token }}
        run: python .conductor/scripts/cleanup-stale.py
"""

        conductor_file = workflows_dir / "conductor.yml"
        with open(conductor_file, "w") as f:
            f.write(conductor_workflow)
        print(f"✓ Created {conductor_file}")

    def _create_cleanup_workflow(self, workflows_dir: Path):
        """Create the cleanup workflow"""
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

    def _create_pr_review_workflow(self, workflows_dir: Path):
        """Create the PR review workflow for AI-powered code reviews"""
        pr_review_workflow = """name: AI Code Review

on:
  pull_request:
    types: [opened, synchronize, reopened]
  pull_request_review_comment:
    types: [created, edited]
  issue_comment:
    types: [created]

permissions:
  contents: read
  pull-requests: write
  issues: write

jobs:
  ai-review:
    name: AI Code Review
    runs-on: ubuntu-latest
    # Skip if PR is from a bot or if skip-review label is present
    if: |
      github.event.pull_request && 
      github.event.pull_request.user.type != 'Bot' &&
      !contains(github.event.pull_request.labels.*.name, 'skip-review')
    
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install pyyaml requests
      
      - name: Run AI Code Review
        env:
          GH_TOKEN: ${{ github.token }}
          PR_NUMBER: ${{ github.event.pull_request.number }}
        run: |
          # Simple AI review trigger
          echo "🔍 AI Code Review triggered for PR #$PR_NUMBER"
          
          # Check if code-reviewer role exists
          if [ -f ".conductor/roles/code-reviewer.md" ]; then
            echo "✅ Code reviewer role found"
            # The actual review would be done by the code-reviewer agent
            # This workflow just ensures the infrastructure is in place
          else
            echo "⚠️ Code reviewer role not configured"
          fi
"""

        pr_review_file = workflows_dir / "pr-review.yml"
        with open(pr_review_file, "w") as f:
            f.write(pr_review_workflow)
        print(f"✓ Created {pr_review_file}")

    def _create_issue_template(self):
        """Create GitHub issue template for conductor tasks"""
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
