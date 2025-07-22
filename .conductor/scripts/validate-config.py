#!/usr/bin/env python3
"""Validate conductor configuration"""

import json
import yaml
import sys
from pathlib import Path
import os


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

    # Validate agent settings
    if "agent_settings" in config:
        settings = config["agent_settings"]
        if "heartbeat_interval" in settings:
            try:
                interval = int(settings["heartbeat_interval"])
                if interval < 60:
                    warnings.append(
                        "Heartbeat interval less than 60 seconds may cause issues"
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


def validate_workflow_state():
    """Validate the workflow state file"""
    state_file = Path(".conductor/workflow-state.json")
    errors = []
    warnings = []

    if not state_file.exists():
        warnings.append("workflow-state.json not found (will be created)")
        return errors, warnings

    try:
        with open(state_file, "r") as f:
            state = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON in workflow-state.json: {e}")
        return errors, warnings

    # Required sections
    required_sections = ["active_work", "available_tasks", "completed_work"]
    for section in required_sections:
        if section not in state:
            warnings.append(f"Missing section in workflow-state.json: {section}")

    # Validate task structure
    if "available_tasks" in state:
        for i, task in enumerate(state["available_tasks"]):
            if not isinstance(task, dict):
                errors.append(f"Task {i} is not a dictionary")
                continue

            required_task_fields = ["id", "title"]
            for field in required_task_fields:
                if field not in task:
                    errors.append(f"Task {i} missing required field: {field}")

            # Validate effort levels
            if "estimated_effort" in task:
                effort = task["estimated_effort"]
                valid_efforts = ["small", "medium", "large"]
                if effort not in valid_efforts:
                    warnings.append(f"Task {i} has invalid effort level: {effort}")

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
    optional_scripts = ["cleanup-stale.py", "update-status.py", "generate-summary.py"]

    for script in optional_scripts:
        script_path = scripts_dir / script
        if not script_path.exists():
            warnings.append(f"Optional script not found: {script}")

    return errors, warnings


def validate_github_integration():
    """Validate GitHub integration setup"""
    errors = []
    warnings = []

    # Check for GitHub workflows
    workflows_dir = Path(".github/workflows")
    if workflows_dir.exists():
        conductor_workflow = workflows_dir / "conductor.yml"
        if not conductor_workflow.exists():
            warnings.append("conductor.yml workflow not found")
    else:
        warnings.append(".github/workflows directory not found")

    # Check for issue templates
    issue_templates_dir = Path(".github/ISSUE_TEMPLATE")
    if issue_templates_dir.exists():
        task_template = issue_templates_dir / "conductor-task.yml"
        if not task_template.exists():
            warnings.append("conductor-task.yml issue template not found")
    else:
        warnings.append("GitHub issue templates not found")

    return errors, warnings


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Validate conductor configuration")
    parser.add_argument(
        "--strict", action="store_true", help="Treat warnings as errors"
    )

    args = parser.parse_args()

    print("🔍 Validating conductor configuration...")

    all_errors = []
    all_warnings = []

    # Run all validations
    validations = [
        ("Configuration", validate_config_yaml),
        ("Workflow State", validate_workflow_state),
        ("Role Files", validate_role_files),
        ("Scripts", validate_scripts),
        ("GitHub Integration", validate_github_integration),
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

    # Summary
    print("\n📊 Validation Summary")
    print(f"  Errors: {len(all_errors)}")
    print(f"  Warnings: {len(all_warnings)}")

    if all_errors:
        print("\n❌ Configuration validation failed")
        sys.exit(1)
    elif all_warnings and args.strict:
        print("\n❌ Configuration validation failed (strict mode)")
        sys.exit(1)
    elif all_warnings:
        print("\n⚠️  Configuration validation passed with warnings")
        sys.exit(0)
    else:
        print("\n✅ Configuration validation passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
