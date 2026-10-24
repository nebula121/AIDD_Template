#!/usr/bin/env python3
import sys
import os
import argparse
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

def find_repo_root() -> Path:
    """Find repository root by looking for .git or AGENTS.md in parents."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / ".git").exists() or (parent / "AGENTS.md").exists():
            return parent
    return Path.cwd()

def run_command(cmd, check=True, cwd=None, capture_output=True, text=True):
    return subprocess.run(cmd, check=check, cwd=cwd, capture_output=capture_output, text=text, encoding='utf-8', errors='replace')

def main():
    parser = argparse.ArgumentParser(description="Start feature branch creation workflow.")
    parser.add_argument("-b", "--branch-name", required=True, help="Target feature branch name (e.g. feature/issue-123-title)")
    parser.add_argument("--base-branch", default="main", help="Base branch name to branch off from (default: main)")
    parser.add_argument("--auto-stash", action="store_true", help="Auto stash uncommitted tracked changes before switching branch")

    args = parser.parse_args()

    root_dir = find_repo_root()
    os.chdir(root_dir)

    base_branch = args.base_branch
    print(f"=== Starting Feature Branch Creation Workflow (Base: {base_branch}) ===")

    # 1. Check for uncommitted tracked changes
    res = run_command(["git", "status", "--porcelain", "-uno"], check=False)
    status_output = res.stdout.strip() if res.stdout else ""

    if status_output:
        if args.auto_stash:
            print("Uncommitted changes detected. AutoStash requested: running git stash...")
            run_command(["git", "stash", "push", "-m", "AutoStash by start_feature_branch script"])
        else:
            print("Error: Working directory has uncommitted tracked changes. Pass --auto-stash or commit/stash them before creating a new branch.", file=sys.stderr)
            sys.exit(1)

    # 2. Switch to base branch
    print(f"Switching to {base_branch} branch...")
    res = run_command(["git", "checkout", base_branch], check=False)
    if res.returncode != 0:
        print(f"Error: Failed to checkout {base_branch} branch:\n{res.stderr}", file=sys.stderr)
        sys.exit(res.returncode)

    # 3. Pull latest base branch if remote exists
    remotes_res = run_command(["git", "remote"], check=False)
    has_remote = bool(remotes_res.stdout and "origin" in remotes_res.stdout.splitlines())

    if has_remote:
        # Try gh auth setup-git if available
        try:
            run_command(["gh", "auth", "setup-git"], check=False)
        except Exception:
            pass

        print(f"Pulling latest changes from origin/{base_branch}...")
        res = run_command(["git", "pull", "origin", base_branch], check=False)
        if res.returncode != 0:
            print(f"Warning: Failed to pull origin {base_branch}:\n{res.stderr}\nContinuing with local {base_branch}...", file=sys.stderr)
    else:
        print("Notice: No 'origin' remote found. Skipping pull.")

    # 4. Create and switch to target feature branch
    print(f"Creating/switching to feature branch '{args.branch_name}'...")
    res = run_command(["git", "checkout", "-b", args.branch_name], check=False)
    if res.returncode != 0:
        # If branch already exists, switch to it
        res = run_command(["git", "checkout", args.branch_name], check=False)
        if res.returncode != 0:
            print(f"Error: Failed to checkout branch {args.branch_name}:\n{res.stderr}", file=sys.stderr)
            sys.exit(res.returncode)

    res = run_command(["git", "branch", "--show-current"])
    current = res.stdout.strip()
    if current != args.branch_name:
        print(f"Error: Branch checkout verification failed! Active branch is '{current}', expected '{args.branch_name}'.", file=sys.stderr)
        sys.exit(1)

    print(f"Successfully verified active branch is '{args.branch_name}' (based on {base_branch}).")

if __name__ == "__main__":
    main()
