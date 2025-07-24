#!/usr/bin/env python3
"""Create code review tasks from pull request events"""

import argparse
import json
import subprocess
import sys
from typing import Dict, Optional


def run_gh_command(args: list) -> Dict:
    """Run a GitHub CLI command and return JSON output"""
    try:
        result = subprocess.run(
            ["gh"] + args, capture_output=True, text=True, check=True
        )
        return json.loads(result.stdout) if result.stdout else {}
    except subprocess.CalledProcessError as e:
        print(f"Error running gh command: {e}")
        print(f"stderr: {e.stderr}")
        sys.exit(1)


def get_pr_info(pr_number: str, repo: str) -> Dict:
    """Get detailed PR information"""
    return run_gh_command(
        [
            "pr",
            "view",
            pr_number,
            "--repo",
            repo,
            "--json",
            (
                "number,title,body,author,files,additions,deletions,"
                "labels,headRefName,baseRefName,isDraft,state"
            ),
        ]
    )


def check_existing_review_task(pr_number: str, repo: str) -> Optional[int]:
    """Check if a review task already exists for this PR"""
    issues = run_gh_command(
        [
            "issue",
            "list",
            "--repo",
            repo,
            "--label",
            "conductor:task,code-review",
            "--state",
            "open",
            "--json",
            "number,title,body",
        ]
    )

    for issue in issues:
        # Check if issue references this PR
        if f"PR #{pr_number}" in issue.get(
            "title", ""
        ) or f"PR #{pr_number}" in issue.get("body", ""):
            return issue["number"]

    return None


def calculate_priority(pr_info: Dict) -> str:
    """Calculate priority based on PR characteristics"""
    additions = pr_info.get("additions", 0)
    deletions = pr_info.get("deletions", 0)
    total_changes = additions + deletions

    # Priority based on change size
    if total_changes > 500:
        return "high"
    elif total_changes > 100:
        return "medium"
    else:
        return "low"


def calculate_effort(pr_info: Dict) -> str:
    """Calculate effort based on PR characteristics"""
    files_changed = len(pr_info.get("files", []))
    additions = pr_info.get("additions", 0)
    deletions = pr_info.get("deletions", 0)
    total_changes = additions + deletions

    # Effort based on files and changes
    if files_changed > 20 or total_changes > 500:
        return "large"
    elif files_changed > 5 or total_changes > 100:
        return "medium"
    else:
        return "small"


def create_review_task_body(pr_info: Dict, pr_number: str, repo: str) -> str:
    """Create the issue body for the review task"""
    files = pr_info.get("files", [])
    file_list = "\n".join(
        [f"- `{f['path']}` (+{f['additions']}/-{f['deletions']})" for f in files[:20]]
    )
    if len(files) > 20:
        file_list += f"\n- ... and {len(files) - 20} more files"

    body = f"""## 🔍 Code Review Task

**Pull Request:** #{pr_number} - {pr_info['title']}
**Author:** @{pr_info['author']['login']}
**Branch:** `{pr_info['headRefName']}` → `{pr_info['baseRefName']}`
**Changes:** +{pr_info['additions']} / -{pr_info['deletions']} lines \\
in {len(files)} files

### 📋 Review Checklist

Please review the following aspects:

- [ ] **Code Quality**: Is the code clean, readable, and following project conventions?
- [ ] **Logic & Correctness**: Are there any bugs or logic errors?
- [ ] **Security**: Are there any security vulnerabilities or concerns?
- [ ] **Performance**: Are there any performance issues or inefficiencies?
- [ ] **Testing**: Are changes adequately tested? Need more tests?
- [ ] **Documentation**: Are complex parts documented? Updated user docs?
- [ ] **Dependencies**: Are new deps necessary and properly licensed?
- [ ] **Breaking Changes**: Any breaking changes to communicate?

### 📁 Files Changed

{file_list}

### 🎯 Success Criteria

- Complete all checklist items
- Post a comprehensive review comment on the PR
- Identify any blocking issues that must be addressed
- Suggest improvements (non-blocking) where applicable
- Approve or request changes as appropriate

### 🤖 Agent Instructions

1. Use `gh pr checkout {pr_number}` to review the code locally
2. Run existing tests to ensure they pass
3. Review each file systematically
4. Focus on the most critical issues first
5. Be constructive and specific in feedback
6. Post your review using `gh pr review {pr_number} --comment --body "your review"`

### 📝 PR Description

{pr_info.get('body', '_No description provided_')}

---
_This task was automatically created for PR #{pr_number}_
"""

    return body


