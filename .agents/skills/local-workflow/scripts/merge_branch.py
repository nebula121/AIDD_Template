#!/usr/bin/env python3
import sys
import os
import argparse
import subprocess

def run_command(cmd, check=False, cwd=None, capture_output=True, text=True):
    return subprocess.run(cmd, check=check, cwd=cwd, capture_output=capture_output, text=text, encoding='utf-8', errors='replace')

def main():
    parser = argparse.ArgumentParser(description="Merge local task branch into base branch and cleanup.")
    parser.add_argument("-b", "--target-branch", required=True, help="Task/feature branch to merge and delete")
    parser.add_argument("--base-branch", default="main", help="Base branch to merge into (default: main)")
    parser.add_argument("--no-ff", action="store_true", help="Create a merge commit even if fast-forward is possible")
    parser.add_argument("--auto-stash", action="store_true", help="Auto stash uncommitted tracked changes before merging")

    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, "..", "..", "..", ".."))
    os.chdir(root_dir)

    base_branch = args.base_branch
    target_branch = args.target_branch

    print(f"=== Starting Local Branch Merge Workflow (Target: {target_branch} -> Base: {base_branch}) ===")

    if target_branch == base_branch:
        print(f"Error: Cannot merge base branch '{base_branch}' into itself.", file=sys.stderr)
        sys.exit(1)

    # 1. Check for uncommitted tracked changes
    res_status = run_command(["git", "status", "--porcelain", "-uno"])
    if res_status.returncode != 0:
        print("Error: Failed to execute 'git status'.", file=sys.stderr)
        sys.exit(1)

    status_output = res_status.stdout.strip() if res_status.stdout else ""
    if status_output:
        if args.auto_stash:
            print("Uncommitted tracked changes detected. AutoStash requested: running git stash...")
            res_stash = run_command(["git", "stash", "push", "-m", f"AutoStash before merging {target_branch}"])
            if res_stash.returncode != 0:
                print("Error: git stash failed.", file=sys.stderr)
                sys.exit(res_stash.returncode)
        else:
            print("Error: Working directory has uncommitted tracked changes. Pass --auto-stash or commit/stash them before merging.", file=sys.stderr)
            sys.exit(1)

    # 2. Switch to base branch
    print(f"Switching to base branch '{base_branch}'...")
    res_co = run_command(["git", "checkout", base_branch])
    if res_co.returncode != 0:
        print(f"Error: Failed to checkout {base_branch} branch:\n{res_co.stderr}", file=sys.stderr)
        sys.exit(res_co.returncode)

    # 3. Merge target branch
    merge_cmd = ["git", "merge", target_branch]
    if args.no_ff:
        merge_cmd.append("--no-ff")

    print(f"Merging '{target_branch}' into '{base_branch}'...")
    res_merge = run_command(merge_cmd)
    if res_merge.returncode != 0:
        print(f"CRITICAL: Git merge failed with conflict or error:\n{res_merge.stderr}\nMerge abort recommended if unresolved.", file=sys.stderr)
        sys.exit(res_merge.returncode)

    if res_merge.stdout:
        print(res_merge.stdout.strip())

    # 4. Delete the merged target branch
    print(f"Deleting local task branch '{target_branch}'...")
    res_del = run_command(["git", "branch", "-d", target_branch])
    if res_del.returncode != 0:
        print("Safe delete (-d) failed. Attempting force delete (-D)...")
        res_fdel = run_command(["git", "branch", "-D", target_branch])
        if res_fdel.returncode != 0:
            print(f"Warning: Failed to delete branch '{target_branch}':\n{res_fdel.stderr}", file=sys.stderr)
        else:
            print(f"Successfully force deleted branch '{target_branch}'.")
    else:
        print(f"Successfully deleted branch '{target_branch}'.")

    # 5. Clean temporary workflow artifacts
    temp_file = os.path.join(root_dir, "diff_summary_for_agent.txt")
    if os.path.exists(temp_file):
        try:
            os.remove(temp_file)
            print("Cleaned temporary diff summary artifact.")
        except Exception:
            pass

    # 6. Post-verification of base branch
    print(f"=== Verifying Latest Commit on Local {base_branch} Branch ===")
    res_log = run_command(["git", "log", "-n", "1", base_branch], capture_output=False)
    if res_log.returncode != 0:
        print(f"Error: Failed to retrieve git log for {base_branch}.", file=sys.stderr)
        sys.exit(res_log.returncode)

    print(f"Successfully merged '{target_branch}' into '{base_branch}' and cleaned up.")

if __name__ == "__main__":
    main()
