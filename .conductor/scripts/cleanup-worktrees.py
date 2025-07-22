#!/usr/bin/env python3
"""Clean up abandoned git worktrees"""

import os
import subprocess
import sys
import shutil
from pathlib import Path
from datetime import datetime, timedelta

def get_worktrees():
    """Get list of current git worktrees"""
    try:
        result = subprocess.run(['git', 'worktree', 'list'],
                              capture_output=True, text=True, check=True)
        worktrees = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split()
                if len(parts) >= 2:
                    path = parts[0]
                    branch = parts[1] if len(parts) > 1 else None
                    worktrees.append({'path': path, 'branch': branch})
        return worktrees
    except subprocess.CalledProcessError:
        print("❌ Failed to list git worktrees")
        return []

def is_worktree_stale(worktree_path, max_age_hours=24):
    """Check if a worktree is stale based on last modification time"""
    try:
        path = Path(worktree_path)
        if not path.exists():
            return True

        # Check last modification time of the worktree directory
        stat = path.stat()
        last_modified = datetime.fromtimestamp(stat.st_mtime)
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

        return last_modified < cutoff_time
    except OSError:
        return True

def is_conductor_worktree(worktree_path):
    """Check if this is a conductor-generated worktree"""
    path = Path(worktree_path)

    # Check if it's in the worktrees directory
    if 'worktrees' in path.parts:
        return True

    # Check if the branch name follows conductor pattern
    try:
        result = subprocess.run(['git', 'branch', '--show-current'],
                              cwd=worktree_path, capture_output=True, text=True, check=True)
        branch = result.stdout.strip()
        return branch.startswith('agent-')
    except subprocess.CalledProcessError:
        return False

def remove_worktree(worktree_path, force=False):
    """Remove a git worktree"""
    try:
        # First try git worktree remove
        cmd = ['git', 'worktree', 'remove', worktree_path]
        if force:
            cmd.append('--force')

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ Removed worktree: {worktree_path}")
            return True
        else:
            # If git command failed, try manual removal
            if force and Path(worktree_path).exists():
                shutil.rmtree(worktree_path)
                print(f"✅ Force removed worktree directory: {worktree_path}")
                return True
            else:
                print(f"⚠️  Failed to remove worktree: {worktree_path}")
                print(f"   Error: {result.stderr.strip()}")
                return False
    except Exception as e:
        print(f"❌ Error removing worktree {worktree_path}: {e}")
        return False

def cleanup_worktree_branches():
    """Clean up branches that no longer have worktrees"""
    try:
        # Get all branches
        result = subprocess.run(['git', 'branch'], capture_output=True, text=True, check=True)
        branches = []
        for line in result.stdout.split('\n'):
            line = line.strip()
            if line and not line.startswith('*'):
                branch = line.replace('*', '').strip()
                branches.append(branch)

        # Get current worktrees
        worktrees = get_worktrees()
        worktree_branches = {wt.get('branch') for wt in worktrees if wt.get('branch')}

        # Find orphaned agent branches
        orphaned_branches = []
        for branch in branches:
            if branch.startswith('agent-') and branch not in worktree_branches:
                orphaned_branches.append(branch)

        # Remove orphaned branches
        removed_count = 0
        for branch in orphaned_branches:
            try:
                subprocess.run(['git', 'branch', '-D', branch],
                             capture_output=True, text=True, check=True)
                print(f"🗑️  Deleted orphaned branch: {branch}")
                removed_count += 1
            except subprocess.CalledProcessError as e:
                print(f"⚠️  Failed to delete branch {branch}: {e}")

        return removed_count
    except subprocess.CalledProcessError:
        print("⚠️  Failed to clean up orphaned branches")
        return 0

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Clean up abandoned git worktrees")
    parser.add_argument("--max-age", type=int, default=24,
                       help="Maximum age in hours for worktrees (default: 24)")
    parser.add_argument("--force", action="store_true",
                       help="Force removal of worktrees with uncommitted changes")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be done without making changes")
    parser.add_argument("--all", action="store_true",
                       help="Clean up all conductor worktrees regardless of age")

    args = parser.parse_args()

    print("🧹 Cleaning up git worktrees...")

    # Get current worktrees
    worktrees = get_worktrees()

    if not worktrees:
        print("ℹ️  No worktrees found")
        return

    # Filter for conductor worktrees
    conductor_worktrees = []
    for wt in worktrees:
        path = wt['path']
        if path != '.' and is_conductor_worktree(path):  # Skip main worktree
            conductor_worktrees.append(wt)

    if not conductor_worktrees:
        print("ℹ️  No conductor worktrees found")
        return

    print(f"📂 Found {len(conductor_worktrees)} conductor worktree(s)")

    # Identify stale worktrees
    stale_worktrees = []
    for wt in conductor_worktrees:
        path = wt['path']
        if args.all or is_worktree_stale(path, args.max_age):
            stale_worktrees.append(wt)

    if not stale_worktrees:
        print(f"✅ No stale worktrees found (max age: {args.max_age} hours)")
        return

    print(f"🗑️  Found {len(stale_worktrees)} stale worktree(s)")

    if args.dry_run:
        print("\n(DRY RUN - showing what would be removed)")
        for wt in stale_worktrees:
            print(f"  - {wt['path']} (branch: {wt.get('branch', 'unknown')})")
        print(f"\nRun without --dry-run to remove {len(stale_worktrees)} worktree(s)")
        return

    # Remove stale worktrees
    removed_count = 0
    for wt in stale_worktrees:
        path = wt['path']
        if remove_worktree(path, args.force):
            removed_count += 1

    # Clean up orphaned branches
    orphaned_branches = cleanup_worktree_branches()

    # Summary
    print(f"\n📊 Cleanup Summary")
    print(f"  Worktrees removed: {removed_count}")
    print(f"  Branches cleaned: {orphaned_branches}")
    print(f"  Remaining worktrees: {len(conductor_worktrees) - removed_count}")

    if removed_count > 0:
        print("\n✅ Worktree cleanup completed")
    else:
        print("\n⚠️  No worktrees were removed")

if __name__ == "__main__":
    main() 