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

def run_command(cmd, check=False, cwd=None, capture_output=True, text=True):
    return subprocess.run(cmd, check=check, cwd=cwd, capture_output=capture_output, text=text, encoding='utf-8', errors='replace')

def main():
    parser = argparse.ArgumentParser(description="Generate Walkthrough diff summary for agents.")
    parser.add_argument("--base-branch", default="main", help="Base branch to compare against (default: main)")

    args = parser.parse_args()

    root_dir = find_repo_root()
    os.chdir(root_dir)

    base_branch = args.base_branch
    print(f"Generating diff summary for Walkthrough (Base: {base_branch})...")
    res_branch = run_command(["git", "branch", "--show-current"])
    current_branch = res_branch.stdout.strip() if res_branch.stdout else ""

    # 1. Uncommitted changes summary
    res_uncommitted_name = run_command(["git", "diff", "HEAD", "--name-status"])
    uncommitted_name_status = res_uncommitted_name.stdout.strip() if res_uncommitted_name.stdout else ""

    res_uncommitted_stat = run_command(["git", "diff", "HEAD", "--stat"])
    uncommitted_stat = res_uncommitted_stat.stdout.strip() if res_uncommitted_stat.stdout else ""

    # 2. Untracked files summary (BUG-05)
    res_untracked = run_command(["git", "ls-files", "--others", "--exclude-standard"])
    untracked_files = res_untracked.stdout.strip() if res_untracked.stdout else ""

    # 3. Branch commits relative to base_branch
    branch_name_status = ""
    branch_stat = ""
    if current_branch and current_branch != base_branch:
        res_b_name = run_command(["git", "diff", f"{base_branch}...HEAD", "--name-status"])
        branch_name_status = res_b_name.stdout.strip() if res_b_name.stdout else ""
        res_b_stat = run_command(["git", "diff", f"{base_branch}...HEAD", "--stat"])
        branch_stat = res_b_stat.stdout.strip() if res_b_stat.stdout else ""

    if not uncommitted_name_status and not branch_name_status and not untracked_files:
        print("No changes found.")
        sys.exit(0)

    output_file = root_dir / "diff_summary_for_agent.txt"

    lines = [
        "=== Walkthrough Diff Summary ===",
        f"Branch: {current_branch}",
        ""
    ]

    if branch_name_status:
        lines.extend([
            f"--- Branch Commits vs {base_branch} (Name Status) ---",
            branch_name_status,
            "",
            f"--- Branch Commits vs {base_branch} (Diff Stat) ---",
            branch_stat,
            ""
        ])

    if uncommitted_name_status:
        lines.extend([
            "--- Uncommitted Changes (Name Status) ---",
            uncommitted_name_status,
            "",
            "--- Uncommitted Changes (Diff Stat) ---",
            uncommitted_stat,
            ""
        ])

    if untracked_files:
        lines.extend([
            "--- Untracked Files ---",
            untracked_files,
            ""
        ])

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("Diff summary generated at: diff_summary_for_agent.txt")
    print("Agents can read this file to generate Walkthrough.md with minimal token usage.")

if __name__ == "__main__":
    main()
