#!/usr/bin/env python3
import sys
import os
import re
import datetime
import argparse
import subprocess

def run_command(cmd, check=True, cwd=None, capture_output=True, text=True):
    return subprocess.run(cmd, check=check, cwd=cwd, capture_output=capture_output, text=text, encoding='utf-8', errors='replace')

def main():
    parser = argparse.ArgumentParser(description="Start local task branch and initialize task document.")
    parser.add_argument("-t", "--task-name", required=True, help="Task identifier/filename (e.g. 001-user-auth)")
    parser.add_argument("--title", default="", help="Human-readable title of the task")
    parser.add_argument("-b", "--branch-name", default="", help="Feature/task branch name (default: task/<task-name>)")
    parser.add_argument("--base-branch", default="main", help="Base branch name to branch off from (default: main)")
    parser.add_argument("--auto-stash", action="store_true", help="Auto stash uncommitted tracked changes before switching branch")
    parser.add_argument("--harness", default=os.environ.get("AGENT_HARNESS", "Antigravity"), help="AI Agent harness/runtime name (default: Antigravity)")

    args = parser.parse_args()

    # Determine project root directory (.agents/skills/local-workflow/scripts -> 4 levels up)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, "..", "..", "..", ".."))
    os.chdir(root_dir)

    base_branch = args.base_branch
    task_name = args.task_name.strip()
    if not task_name.endswith(".md"):
        task_file_name = f"{task_name}.md"
    else:
        task_file_name = task_name
        task_name = task_name[:-3]

    branch_name = args.branch_name if args.branch_name else f"task/{task_name}"
    task_title = args.title if args.title else task_name

    print(f"=== Starting Local Task Branch Workflow (Task: {task_name}, Base: {base_branch}) ===")

    # 1. Check for uncommitted tracked changes
    res = run_command(["git", "status", "--porcelain", "-uno"], check=False)
    status_output = res.stdout.strip() if res.stdout else ""

    if status_output:
        if args.auto_stash:
            print("Uncommitted changes detected. AutoStash requested: running git stash...")
            run_command(["git", "stash", "push", "-m", f"AutoStash before starting {task_name}"])
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
        print(f"Pulling latest changes from origin/{base_branch}...")
        res_pull = run_command(["git", "pull", "origin", base_branch], check=False)
        if res_pull.returncode != 0:
            print(f"Notice: Failed to pull origin {base_branch}. Continuing with local {base_branch}...", file=sys.stderr)

    # 4. Initialize docs/tasks directory and README.md if not existing
    tasks_dir = os.path.join(root_dir, "docs", "tasks")
    completed_dir = os.path.join(tasks_dir, "completed")
    os.makedirs(completed_dir, exist_ok=True)

    readme_path = os.path.join(tasks_dir, "README.md")
    if not os.path.exists(readme_path):
        initial_readme = (
            "# タスク管理台帳 (Local Tasks Index)\n\n"
            "本ディレクトリは、GitHub Issue を使用しないローカル開発におけるタスク管理正本（SSOT）である。\n\n"
            "## 進行中 / 未着手タスク (Active Tasks)\n\n"
            "## 完了タスク (Completed Tasks)\n\n"
        )
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(initial_readme)
        print("Initialized docs/tasks/README.md")

    # 5. Create or verify task markdown file
    task_file_path = os.path.join(tasks_dir, task_file_name)
    template_path = os.path.join(script_dir, "..", "resources", "TASK_TEMPLATE.md")

    today_str = datetime.date.today().strftime("%Y-%m-%d")

    if not os.path.exists(task_file_path):
        harness_name = args.harness.strip() if args.harness and args.harness.strip() else "Antigravity"
        if os.path.exists(template_path):
            with open(template_path, "r", encoding="utf-8") as f:
                template_content = f.read()
        else:
            template_content = (
                "---\n"
                "task_id: \"{{TASK_ID}}\"\n"
                "title: \"{{TASK_TITLE}}\"\n"
                "status: \"in-progress\"\n"
                "created_at: \"{{CREATED_DATE}}\"\n"
                "branch: \"{{BRANCH_NAME}}\"\n"
                "labels:\n"
                "  - \"ai-generated\"\n"
                "---\n"
                "# タスク仕様書: {{TASK_TITLE}}\n\n"
                "- **ステータス**: 🟡 進行中\n"
                "- **作成日**: {{CREATED_DATE}}\n"
                "- **作業ブランチ**: {{BRANCH_NAME}}\n\n"
                "## 1. Goal (目的・完了条件)\n\n"
                "## 2. Context (背景・仕様参照)\n\n"
                "## 3. Technical Details (技術要件・制約)\n\n"
                "## 4. Verification (検証手順)\n\n"
                "---\n"
                "<sub>Generated with AI Agent ({{HARNESS_NAME}})</sub>\n"
            )

        replacements = {
            "{{TASK_ID}}": task_name,
            "{{TASK_TITLE}}": task_title,
            "{{CREATED_DATE}}": today_str,
            "{{BRANCH_NAME}}": branch_name,
            "{{HARNESS_NAME}}": harness_name,
        }
        task_content = template_content
        for key, val in replacements.items():
            task_content = task_content.replace(key, val)

        with open(task_file_path, "w", encoding="utf-8") as f:
            f.write(task_content)
        print(f"Created task file at: docs/tasks/{task_file_name}")

        # Update README.md with link to active task
        with open(readme_path, "r", encoding="utf-8") as f:
            readme_content = f.read()

        active_entry = f"- [🟡 進行中: {task_title}]({task_file_name})\n"
        if active_entry not in readme_content:
            if "## 進行中 / 未着手タスク (Active Tasks)" in readme_content:
                readme_content = readme_content.replace(
                    "## 進行中 / 未着手タスク (Active Tasks)\n",
                    f"## 進行中 / 未着手タスク (Active Tasks)\n{active_entry}"
                )
            else:
                readme_content = f"## 進行中 / 未着手タスク (Active Tasks)\n{active_entry}\n" + readme_content

            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(readme_content)
            print("Updated docs/tasks/README.md with new active task.")
    else:
        print(f"Task file already exists: docs/tasks/{task_file_name}")

    # 6. Create and checkout target task branch
    print(f"Creating/switching to task branch '{branch_name}'...")
    res = run_command(["git", "checkout", "-b", branch_name], check=False)
    if res.returncode != 0:
        res = run_command(["git", "checkout", branch_name], check=False)
        if res.returncode != 0:
            print(f"Error: Failed to checkout branch {branch_name}:\n{res.stderr}", file=sys.stderr)
            sys.exit(res.returncode)

    res = run_command(["git", "branch", "--show-current"])
    current = res.stdout.strip()
    if current != branch_name:
        print(f"Error: Branch checkout verification failed! Active branch is '{current}', expected '{branch_name}'.", file=sys.stderr)
        sys.exit(1)

    print(f"Successfully started task '{task_name}' on branch '{branch_name}'.")

if __name__ == "__main__":
    main()
