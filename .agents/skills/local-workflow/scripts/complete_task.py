#!/usr/bin/env python3
import sys
import os
import re
import datetime
import argparse
import shutil
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

def find_repo_root() -> Path:
    """Find repository root by looking for .git or AGENTS.md in cwd or parents."""
    cwd = Path.cwd().resolve()
    for p in [cwd] + list(cwd.parents):
        if (p / ".git").exists() or (p / "AGENTS.md").exists():
            return p
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / ".git").exists() or (parent / "AGENTS.md").exists():
            return parent
    return cwd

def get_current_branch() -> str:
    res = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return res.stdout.strip() if res.returncode == 0 else ""

def extract_title_from_md(file_path: Path, fallback: str) -> str:
    if not file_path.exists():
        return fallback
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if match:
        raw_title = match.group(1).strip()
        # Strip prefixes like 'タスク仕様書: ' or 'PR: '
        raw_title = re.sub(r"^(タスク仕様書|PR):\s*", "", raw_title)
        return raw_title
    return fallback

def main():
    parser = argparse.ArgumentParser(description="Complete local tasks and generate/close local PR document.")
    parser.add_argument("-t", "--tasks", "--task-file", dest="tasks", nargs="+", required=True,
                        help="One or more task markdown file names in docs/tasks (e.g. 001-user-auth.md)")
    parser.add_argument("--pr-file", "--pr-name", dest="pr_name", default="",
                        help="PR markdown file name (e.g. pr-auth-system.md). Default: <task>-pr.md for single task.")
    parser.add_argument("--pr-title", default="", help="Title for the PR document")
    parser.add_argument("--target-branch", default="main", help="Target merge branch (default: main)")
    parser.add_argument("--walkthrough-file", default="", help="Path to walkthrough.md artifact to import content from")
    parser.add_argument("--harness", default=os.environ.get("AGENT_HARNESS", "Antigravity"),
                        help="AI harness name (default: Antigravity)")

    args = parser.parse_args()

    root_dir = find_repo_root()
    script_dir = Path(__file__).resolve().parent

    tasks_dir = root_dir / "docs" / "tasks"
    completed_dir = tasks_dir / "completed"
    readme_path = tasks_dir / "README.md"
    template_path = script_dir.parent / "resources" / "PR_TEMPLATE.md"

    completed_dir.mkdir(parents=True, exist_ok=True)
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    current_branch = get_current_branch()

    task_files = []
    for t in args.tasks:
        name = t.strip()
        if not name.endswith(".md"):
            name = f"{name}.md"
        task_files.append(name)

    # Determine PR file name
    pr_file_name = args.pr_name.strip()
    if not pr_file_name:
        if len(task_files) == 1:
            base = task_files[0][:-3]
            pr_file_name = f"{base}-pr.md"
        else:
            branch_clean = current_branch.replace("task/", "").replace("feature/", "").strip()
            if branch_clean:
                pr_file_name = f"pr-{branch_clean}.md"
            else:
                pr_file_name = f"pr-{task_files[0][:-3]}.md"
    if not pr_file_name.endswith(".md"):
        pr_file_name = f"{pr_file_name}.md"

    pr_id = pr_file_name[:-3]

    print(f"=== Completing Local Task(s) for PR '{pr_file_name}' ===")
    print(f"Target Tasks: {', '.join(task_files)}")

    # 1. Verify existence of task files
    valid_tasks = []
    task_titles = {}
    for tf in task_files:
        src = tasks_dir / tf
        already_comp = completed_dir / tf
        if src.exists():
            valid_tasks.append((tf, src, False))
            task_titles[tf] = extract_title_from_md(src, tf[:-3])
        elif already_comp.exists():
            valid_tasks.append((tf, already_comp, True))
            task_titles[tf] = extract_title_from_md(already_comp, tf[:-3])
        else:
            print(f"Error: Task file not found: docs/tasks/{tf}", file=sys.stderr)
            sys.exit(1)

    # Determine PR Title
    pr_title = args.pr_title.strip()
    if not pr_title:
        if len(task_files) == 1:
            pr_title = f"{task_titles[task_files[0]]}"
        else:
            pr_title = f"Resolve {len(task_files)} tasks: {task_titles[task_files[0]]} and others"

    # 2. Process or Create PR document
    pr_path_active = tasks_dir / pr_file_name
    pr_path_completed = completed_dir / pr_file_name

    closes_list_yaml = "\n".join([f'  - "{tf}"' for tf in task_files])
    resolved_tasks_md = "\n".join([f'- Closes [{tf}]({tf}) - {task_titles[tf]}' for tf in task_files])

    walkthrough_summary = ""
    walkthrough_changes = ""
    walkthrough_verification = ""
    walkthrough_followups = ""

    if args.walkthrough_file and Path(args.walkthrough_file).exists():
        try:
            with open(args.walkthrough_file, "r", encoding="utf-8") as wf:
                wt_content = wf.read()
            # Extract sections if available
            s_match = re.search(r"##\s+(?:1\.\s*)?(?:Summary|概要)(.*?)(?=##|\Z)", wt_content, re.DOTALL | re.IGNORECASE)
            if s_match:
                walkthrough_summary = s_match.group(1).strip()
            c_match = re.search(r"##\s+(?:2\.\s*)?(?:Changes|変更内容)(.*?)(?=##|\Z)", wt_content, re.DOTALL | re.IGNORECASE)
            if c_match:
                walkthrough_changes = c_match.group(1).strip()
            v_match = re.search(r"##\s+(?:3\.\s*)?(?:Verification|検証結果|テスト)(.*?)(?=##|\Z)", wt_content, re.DOTALL | re.IGNORECASE)
            if v_match:
                walkthrough_verification = v_match.group(1).strip()
            f_match = re.search(r"##\s+(?:4\.\s*)?(?:Follow-ups|派生課題)(.*?)(?=##|\Z)", wt_content, re.DOTALL | re.IGNORECASE)
            if f_match:
                walkthrough_followups = f_match.group(1).strip()
        except Exception as e:
            print(f"Notice: Failed to parse walkthrough artifact: {e}")

    if pr_path_active.exists():
        # Update existing PR file and move to completed
        with open(pr_path_active, "r", encoding="utf-8") as f:
            pr_content = f.read()
        pr_content = re.sub(r'status:\s*["\']?[a-zA-Z0-9_\-]+["\']?', 'status: "merged"', pr_content)
        pr_content = re.sub(r"- \*\*ステータス\*\*: .*", "- **ステータス**: 🟣 Merged", pr_content)
        if "merged_date:" not in pr_content:
            pr_content = re.sub(r'(status:\s*"merged")', f'\\1\nmerged_date: "{today_str}"', pr_content)
        if "- **マージ日**:" not in pr_content:
            pr_content = re.sub(r'(- \*\*ステータス\*\*: 🟣 Merged)', f'\\1\n- **マージ日**: {today_str}', pr_content)
        
        with open(pr_path_active, "w", encoding="utf-8") as f:
            f.write(pr_content)
        shutil.move(str(pr_path_active), str(pr_path_completed))
        print(f"Moved active PR file to: docs/tasks/completed/{pr_file_name}")
    elif pr_path_completed.exists():
        print(f"PR document already in completed: docs/tasks/completed/{pr_file_name}")
    else:
        # Create from template directly in completed
        if template_path.exists():
            with open(template_path, "r", encoding="utf-8") as tf:
                tpl = tf.read()
            replacements = {
                "{{PR_ID}}": pr_id,
                "{{PR_TITLE}}": pr_title,
                "{{CLOSES_LIST}}": closes_list_yaml,
                "{{TARGET_BRANCH}}": args.target_branch,
                "{{BRANCH_NAME}}": current_branch if current_branch else "task-branch",
                "{{STATUS}}": "merged",
                "{{STATUS_DISPLAY}}": "🟣 Merged",
                "{{CREATED_DATE}}": today_str,
                "{{RESOLVED_TASKS}}": resolved_tasks_md,
                "{{HARNESS_NAME}}": args.harness,
            }
            pr_body = tpl
            for k, v in replacements.items():
                pr_body = pr_body.replace(k, v)

            if walkthrough_summary:
                pr_body = re.sub(r"## 1\. Summary \(概要\)\s*<!--.*?-->", f"## 1. Summary (概要)\n{walkthrough_summary}", pr_body, flags=re.DOTALL)
            if walkthrough_changes:
                pr_body = re.sub(r"## 2\. Changes \(変更内容の詳細\)\s*<!--.*?-->", f"## 2. Changes (変更内容の詳細)\n{walkthrough_changes}", pr_body, flags=re.DOTALL)
            if walkthrough_verification:
                pr_body = re.sub(r"## 3\. Verification \(検証結果・テストエビデンス\)\s*<!--.*?-->", f"## 3. Verification (検証結果・テストエビデンス)\n{walkthrough_verification}", pr_body, flags=re.DOTALL)
            if walkthrough_followups:
                pr_body = re.sub(r"## 4\. Follow-ups \(派生課題・今後のタスク\)\s*<!--.*?-->", f"## 4. Follow-ups (派生課題・今後のタスク)\n{walkthrough_followups}", pr_body, flags=re.DOTALL)

            with open(pr_path_completed, "w", encoding="utf-8") as pf:
                pf.write(pr_body)
            print(f"Created completed PR document: docs/tasks/completed/{pr_file_name}")

    # 3. Process each task document
    for tf, path, is_already_completed in valid_tasks:
        file_to_read = path
        with open(file_to_read, "r", encoding="utf-8") as f:
            content = f.read()

        # Update Frontmatter status to completed
        content = re.sub(r'status:\s*["\']?in-progress["\']?', 'status: "completed"', content)
        if "completed_at:" not in content:
            content = re.sub(r'(status:\s*"completed")', f'\\1\ncompleted_at: "{today_str}"', content)

        # Update body status
        content = re.sub(r"- \*\*ステータス\*\*: .*", "- **ステータス**: 🟢 完了", content)
        if "- **完了日**:" in content:
            content = re.sub(r"- \*\*完了日\*\*: .*", f"- **完了日**: {today_str}", content)
        else:
            content = re.sub(r"(- \*\*ステータス\*\*: 🟢 完了)", f"\\1\n- **完了日**: {today_str}", content)

        # Add Resolved PR link if not present
        pr_link_line = f"- **解決PR**: [{pr_file_name}]({pr_file_name})"
        if "- **解決PR**:" not in content:
            content = re.sub(r"(- \*\*完了日\*\*: [0-9\-]+)", f"\\1\n{pr_link_line}", content)

        if not is_already_completed:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            target = completed_dir / tf
            shutil.move(str(path), str(target))
            print(f"Moved task document to: docs/tasks/completed/{tf}")
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Updated completed task document: docs/tasks/completed/{tf}")

    # 4. Update docs/tasks/README.md
    if readme_path.exists():
        with open(readme_path, "r", encoding="utf-8") as f:
            readme_content = f.read()

        for tf in task_files:
            escaped_name = re.escape(tf)
            line_pattern = rf"^[ \t]*- \[.*\]\({escaped_name}\)[ \t]*\r?\n?"
            matched = re.findall(line_pattern, readme_content, flags=re.MULTILINE)

            if matched:
                readme_content = re.sub(line_pattern, "", readme_content, flags=re.MULTILINE)
                raw_line = matched[0].strip()
                comp_line = re.sub(r'\]\(' + escaped_name + r'\)', f"](completed/{tf})", raw_line)
                comp_line = re.sub(r'🟡 進行中:', '🟢 完了:', comp_line)
                comp_line = f"{comp_line} ([PR](completed/{pr_file_name}))\n"

                completed_header = "## 完了タスク (Completed Tasks)"
                if completed_header in readme_content:
                    readme_content = re.sub(
                        r"(## 完了タスク \(Completed Tasks\)\s*)",
                        rf"\1{comp_line}",
                        readme_content,
                        count=1
                    )
                else:
                    readme_content = readme_content.rstrip() + f"\n\n{completed_header}\n{comp_line}"

        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)
        print("Updated docs/tasks/README.md with completed task(s) and PR link.")

    print(f"=== Successfully completed {len(task_files)} task(s) resolved by PR '{pr_file_name}' ===")

if __name__ == "__main__":
    main()
