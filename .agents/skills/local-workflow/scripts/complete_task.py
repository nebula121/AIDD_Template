#!/usr/bin/env python3
import sys
import os
import re
import datetime
import argparse
import shutil

def main():
    parser = argparse.ArgumentParser(description="Complete local task document processing.")
    parser.add_argument("-t", "--task-file", required=True, help="Task markdown file name in docs/tasks (e.g. 001-user-auth.md)")

    args = parser.parse_args()

    task_file_name = args.task_file.strip()
    if not task_file_name.endswith(".md"):
        task_file_name = f"{task_file_name}.md"

    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, "..", "..", "..", ".."))

    tasks_dir = os.path.join(root_dir, "docs", "tasks")
    completed_dir = os.path.join(tasks_dir, "completed")
    readme_path = os.path.join(tasks_dir, "README.md")
    task_path = os.path.join(tasks_dir, task_file_name)

    if not os.path.exists(task_path):
        # Check if already completed
        already_completed = os.path.join(completed_dir, task_file_name)
        if os.path.exists(already_completed):
            print(f"Notice: Task file is already in completed directory: {already_completed}")
            sys.exit(0)
        print(f"Error: Task file not found: {task_path}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(completed_dir, exist_ok=True)

    today_str = datetime.date.today().strftime("%Y-%m-%d")

    # 1. Update task status and completion date inside task file
    with open(task_path, "r", encoding="utf-8") as f:
        content = f.read()

    content = re.sub(r"- \*\*ステータス\*\*: .*", "- **ステータス**: 🟢 完了", content)
    if "- **完了日**:" in content:
        content = re.sub(r"- \*\*完了日\*\*: .*", f"- **完了日**: {today_str}", content)
    else:
        content = re.sub(r"(- \*\*ステータス\*\*: 🟢 完了)", f"\\1\n- **完了日**: {today_str}", content)

    with open(task_path, "w", encoding="utf-8") as f:
        f.write(content)

    # 2. Move to completed directory
    target_path = os.path.join(completed_dir, task_file_name)
    shutil.move(task_path, target_path)
    print(f"Moved task document to: docs/tasks/completed/{task_file_name}")

    # 3. Update docs/tasks/README.md if exists
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            readme_content = f.read()

        # Update link path from task_file_name to completed/task_file_name
        escaped_name = re.escape(task_file_name)
        pattern = r'\]\(' + escaped_name + r'\)'
        replacement = f"](completed/{task_file_name})"
        readme_content = re.sub(pattern, replacement, readme_content)

        # Update status icon in link label
        readme_content = re.sub(r'🟡 進行中: ([^\]]+)\]\(completed/' + escaped_name + r'\)', r'🟢 完了: \1](completed/' + task_file_name + r')', readme_content)

        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)
        print("Updated docs/tasks/README.md link and status to completed.")

    print(f"Successfully completed task '{task_file_name}'.")

if __name__ == "__main__":
    main()
