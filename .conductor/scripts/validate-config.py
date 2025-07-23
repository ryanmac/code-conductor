#!/usr/bin/env python3
"""Validate conductor configuration for GitHub-native integration"""

import json
import yaml
import sys
import subprocess
from pathlib import Path
import os


def run_gh_command(args):
    """Run GitHub CLI command and return output"""
    try:
        # Pass through environment variables including GITHUB_TOKEN
        env = os.environ.copy()
        result = subprocess.run(
            ["gh"] + args, capture_output=True, text=True, check=True, env=env
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None
    except FileNotFoundError:
        return None


def validate_config_yaml():
    """Validate the main configuration file"""
    config_file = Path(".conductor/config.yaml")
    errors = []
    warnings = []

    if not config_file.exists():
        errors.append("config.yaml not found")
        return errors, warnings

    try:
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML in config.yaml: {e}")
        return errors, warnings

    # Required fields
    required_fields = ["version", "project_name", "roles"]
    for field in required_fields:
        if field not in config:
            errors.append(f"Missing required field: {field}")

    # Validate roles
    if "roles" in config:
        roles = config["roles"]
        if not isinstance(roles, dict):
            errors.append("'roles' must be a dictionary")
        else:
            if "default" not in roles:
                errors.append("Missing 'default' role")

            if "specialized" in roles and not isinstance(roles["specialized"], list):
                errors.append("'specialized' roles must be a list")

    # Validate GitHub integration settings
    if "github_integration" in config:
        gh_config = config["github_integration"]
        if not isinstance(gh_config, dict):
            errors.append("'github_integration' must be a dictionary")
        else:
            if gh_config.get("enabled", True) and not gh_config.get(
                "issue_to_task", True
            ):
                warnings.append(
                    "GitHub integration enabled but issue_to_task is disabled"
                )
    else:
        warnings.append("No 'github_integration' section in config (using defaults)")

    # Validate agent settings
    if "agent_settings" in config:
        settings = config["agent_settings"]
        if "heartbeat_interval" in settings:
            try:
                interval = int(settings["heartbeat_interval"])
                if interval < 60:
                    warnings.append(
                        "Heartbeat interval less than 60 seconds may cause excessive API calls"
                    )
                elif interval > 3600:
                    warnings.append(
                        "Heartbeat interval greater than 1 hour may cause timeouts"
                    )
            except (ValueError, TypeError):
                errors.append("heartbeat_interval must be a number")

        if "max_concurrent" in settings:
            try:
                max_concurrent = int(settings["max_concurrent"])
                if max_concurrent < 1:
                    errors.append("max_concurrent must be at least 1")
                elif max_concurrent > 50:
                    warnings.append("max_concurrent > 50 may overwhelm the system")
            except (ValueError, TypeError):
                errors.append("max_concurrent must be a number")

    return errors, warnings


def validate_github_cli():
    """Validate GitHub CLI availability and authentication"""
    errors = []
    warnings = []

    # Check if gh is installed
    output = run_gh_command(["--version"])
    if not output:
        errors.append(
            "GitHub CLI (gh) not found. Please install it from https://cli.github.com/"
        )
        return errors, warnings

    # Check authentication
    output = run_gh_command(["auth", "status"])
    if not output:
        # In CI environment with GITHUB_TOKEN, this might be a warning not an error
        if os.environ.get("GITHUB_TOKEN") or os.environ.get("CI"):
            warnings.append(
                "GitHub CLI auth status check failed (but GITHUB_TOKEN is set)"
            )
        else:
            errors.append(
                "GitHub CLI not authenticated. Run 'gh auth login' to authenticate"
            )
    else:
        print(
            f"  ✓ GitHub CLI authenticated"
        )

    # Check if we're in a git repository
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        warnings.append("Not in a git repository or git not installed")

    # Check if remote is configured
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
        )
        remote_url = result.stdout.strip()
        if "github.com" not in remote_url:
            warnings.append(f"Remote origin is not a GitHub repository: {remote_url}")
    except subprocess.CalledProcessError:
        warnings.append("No remote 'origin' configured")

    return errors, warnings


