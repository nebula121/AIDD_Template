#!/usr/bin/env python3
import sys
import os
import re
import argparse
import subprocess

def run_command(cmd, check=True, cwd=None, capture_output=True, text=True):
    return subprocess.run(cmd, check=check, cwd=cwd, capture_output=capture_output, text=text, encoding='utf-8', errors='replace')

def main():
    parser = argparse.ArgumentParser(description="Create WIP commit with secret scanning for local workflow.")
    parser.add_argument("-m", "--message", required=True, help="Commit message description")
    parser.add_argument("-t", "--task", required=False, default=None, help="Target task name or ID (optional)")

    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, "..", "..", "..", ".."))
    os.chdir(root_dir)

    # 1. Stage changes first
    print("Staging changes...")
    run_command(["git", "add", "-A"])
    print("=== Staged Files ===")
    res = run_command(["git", "diff", "--cached", "--name-only"])
    staged_files = res.stdout.strip() if res.stdout else ""
    if not staged_files:
        print("Notice: No changes staged to commit. Working directory clean.")
        sys.exit(0)
    print(staged_files)

    print("=== Running Agent Pre-Commit Secret Scan ===")

    # 2. Pre-commit secret check on staged changes
    res_diff = run_command(["git", "diff", "--cached"])
    staged_content = res_diff.stdout if res_diff.stdout else ""

    patterns = [
        r"BEGIN RSA PRIVATE KEY",
        r"BEGIN PRIVATE KEY",
        r"BEGIN OPENSSH PRIVATE KEY",
        r"ghs_[a-zA-Z0-9]{30,}",
        r"ghp_[a-zA-Z0-9]{30,}",
        r"github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}",
        r"AKIA[0-9A-Z]{16}",
        r"sk_live_[a-zA-Z0-9]+",
        r"(api[_-]?key|secret|password|token)\s*[:=]\s*['\"][a-zA-Z0-9_\-]{8,}['\"]",
        r"password\s*=\s*['\"]",
        r"api[_-]?key\s*=\s*['\"]",
    ]

    secret_found = False
    for pat in patterns:
        if re.search(pat, staged_content, re.IGNORECASE):
            print(f"CRITICAL: Secret pattern '{pat}' detected in staged diff! Commit blocked.", file=sys.stderr)
            secret_found = True

    if secret_found:
        print("Unstaging changes due to secret detection...", file=sys.stderr)
        run_command(["git", "reset"], check=False)
        sys.exit(1)

    # 3. Format commit message
    if args.task:
        commit_msg = f"wip: {args.message} (Task: {args.task})"
    else:
        commit_msg = f"wip: {args.message}"
    print(f"Creating WIP commit: '{commit_msg}'")

    res_commit = run_command(["git", "commit", "-m", commit_msg], check=False)
    if res_commit.returncode != 0:
        print(f"Error: Git commit failed:\n{res_commit.stderr}", file=sys.stderr)
        sys.exit(res_commit.returncode)

    print("Successfully created WIP commit.")

if __name__ == "__main__":
    main()
