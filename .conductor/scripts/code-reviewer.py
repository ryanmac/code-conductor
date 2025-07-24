#!/usr/bin/env python3
"""AI-powered code reviewer for pull requests"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class CodeReviewer:
    def __init__(self, pr_number: str, repo: str):
        self.pr_number = pr_number
        self.repo = repo
        # Try multiple token sources in order of preference
        self.github_token = (
            os.getenv("GH_TOKEN")
            or os.getenv("GITHUB_TOKEN")
            or os.getenv("CONDUCTOR_GITHUB_TOKEN")
        )
        self.review_comments = []
        self.summary = {
            "security_issues": [],
            "bugs": [],
            "improvements": [],
            "style_issues": [],
            "test_suggestions": [],
        }

    def get_pr_diff(self) -> str:
        """Get the diff for the PR"""
        try:
            cmd = ["gh", "pr", "diff", self.pr_number, "--repo", self.repo]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error getting PR diff: {e}")
            return ""

    def get_pr_files(self) -> List[str]:
        """Get list of changed files in the PR"""
        try:
            cmd = [
                "gh",
                "pr",
                "view",
                self.pr_number,
                "--repo",
                self.repo,
                "--json",
                "files",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            return [f["path"] for f in data.get("files", [])]
        except subprocess.CalledProcessError as e:
            print(f"Error getting PR files: {e}")
            return []

    def analyze_security(self, diff: str, files: List[str]) -> None:
        """Analyze for security issues"""
        security_patterns = {
            r"api[_-]?key.*=.*['\"][\w]+['\"]": "Hardcoded API key detected",
            r"password.*=.*['\"][\w]+['\"]": "Hardcoded password detected",
            r"secret.*=.*['\"][\w]+['\"]": "Hardcoded secret detected",
            r"eval\s*\(": "Dangerous eval() usage",
            r"exec\s*\(": "Dangerous exec() usage",
            r"subprocess.*shell\s*=\s*True": "Shell injection risk with subprocess",
            r"pickle\.loads?\s*\(": "Unsafe pickle deserialization",
            r"yaml\.load\s*\(": "Unsafe YAML loading (use safe_load)",
        }

        for pattern, message in security_patterns.items():
            matches = re.finditer(pattern, diff, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                self.summary["security_issues"].append(
                    {"pattern": pattern, "message": message, "line": match.group(0)}
                )

    def analyze_bugs(self, diff: str) -> None:
        """Analyze for potential bugs"""
        bug_patterns = {
            r"except\s*:": "Bare except clause - specify exception type",
            r"if\s+[\w\[\]\.]+\s*=\s*": "Assignment in if condition (use == for comparison)",
            r"return\s+$": "Empty return statement in non-void function",
            r"TODO|FIXME|XXX|HACK": "Unresolved TODO/FIXME comment",
            r"print\s*\(": "Debug print statement left in code",
            r"console\.log": "Debug console.log left in code",
            r"import\s+\*": "Wildcard import can cause namespace pollution",
        }

        for pattern, message in bug_patterns.items():
            matches = re.finditer(pattern, diff, re.MULTILINE)
            for match in matches:
                # Check if this is in added lines (starting with +)
                line_start = diff.rfind("\n", 0, match.start()) + 1
                if diff[line_start : line_start + 1] == "+":
                    self.summary["bugs"].append(
                        {"pattern": pattern, "message": message, "line": match.group(0)}
                    )

    def analyze_code_quality(self, diff: str) -> None:
        """Analyze code quality and suggest improvements"""
        # Check for long functions
        function_pattern = r"^\+\s*(def|function|func)\s+(\w+)"
        matches = re.finditer(function_pattern, diff, re.MULTILINE)

        for match in matches:
            func_name = match.group(2)
            # Count lines until next function or class
            func_start = match.end()
            next_func = re.search(
                r"^\+?\s*(def|function|func|class)\s+", diff[func_start:], re.MULTILINE
            )
            func_end = func_start + next_func.start() if next_func else len(diff)

            func_lines = diff[func_start:func_end].count("\n")
            if func_lines > 50:
                self.summary["improvements"].append(
                    {
                        "type": "long_function",
                        "message": f"Function '{func_name}' is {func_lines} lines long. Consider breaking it down.",
                        "function": func_name,
                    }
                )

        # Check for missing docstrings
        function_without_docstring = (
            r"^\+\s*(def|class)\s+(\w+).*:\s*\n(?!\+\s*[\"']{3})"
        )
        matches = re.finditer(function_without_docstring, diff, re.MULTILINE)
        for match in matches:
            name = match.group(2)
            self.summary["style_issues"].append(
                {
                    "type": "missing_docstring",
                    "message": f"Missing docstring for '{name}'",
                    "name": name,
                }
            )

    def suggest_tests(self, files: List[str]) -> None:
        """Suggest tests for changed files"""
        for file in files:
            if (
                file.endswith(".py")
                and not file.startswith("test_")
                and "test" not in file
            ):
                test_file = f"test_{Path(file).name}"
                self.summary["test_suggestions"].append(
                    {
                        "file": file,
                        "suggestion": f"Consider adding tests in '{test_file}'",
                    }
                )
            elif (
                file.endswith((".js", ".ts"))
                and not file.includes("test")
                and not file.includes("spec")
            ):
                test_file = file.replace(".js", ".test.js").replace(".ts", ".test.ts")
                self.summary["test_suggestions"].append(
                    {
                        "file": file,
                        "suggestion": f"Consider adding tests in '{test_file}'",
                    }
                )

    def format_review_comment(self, issue_type: str, issues: List[Dict]) -> str:
        """Format issues into a review comment"""
        if not issues:
            return ""

        icons = {
            "security_issues": "🔒",
            "bugs": "🐛",
            "improvements": "💡",
            "style_issues": "🎨",
            "test_suggestions": "🧪",
        }

        titles = {
            "security_issues": "Security Issues",
            "bugs": "Potential Bugs",
            "improvements": "Suggested Improvements",
            "style_issues": "Style Issues",
            "test_suggestions": "Test Coverage",
        }

        comment = f"\n### {icons.get(issue_type, '📝')} {titles.get(issue_type, issue_type)}\n\n"

        for issue in issues:
            if "message" in issue:
                comment += f"- {issue['message']}\n"
                if "line" in issue:
                    comment += f"  ```\n  {issue['line']}\n  ```\n"
            elif "suggestion" in issue:
                comment += f"- {issue['suggestion']}\n"

        return comment

    def post_review(self) -> None:
        """Post the review as a PR comment"""
        if not any(self.summary.values()):
            # No issues found
            comment = "## 🤖 AI Code Review\n\n✅ No issues found! The code looks good."
        else:
            comment = "## 🤖 AI Code Review\n\n"
            comment += "I've reviewed the changes and found the following:\n"

            # Add summary stats
            total_issues = sum(len(issues) for issues in self.summary.values())
            comment += f"\n**Total issues found:** {total_issues}\n"

            # Add detailed sections
            for issue_type, issues in self.summary.items():
                if issues:
                    comment += self.format_review_comment(issue_type, issues)

            comment += "\n---\n*This is an automated review. Please verify suggestions before implementing.*"

        # Post comment using gh CLI
        try:
            cmd = [
                "gh",
                "pr",
                "comment",
                self.pr_number,
                "--repo",
                self.repo,
                "--body",
                comment,
            ]
            subprocess.run(cmd, check=True)
            print(f"✅ Review posted to PR #{self.pr_number}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error posting review: {e}")

        # Save summary for GitHub Actions
        summary_file = Path(".conductor/review-summary.md")
        summary_file.parent.mkdir(exist_ok=True)
        with open(summary_file, "w") as f:
            f.write(comment)

    def review(self) -> None:
        """Run the complete review process"""
        print(f"🔍 Reviewing PR #{self.pr_number} in {self.repo}")

        # Get PR information
        diff = self.get_pr_diff()
        files = self.get_pr_files()

        if not diff:
            print("❌ Could not retrieve PR diff")
            return

        print(f"📝 Analyzing {len(files)} changed files...")

        # Run analyses
        self.analyze_security(diff, files)
        self.analyze_bugs(diff)
        self.analyze_code_quality(diff)
        self.suggest_tests(files)

        # Post review
        self.post_review()


def main():
    parser = argparse.ArgumentParser(description="AI-powered code reviewer")
    parser.add_argument("--pr-number", required=True, help="Pull request number")
    parser.add_argument("--repo", required=True, help="Repository (owner/name)")

    args = parser.parse_args()

    reviewer = CodeReviewer(args.pr_number, args.repo)
    reviewer.review()


if __name__ == "__main__":
    main()