def validate_github_labels():
    """Validate required GitHub labels exist"""
    errors = []
    warnings = []

    # Check if we can list labels
    output = run_gh_command(["label", "list", "--limit", "100", "--json", "name"])

    if not output:
        warnings.append(
            "Could not fetch repository labels (might not have permissions)"
        )
        return errors, warnings

    try:
        labels = json.loads(output)
        label_names = [label["name"] for label in labels]
    except json.JSONDecodeError:
        warnings.append("Could not parse repository labels")
        return errors, warnings

    # Required labels
    required_labels = ["conductor:task", "conductor:status", "conductor:in-progress"]

    for label in required_labels:
        if label not in label_names:
            warnings.append(f"Required label '{label}' not found in repository")

    # Recommended labels
    recommended_labels = [
        "conductor:blocked",
        "conductor:archived",
        "effort:small",
        "effort:medium",
        "effort:large",
        "priority:high",
        "priority:medium",
        "priority:low",
    ]

    missing_recommended = []
    for label in recommended_labels:
        if label not in label_names:
            missing_recommended.append(label)

    if missing_recommended:
        warnings.append(f"Recommended labels missing: {', '.join(missing_recommended)}")

    return errors, warnings


def validate_role_files():
    """Validate role definition files"""
    roles_dir = Path(".conductor/roles")
    errors = []
    warnings = []

    if not roles_dir.exists():
        warnings.append("roles directory not found")
        return errors, warnings

    # Check for dev role (default)
    dev_role = roles_dir / "dev.md"
    if not dev_role.exists():
        warnings.append("dev.md role file not found (recommended)")

    # Validate existing role files
    for role_file in roles_dir.glob("*.md"):
        try:
            with open(role_file, "r") as f:
                content = f.read()

            if len(content.strip()) < 100:
                warnings.append(f"Role file {role_file.name} seems too short")

            # Check for basic sections
            required_sections = ["## Overview", "## Responsibilities"]
            for section in required_sections:
                if section not in content:
                    warnings.append(f"Role file {role_file.name} missing {section}")

        except Exception as e:
            errors.append(f"Error reading role file {role_file.name}: {e}")

    return errors, warnings


def validate_scripts():
    """Validate that required scripts exist"""
    scripts_dir = Path(".conductor/scripts")
    errors = []
    warnings = []

    if not scripts_dir.exists():
        errors.append("scripts directory not found")
        return errors, warnings

    # Required scripts
    required_scripts = [
        "bootstrap.sh",
        "task-claim.py",
        "dependency-check.py",
        "health-check.py",
    ]

    for script in required_scripts:
        script_path = scripts_dir / script
        if not script_path.exists():
            errors.append(f"Required script not found: {script}")
        elif not os.access(script_path, os.R_OK):
            errors.append(f"Script not readable: {script}")
        elif script.endswith(".sh") and not os.access(script_path, os.X_OK):
            warnings.append(f"Shell script not executable: {script}")

    # Optional but recommended scripts
    optional_scripts = [
        "cleanup-stale.py",
        "update-status.py",
        "generate-summary.py",
        "issue-to-task.py",
        "archive-completed.py",
    ]

    for script in optional_scripts:
        script_path = scripts_dir / script
        if not script_path.exists():
            warnings.append(f"Optional script not found: {script}")

    return errors, warnings


def validate_github_templates():
    """Validate GitHub issue and workflow templates"""
    errors = []
    warnings = []

    # Check for GitHub workflows
    workflows_dir = Path(".github/workflows")
    if workflows_dir.exists():
        conductor_workflow = workflows_dir / "conductor.yml"
        if not conductor_workflow.exists():
            warnings.append("conductor.yml workflow not found")
        else:
            # Check workflow content
            try:
                with open(conductor_workflow, "r") as f:
                    content = f.read()
                    if "workflow-state.json" in content:
                        errors.append(
                            "conductor.yml still references workflow-state.json (needs update)"
                        )
            except Exception as e:
                warnings.append(f"Could not read conductor.yml: {e}")
    else:
        warnings.append(".github/workflows directory not found")

    # Check for issue templates
    issue_templates_dir = Path(".github/ISSUE_TEMPLATE")
    if issue_templates_dir.exists():
        task_template = issue_templates_dir / "conductor-task.yml"
        if not task_template.exists():
            warnings.append("conductor-task.yml issue template not found")
        else:
            # Validate template content
            try:
                with open(task_template, "r") as f:
                    template = yaml.safe_load(f)
                    if not template.get("labels"):
                        warnings.append("Task template missing labels")
                    elif "conductor:task" not in template.get("labels", []):
                        errors.append(
                            "Task template must include 'conductor:task' label"
                        )
            except Exception as e:
                warnings.append(f"Could not parse task template: {e}")
    else:
        warnings.append("GitHub issue templates directory not found")

    return errors, warnings


