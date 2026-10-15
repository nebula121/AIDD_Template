#!/usr/bin/env python3
import sys
import os
import argparse
import subprocess

def run_command(cmd, check=False, cwd=None, capture_output=True, text=True):
    return subprocess.run(cmd, check=check, cwd=cwd, capture_output=capture_output, text=text, encoding='utf-8', errors='replace')

def main():
    parser = argparse.ArgumentParser(description="Generate Walkthrough diff summary for local agents.")
    parser.add_argument("--base-branch", default="main", help="Base branch to compare against (default: main)")
    parser.add_argument("--max-lines", type=int, default=200, help="Max lines for diff")

    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, "..", "..", "..", ".."))
    os.chdir(root_dir)

    base_branch = args.base_branch
    print(f"Generating diff summary for Walkthrough (Base: {base_branch})...")
    res_branch = run_command(["git", "branch", "--show-current"])
    current_branch = res_branch.stdout.strip() if res_branch.stdout else ""

    # 1. Uncommitted changes summary
    res_uncommitted_name = run_command(["git", "diff", "HEAD", "--name-status"])
    uncommitted_name_status = res_uncommitted_name.stdout.strip() if res_uncommitted_name.stdout else ""
    if not uncommitted_name_status:
        res_uncommitted_name = run_command(["git", "diff", "--cached", "HEAD", "--name-status"])
        uncommitted_name_status = res_uncommitted_name.stdout.strip() if res_uncommitted_name.stdout else ""

    res_uncommitted_stat = run_command(["git", "diff", "HEAD", "--stat"])
    uncommitted_stat = res_uncommitted_stat.stdout.strip() if res_uncommitted_stat.stdout else ""
    if not uncommitted_stat:
        res_uncommitted_stat = run_command(["git", "diff", "--cached", "HEAD", "--stat"])
        uncommitted_stat = res_uncommitted_stat.stdout.strip() if res_uncommitted_stat.stdout else ""

    # 2. Branch commits relative to base_branch
    branch_name_status = ""
    branch_stat = ""
    if current_branch and current_branch != base_branch:
        res_b_name = run_command(["git", "diff", f"{base_branch}...HEAD", "--name-status"])
        branch_name_status = res_b_name.stdout.strip() if res_b_name.stdout else ""
        res_b_stat = run_command(["git", "diff", f"{base_branch}...HEAD", "--stat"])
        branch_stat = res_b_stat.stdout.strip() if res_b_stat.stdout else ""

    if not uncommitted_name_status and not branch_name_status:
        print("No changes found.")
        sys.exit(0)

    output_file = os.path.join(root_dir, "diff_summary_for_agent.txt")

    lines = [
        "=== Local Walkthrough Diff Summary ===",
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

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("Diff summary generated at: diff_summary_for_agent.txt")
    print("Agents can read this file to present concise Walkthrough to the human developer.")

if __name__ == "__main__":
    main()
