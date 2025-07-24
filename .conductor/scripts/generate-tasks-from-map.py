#!/usr/bin/env python3
"""Generate GitHub issues from the documentation map created by AI agent"""

import yaml
import subprocess
import sys
from pathlib import Path
from datetime import datetime


class TaskGenerator:
    def __init__(self):
        self.map_file = Path(".conductor/documentation-map.yaml")
        self.generated_count = 0

    def load_documentation_map(self):
        """Load the AI-generated documentation map"""
        if not self.map_file.exists():
            print("❌ Documentation map not found at .conductor/documentation-map.yaml")
            print("   Run the discovery task first to create this file.")
            return None

        try:
            with open(self.map_file, "r") as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"❌ Invalid YAML in documentation map: {e}")
            return None
        except Exception as e:
            print(f"❌ Error loading documentation map: {e}")
            return None

    def validate_map(self, doc_map):
        """Validate the AI-generated map"""
        issues = []

        # Check required fields
        if not doc_map:
            issues.append("Documentation map is empty")
            return issues

        if not doc_map.get("project", {}).get("name"):
            issues.append("Missing project name")

        if not doc_map.get("proposed_tasks"):
            issues.append("No tasks proposed")
        else:
            # Validate each task
            for i, task in enumerate(doc_map.get("proposed_tasks", [])):
                task_issues = []
                if not task.get("title"):
                    task_issues.append("missing title")
                if not task.get("description"):
                    task_issues.append("missing description")
                if not task.get("success_criteria"):
                    task_issues.append("missing success criteria")

                if task_issues:
                    issues.append(
                        f"Task {i+1} ({task.get('title', 'unnamed')}): {', '.join(task_issues)}"
                    )

        return issues

    def interactive_review(self, doc_map):
        """Allow human to review AI-generated map"""
        print("\n📋 Documentation Map Review")
        print("=" * 50)

        # Project overview
        project = doc_map.get("project", {})
        print(f"Project: {project.get('name', 'Unknown')}")
        print(f"Type: {project.get('type', 'unknown')}")
        print(f"Language: {project.get('primary_language', 'unknown')}")
        print(f"Status: {project.get('status', 'unknown')}")
        print(f"Completion: {project.get('estimated_completion', '?')}%")
        print()

        # Task summary
        tasks = doc_map.get("proposed_tasks", [])
        print(f"Proposed Tasks: {len(tasks)}")

        # Group by priority
        by_priority = {"critical": [], "high": [], "medium": [], "low": []}
        for task in tasks:
            priority = task.get("priority", "medium")
            by_priority[priority].append(task)

        # Show summary by priority
        for priority in ["critical", "high", "medium", "low"]:
            count = len(by_priority[priority])
            if count > 0:
                print(f"\n{priority.upper()} Priority ({count}):")
                # Show first 3 tasks
                for task in by_priority[priority][:3]:
                    print(f"  - {task.get('title', 'Untitled')}")
                if count > 3:
                    print(f"  ... and {count - 3} more")

        # Summary stats
        summary = doc_map.get("summary", {})
        if summary:
            print(
                f"\nTotal effort estimate: {summary.get('estimated_total_effort', 'unknown')}"
            )

        print("\n" + "=" * 50)
        print("Options:")
        print("1. Create all tasks")
        print("2. Create high/critical priority only")
        print("3. Review map file first")
        print("4. Cancel")

        try:
            choice = input("\nChoice [1-4]: ").strip()
            return choice
        except (KeyboardInterrupt, EOFError):
            return "4"

    def generate_tasks(self, filter_priority=None):
        """Create GitHub issues from the proposed tasks"""
        doc_map = self.load_documentation_map()
        if not doc_map:
            return

        # Validate map
        validation_issues = self.validate_map(doc_map)
        if validation_issues:
            print("\n⚠️  Validation issues found:")
            for issue in validation_issues:
                print(f"  - {issue}")

            response = input("\nContinue anyway? [y/N]: ").strip().lower()
            if response != "y":
                print("Cancelled.")
                return

        # Interactive review
        choice = self.interactive_review(doc_map)

        if choice == "3":
            print(f"\nMap file location: {self.map_file.absolute()}")
            print("Review the file and run this script again.")
            return
        elif choice == "4":
            print("Cancelled.")
            return
        elif choice == "2":
            filter_priority = ["critical", "high"]

        # Create issues
        tasks = doc_map.get("proposed_tasks", [])
        if filter_priority:
            tasks = [t for t in tasks if t.get("priority") in filter_priority]
            print(f"\nCreating {len(tasks)} high/critical priority tasks...")
        else:
            print(f"\nCreating {len(tasks)} tasks...")

        for i, task in enumerate(tasks):
            print(f"\n[{i+1}/{len(tasks)}] Creating: {task.get('title', 'Untitled')}")

            # Format issue body
            issue_body = self.format_task_body(task, doc_map.get("documentation", {}))

            # Prepare labels
            labels = ["conductor:task"]

            # Add effort label
            effort = task.get("estimated_effort", "medium")
            labels.append(f"effort:{effort}")

            # Add priority label
            priority = task.get("priority", "medium")
            labels.append(f"priority:{priority}")

            # Add skill labels
            role = task.get("assigned_role", "dev")
            if role != "dev":
                labels.append(f"skill:{role}")

            # Create issue
            try:
                result = subprocess.run(
                    [
                        "gh",
                        "issue",
                        "create",
                        "--title",
                        task.get("title", "Untitled Task"),
                        "--body",
                        issue_body,
                        "--label",
                        ",".join(labels),
                    ],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    self.generated_count += 1
                    issue_url = result.stdout.strip()
                    issue_num = issue_url.split("/")[-1]
                    print(f"  ✅ Created issue #{issue_num}")
                else:
                    print(f"  ❌ Failed to create issue: {result.stderr}")
            except Exception as e:
                print(f"  ❌ Error creating issue: {e}")

        # Update the map to mark as processed
        if self.generated_count > 0:
            doc_map["tasks_generated"] = True
            doc_map["tasks_generated_at"] = datetime.now().isoformat()
            doc_map["tasks_generated_count"] = self.generated_count

            try:
                with open(self.map_file, "w") as f:
                    yaml.dump(doc_map, f, default_flow_style=False, sort_keys=False)
                print("\n✅ Updated documentation map with generation status")
            except Exception as e:
                print(f"\n⚠️  Could not update map file: {e}")

        print(f"\n🎉 Created {self.generated_count} tasks successfully!")

        if self.generated_count > 0:
            print("\n📋 Next steps:")
            print("1. Review the created issues on GitHub")
            print("2. Launch AI agents with: conductor-agent start [role]")
            print("3. Agents will automatically claim and work on tasks")

    def format_task_body(self, task, documentation):
        """Format task with proper documentation links"""
        # Build source documentation section
        source_docs = task.get("source_requirement", "")
        if isinstance(source_docs, list):
            source_docs = "\n".join([f"- `{doc}`" for doc in source_docs])
        elif source_docs:
            source_docs = f"- `{source_docs}`"
        else:
            source_docs = "- See project documentation"

        # Format success criteria
        success_criteria = task.get("success_criteria", [])
        if not success_criteria:
            success_criteria = ["Meets requirements in source documentation"]

        criteria_text = "\n".join(
            [f"- [ ] {criterion}" for criterion in success_criteria]
        )

        # Build the issue body
        body = f"""## Description
{task.get('description', 'No description provided')}

## Task Type
{task.get('type', 'feature').title()}

## Source Documentation
The following documents contain the requirements for this task:
{source_docs}

## Implementation Approach
{task.get('implementation_notes', 'Follow the patterns established in the codebase.')}

## Success Criteria
{criteria_text}

## Definition of Done
- [ ] Implementation complete and working
- [ ] Unit tests written and passing
- [ ] Integration tests updated if needed
- [ ] Documentation updated to reflect changes
- [ ] Code reviewed and approved
- [ ] No linting errors or warnings

## Additional Context
- **Assigned Role**: {task.get('assigned_role', 'dev')}
- **Estimated Effort**: {task.get('estimated_effort', 'medium')}
- **Priority**: {task.get('priority', 'medium')}

---
*Generated from project documentation map by Code Conductor*
"""
        return body


def main():
    """Main entry point"""
    print("🤖 Code Conductor Task Generator")
    print("================================")
    print()
    print("This tool creates GitHub issues from the AI-generated documentation map.")
    print()

    generator = TaskGenerator()

    # Check if map exists
    if not generator.map_file.exists():
        print("❌ No documentation map found!")
        print()
        print("To create one:")
        print("1. Run: conductor-agent start dev")
        print("2. The agent will claim the discovery task")
        print("3. It will analyze your project and create the map")
        print("4. Then run this script again")
        sys.exit(1)

    # Generate tasks
    generator.generate_tasks()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