def create_issue(pr_info: Dict, pr_number: str, repo: str, event_type: str) -> int:
    """Create a new review task issue"""
    title = f"🔍 Code Review: PR #{pr_number} - {pr_info['title']}"
    body = create_review_task_body(pr_info, pr_number, repo)

    # Determine labels
    labels = ["conductor:task", "code-review"]

    # Add priority label
    priority = calculate_priority(pr_info)
    labels.append(f"priority:{priority}")

    # Add effort label
    effort = calculate_effort(pr_info)
    labels.append(f"effort:{effort}")

    # Create the issue
    cmd = ["gh", "issue", "create", "--repo", repo, "--title", title, "--body", body]

    for label in labels:
        cmd.extend(["--label", label])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        # gh issue create returns the issue URL, extract the number
        issue_url = result.stdout.strip()
        issue_number = issue_url.split("/")[-1]
        print(f"✅ Created review task issue #{issue_number}")
    except subprocess.CalledProcessError as e:
        print(f"Error creating issue: {e}")
        print(f"stderr: {e.stderr}")
        sys.exit(1)

    # Add comment to PR linking to review task
    comment = f"""🤖 **Code Review Task Created**

I've created a review task for this PR: #{issue_number}

An AI agent will claim this task and provide a comprehensive code review. \\
You can track progress on the issue.

_This is part of the Code Conductor automated review system._"""

    subprocess.run(
        ["gh", "pr", "comment", pr_number, "--repo", repo, "--body", comment],
        check=True,
    )

    return int(issue_number)


def main():
    parser = argparse.ArgumentParser(description="Create code review task from PR")
    parser.add_argument("--pr-number", required=True, help="Pull request number")
    parser.add_argument("--repo", required=True, help="Repository (owner/name)")
    parser.add_argument(
        "--event-type",
        choices=["pr_event", "comment_trigger"],
        default="pr_event",
        help="How the task was triggered",
    )

    args = parser.parse_args()

    # Get PR information
    print(f"📋 Getting information for PR #{args.pr_number}")
    pr_info = get_pr_info(args.pr_number, args.repo)

    # Check PR state
    if pr_info.get("state") != "OPEN":
        print(f"⚠️ PR #{args.pr_number} is not open (state: {pr_info.get('state')})")
        sys.exit(0)

    if pr_info.get("isDraft", False) and args.event_type == "pr_event":
        print(f"⚠️ PR #{args.pr_number} is a draft, skipping review task creation")
        sys.exit(0)

    # Check if review task already exists
    existing_issue = check_existing_review_task(args.pr_number, args.repo)

    if existing_issue and args.event_type == "pr_event":
        print(f"ℹ️ Review task already exists: #{existing_issue}")
        sys.exit(0)
    elif existing_issue and args.event_type == "comment_trigger":
        print(f"ℹ️ Updating existing review task: #{existing_issue}")
        # Add a comment to the existing issue
        subprocess.run(
            [
                "gh",
                "issue",
                "comment",
                str(existing_issue),
                "--repo",
                args.repo,
                "--body",
                "📌 Re-review requested via `/conductor review` command",
            ],
            check=True,
        )
        sys.exit(0)

    # Create new review task
    issue_number = create_issue(pr_info, args.pr_number, args.repo, args.event_type)

    print(
        f"✅ Successfully created review task #{issue_number} for PR #{args.pr_number}"
    )


if __name__ == "__main__":
    main()
