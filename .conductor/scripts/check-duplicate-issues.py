#!/usr/bin/env python3
"""
Check for duplicate or similar issues before creating a new one.

This script helps prevent duplicate GitHub issues by searching for similar
existing issues based on title and keywords.
"""

import json
import subprocess
import sys
from difflib import SequenceMatcher
import re
import argparse


def run_gh_command(args):
    """Run a GitHub CLI command and return the output."""
    try:
        result = subprocess.run(
            ["gh"] + args, capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running gh command: {e}")
        print(f"stderr: {e.stderr}")
        return None


def get_all_issues(label="conductor:task", limit=200):
    """Get all issues with the specified label."""
    # Get open issues
    open_issues = run_gh_command(
        [
            "issue",
            "list",
            "--label",
            label,
            "--state",
            "open",
            "--limit",
            str(limit),
            "--json",
            "number,title,body,labels,state",
        ]
    )

    # Get closed issues (last 50)
    closed_issues = run_gh_command(
        [
            "issue",
            "list",
            "--label",
            label,
            "--state",
            "closed",
            "--limit",
            "50",
            "--json",
            "number,title,body,labels,state",
        ]
    )

    all_issues = []
    if open_issues:
        all_issues.extend(json.loads(open_issues))
    if closed_issues:
        all_issues.extend(json.loads(closed_issues))

    return all_issues


def extract_keywords(text):
    """Extract meaningful keywords from text."""
    # Remove common words and clean up
    stop_words = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "from",
        "up",
        "about",
        "into",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "between",
        "under",
        "again",
        "further",
        "then",
        "once",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "must",
        "shall",
        "can",
        "need",
    }

    # Convert to lowercase and split
    words = re.findall(r"\b\w+\b", text.lower())

    # Filter out stop words and short words
    keywords = [w for w in words if w not in stop_words and len(w) > 2]

    return set(keywords)


def calculate_similarity(title1, title2, body1="", body2=""):
    """Calculate similarity between two issues."""
    # Title similarity (weighted more heavily)
    title_ratio = SequenceMatcher(None, title1.lower(), title2.lower()).ratio()

    # Keyword overlap
    keywords1 = extract_keywords(f"{title1} {body1}")
    keywords2 = extract_keywords(f"{title2} {body2}")

    if keywords1 and keywords2:
        overlap = len(keywords1.intersection(keywords2))
        total = len(keywords1.union(keywords2))
        keyword_ratio = overlap / total if total > 0 else 0
    else:
        keyword_ratio = 0

    # Combined score (title is more important)
    combined_score = (title_ratio * 0.7) + (keyword_ratio * 0.3)

    return {
        "title_similarity": title_ratio,
        "keyword_overlap": keyword_ratio,
        "combined_score": combined_score,
    }


def check_for_duplicates(new_title, new_body="", threshold=0.6):
    """Check if a similar issue already exists."""
    print(f"🔍 Checking for duplicates of: '{new_title}'")
    print("=" * 80)

    # Get all existing issues
    issues = get_all_issues()

    if not issues:
        print("❌ Could not fetch issues from GitHub")
        return []

    print(f"📊 Analyzing {len(issues)} existing issues...")

    # Find similar issues
    similar_issues = []

    for issue in issues:
        similarity = calculate_similarity(
            new_title, issue["title"], new_body, issue.get("body", "")
        )

        if similarity["combined_score"] >= threshold:
            similar_issues.append({"issue": issue, "similarity": similarity})

    # Sort by similarity score
    similar_issues.sort(key=lambda x: x["similarity"]["combined_score"], reverse=True)

    return similar_issues


def search_by_keywords(keywords):
    """Search for issues containing specific keywords."""
    search_query = " OR ".join(keywords)

    result = run_gh_command(
        [
            "issue",
            "list",
            "--search",
            search_query,
            "--state",
            "all",
            "--limit",
            "20",
            "--json",
            "number,title,state,labels",
        ]
    )

    if result:
        return json.loads(result)
    return []


def main():
    parser = argparse.ArgumentParser(
        description="Check for duplicate GitHub issues before creating a new one"
    )
    parser.add_argument("title", help="Title of the issue you want to create")
    parser.add_argument(
        "--body", "-b", default="", help="Body/description of the issue"
    )
    parser.add_argument(
        "--threshold",
        "-t",
        type=float,
        default=0.6,
        help="Similarity threshold (0.0-1.0, default: 0.6)",
    )
    parser.add_argument(
        "--keywords", "-k", nargs="+", help="Additional keywords to search for"
    )

    args = parser.parse_args()

    # Check for duplicates
    similar_issues = check_for_duplicates(args.title, args.body, args.threshold)

    if similar_issues:
        print("\n⚠️  Found potentially similar issues:")
        print("-" * 80)

        for item in similar_issues:
            issue = item["issue"]
            sim = item["similarity"]

            state_icon = "🟢" if issue["state"] == "OPEN" else "🔴"
            print(f"\n{state_icon} #{issue['number']}: {issue['title']}")
            print(
                f"   Similarity: {sim['combined_score']:.1%} "
                + f"(title: {sim['title_similarity']:.1%}, "
                + f"keywords: {sim['keyword_overlap']:.1%})"
            )

            # Show labels
            labels = [label["name"] for label in issue.get("labels", [])]
            if labels:
                print(f"   Labels: {', '.join(labels)}")

    # Also search by keywords if provided
    if args.keywords:
        print(f"\n🔍 Searching for issues with keywords: {', '.join(args.keywords)}")
        keyword_results = search_by_keywords(args.keywords)

        if keyword_results:
            print(f"\nFound {len(keyword_results)} issues with matching keywords:")
            for issue in keyword_results[:5]:  # Show top 5
                state_icon = "🟢" if issue["state"] == "OPEN" else "🔴"
                print(f"{state_icon} #{issue['number']}: {issue['title']}")

    # Recommendation
    if similar_issues:
        highest_score = similar_issues[0]["similarity"]["combined_score"]
        if highest_score >= 0.8:
            print(
                "\n❌ RECOMMENDATION: Do NOT create this issue - very similar issue exists!"
            )
            print("   Consider adding to the existing issue instead.")
            return 1
        elif highest_score >= 0.6:
            print(
                "\n⚠️  RECOMMENDATION: Review similar issues carefully before creating."
            )
            print("   Your issue might be a duplicate or subset of an existing one.")
            return 2
    else:
        print("\n✅ No similar issues found. Safe to create new issue.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