def validate_existing_issues():
    """Check for existing conductor issues"""
    errors = []
    warnings = []

    # Check for any conductor tasks
    output = run_gh_command(
        [
            "issue",
            "list",
            "-l",
            "conductor:task",
            "--state",
            "all",
            "--limit",
            "1",
            "--json",
            "number",
        ]
    )

    if output:
        try:
            issues = json.loads(output)
            if not issues:
                warnings.append(
                    "No conductor tasks found. Create issues with 'conductor:task' label"
                )
        except json.JSONDecodeError:
            pass

    # Check for status issue
    output = run_gh_command(
        [
            "issue",
            "list",
            "-l",
            "conductor:status",
            "--state",
            "open",
            "--limit",
            "1",
            "--json",
            "number",
        ]
    )

    if output:
        try:
            issues = json.loads(output)
            if not issues:
                warnings.append(
                    "No status issue found. Run 'python .conductor/scripts/update-status.py' to create one"
                )
        except json.JSONDecodeError:
            pass

    return errors, warnings


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Validate conductor configuration")
    parser.add_argument(
        "--strict", action="store_true", help="Treat warnings as errors"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Attempt to fix issues (create missing labels)",
    )

    args = parser.parse_args()

    print("🔍 Validating Code-Conductor configuration...")
    print("   GitHub-native integration (v2.0.0+)")

    all_errors = []
    all_warnings = []

    # Run all validations
    validations = [
        ("Configuration", validate_config_yaml),
        ("GitHub CLI", validate_github_cli),
        ("GitHub Labels", validate_github_labels),
        ("Role Files", validate_role_files),
        ("Scripts", validate_scripts),
        ("GitHub Templates", validate_github_templates),
        ("Existing Issues", validate_existing_issues),
    ]

    for name, validator in validations:
        print(f"\n📋 Validating {name}...")
        errors, warnings = validator()

        if errors:
            print(f"❌ {len(errors)} error(s) found:")
            for error in errors:
                print(f"   - {error}")
            all_errors.extend(errors)

        if warnings:
            print(f"⚠️  {len(warnings)} warning(s) found:")
            for warning in warnings:
                print(f"   - {warning}")
            all_warnings.extend(warnings)

        if not errors and not warnings:
            print("✅ No issues found")

    # Fix mode
    if args.fix and all_warnings:
        print("\n🔧 Attempting to fix issues...")
        # Create missing labels
        for warning in all_warnings:
            if "Required label" in warning and "not found" in warning:
                label = warning.split("'")[1]
                print(f"   Creating label: {label}")
                run_gh_command(["label", "create", label, "--color", "0e8a16"])

    # Summary
    print("\n📊 Validation Summary")
    print(f"  Errors: {len(all_errors)}")
    print(f"  Warnings: {len(all_warnings)}")

    if all_errors:
        print("\n❌ Configuration validation failed")
        print("   Fix the errors above and run validation again")
        sys.exit(1)
    elif all_warnings and args.strict:
        print("\n❌ Configuration validation failed (strict mode)")
        sys.exit(1)
    elif all_warnings:
        print("\n⚠️  Configuration validation passed with warnings")
        print("   Consider addressing the warnings for optimal performance")
        sys.exit(0)
    else:
        print("\n✅ Configuration validation passed")
        print("   Your Code-Conductor setup is ready for GitHub-native operation!")
        sys.exit(0)


if __name__ == "__main__":
    main()
