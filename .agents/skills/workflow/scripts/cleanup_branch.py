#!/usr/bin/env python3
import sys
import os
import json
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

def run_command(cmd, check=False, cwd=None, capture_output=True, text=True):
    return subprocess.run(cmd, check=check, cwd=cwd, capture_output=capture_output, text=text, encoding='utf-8', errors='replace')

def main():
    parser = argparse.ArgumentParser(description="Post-merge branch cleanup workflow.")
    parser.add_argument("-b", "--target-branch", required=True, help="Feature branch to delete")
    parser.add_argument("--base-branch", default="main", help="Base branch name (default: main)")
    parser.add_argument("-i", "--issue-number", type=int, default=0, help="Issue number for reference")
    parser.add_argument("-p", "--pull-request-number", type=int, default=0, help="Pull Request number for safety check")
    parser.add_argument("--delete-remote", action="store_true", help="Delete remote branch via GitHub API")
    parser.add_argument("--auto-stash", action="store_true", help="Auto stash uncommitted tracked changes before cleanup")

    args = parser.parse_args()

    root_dir = find_repo_root()
    os.chdir(root_dir)

    base_branch = args.base_branch
    target_branch = args.target_branch

    print(f"=== Starting Post-Merge Branch Cleanup Workflow (Target: {target_branch}, Base: {base_branch}) ===")

    # 0. Clean temporary workflow artifacts
    temp_files = [
        "diff_summary_for_agent.txt"
    ]
    for tf in temp_files:
        p = root_dir / tf
        if p.exists():
            try:
                p.unlink()
                print(f"Removed temporary artifact: {tf}")
            except Exception:
                pass

    # 1. Check for uncommitted tracked changes
    res_status = run_command(["git", "status", "--porcelain", "-uno"])
    if res_status.returncode != 0:
        print("Error: Failed to execute 'git status'.", file=sys.stderr)
        sys.exit(1)

    status_output = res_status.stdout.strip() if res_status.stdout else ""
    if status_output:
        if args.auto_stash:
            print("Uncommitted tracked changes detected. AutoStash requested: running git stash...")
            res_stash = run_command(["git", "stash", "push", "-m", "AutoStash by cleanup_branch script"])
            if res_stash.returncode != 0:
                print("Error: git stash failed.", file=sys.stderr)
                sys.exit(res_stash.returncode)
        else:
            print("Error: Working directory has uncommitted tracked changes. Pass --auto-stash or commit/stash them before cleanup.", file=sys.stderr)
            sys.exit(1)

    # 2. Determine target branch and verify safety
    if not target_branch:
        print("Error: TargetBranch parameter is mandatory.", file=sys.stderr)
        sys.exit(1)

    if target_branch == base_branch:
        print(f"Error: Cannot delete '{base_branch}' branch.", file=sys.stderr)
        sys.exit(1)

    # Verify PR merge status
    pr_query = str(args.pull_request_number) if args.pull_request_number > 0 else target_branch
    print(f"Verifying PR merge status for TargetBranch '{target_branch}' (query: {pr_query})...")
    res_pr = run_command(["gh", "pr", "view", pr_query, "--json", "number,headRefName,state,mergedAt"])
    if res_pr.returncode != 0 and args.issue_number > 0 and args.pull_request_number == 0:
        # Fallback to issue-number if query by branch name failed
        res_pr = run_command(["gh", "pr", "view", str(args.issue_number), "--json", "number,headRefName,state,mergedAt"])

    is_merged = False
    if res_pr.returncode == 0 and res_pr.stdout:
        try:
            pr_data = json.loads(res_pr.stdout)
            head_ref = pr_data.get("headRefName")
            pr_num = pr_data.get("number", pr_query)
            if head_ref and head_ref != target_branch:
                print(f"Error: Safety Check Failed: Specified TargetBranch '{target_branch}' does not match PR #{pr_num} head branch '{head_ref}'.", file=sys.stderr)
                sys.exit(1)

            merged_at = pr_data.get("mergedAt")
            state = pr_data.get("state")
            if state == "MERGED" or bool(merged_at):
                is_merged = True
                print(f"Verified PR #{pr_num} for '{target_branch}' is merged (mergedAt={merged_at}, state={state}).")
            else:
                print(f"Error: TargetBranch '{target_branch}' (PR #{pr_num}) is not merged (mergedAt={merged_at}, state={state}). Cleanup aborted to prevent data loss.", file=sys.stderr)
                sys.exit(1)
        except json.JSONDecodeError:
            print(f"Warning: Could not parse PR details JSON for query '{pr_query}'.")
    else:
        print(f"Warning: Could not fetch PR details for '{target_branch}' via GitHub CLI.")

    # 3. Switch to base branch
    print(f"Switching to {base_branch} branch...")
    res_co = run_command(["git", "checkout", base_branch])
    if res_co.returncode != 0:
        print(f"Error: Failed to checkout {base_branch} branch:\n{res_co.stderr}", file=sys.stderr)
        sys.exit(res_co.returncode)

    # 4. Pull latest base branch if remote exists
    remotes_res = run_command(["git", "remote"])
    has_remote = bool(remotes_res.stdout and "origin" in remotes_res.stdout.splitlines())

    if has_remote:
        try:
            run_command(["gh", "auth", "setup-git"])
        except Exception:
            pass

        print(f"Pulling latest changes from origin/{base_branch}...")
        res_pull = run_command(["git", "pull", "origin", base_branch])
        if res_pull.returncode != 0:
            print(f"Warning: Failed to pull origin {base_branch}:\n{res_pull.stderr}", file=sys.stderr)
    else:
        print("Notice: No 'origin' remote found. Skipping pull.")

    # 5. Delete the target local branch
    print(f"Deleting local feature branch '{target_branch}'...")
    res_del = run_command(["git", "branch", "-d", target_branch])
    if res_del.returncode != 0:
        if is_merged:
            print("Safe delete (-d) failed (e.g. squash/rebase merged). PR is confirmed merged, attempting force delete (-D)...")
            res_fdel = run_command(["git", "branch", "-D", target_branch])
            if res_fdel.returncode != 0:
                print(f"Error: Failed to force delete branch '{target_branch}':\n{res_fdel.stderr}", file=sys.stderr)
                sys.exit(res_fdel.returncode)
        else:
            print(f"Error: Cannot delete branch '{target_branch}': safe delete (-d) failed and PR merge status was not confirmed. Force delete (-D) is blocked to prevent data loss.", file=sys.stderr)
            sys.exit(1)

    # 6. Delete remote branch via GitHub API if requested
    if args.delete_remote and has_remote:
        if not is_merged:
            print(f"Error: Cannot delete remote branch '{target_branch}' because PR merge status was not confirmed.", file=sys.stderr)
            sys.exit(1)

        print("Deleting remote branch via GitHub API...")
        res_repo = run_command(["gh", "repo", "view", "--json", "fullName", "-q", ".fullName"])
        if res_repo.returncode == 0 and res_repo.stdout.strip():
            repo = res_repo.stdout.strip()
            res_api = run_command(["gh", "api", "-X", "DELETE", f"repos/{repo}/git/refs/heads/{target_branch}"])
            if res_api.returncode != 0:
                print(f"Warning: Remote branch '{target_branch}' on '{repo}' may not exist or already deleted.")
            else:
                print(f"Remote branch '{target_branch}' deleted successfully via GitHub API.")
        else:
            print("Notice: GitHub CLI repo info not available. Attempting git push origin --delete...")
            res_push_del = run_command(["git", "push", "origin", "--delete", target_branch])
            if res_push_del.returncode != 0:
                print(f"Warning: Failed to delete remote branch '{target_branch}': {res_push_del.stderr}", file=sys.stderr)

    # 7. Post-verification of base branch
    print(f"=== Verifying Latest Commit on Local {base_branch} Branch ===")
    res_log = run_command(["git", "log", "-n", "1", base_branch], capture_output=False)
    if res_log.returncode != 0:
        print(f"Error: Failed to retrieve git log for {base_branch}.", file=sys.stderr)
        sys.exit(res_log.returncode)

    print(f"Successfully cleaned up branch '{target_branch}' and updated {base_branch}.")

if __name__ == "__main__":
    main()
