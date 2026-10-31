#!/usr/bin/env python3
"""Integration tests for workflow and local-workflow scripts in isolated Git repositories."""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def run_cmd(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def init_isolated_git_repo(tmp: Path) -> None:
    """Initialize an isolated git repo with initial commit on 'main' and workflow scripts."""
    shutil.copytree(REPO_ROOT / ".agents", tmp / ".agents")
    (tmp / "AGENTS.md").write_text("# AGENTS\n", encoding="utf-8")
    (tmp / "README.md").write_text("# Test Repo\n", encoding="utf-8")

    run_cmd(["git", "init", "-b", "main"], tmp)
    run_cmd(["git", "config", "user.email", "test@example.com"], tmp)
    run_cmd(["git", "config", "user.name", "Test User"], tmp)
    run_cmd(["git", "add", "-A"], tmp)
    run_cmd(["git", "commit", "-m", "initial commit"], tmp)


class TestWorkflowScripts(unittest.TestCase):
    """Test commit_wip.py and local-workflow lifecycle in isolated temporary Git repos."""

    def test_commit_wip_secret_detection_and_deletion_safety(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            init_isolated_git_repo(tmp)
            commit_script = tmp / ".agents/skills/workflow/scripts/commit_wip.py"

            # 1. Normal file commit with -i and -p succeeds
            normal_file = tmp / "app.py"
            normal_file.write_text("print('hello world')\n", encoding="utf-8")
            res_ok = run_cmd(
                [sys.executable, str(commit_script), "-m", "add app", "-i", "42", "-p", "app.py"],
                tmp,
            )
            self.assertEqual(res_ok.returncode, 0, res_ok.stderr)
            log_res = run_cmd(["git", "log", "-n", "1", "--oneline"], tmp)
            self.assertIn("wip: add app (Ref: #42)", log_res.stdout)

            # 2. Staged file containing a secret pattern is blocked and unstaged
            dummy_secret = "ghp_" + ("A" * 36)
            secret_file = tmp / "config.py"
            secret_file.write_text(f"TOKEN = '{dummy_secret}'\n", encoding="utf-8")
            res_blocked = run_cmd(
                [sys.executable, str(commit_script), "-m", "leak secret"],
                tmp,
            )
            self.assertNotEqual(res_blocked.returncode, 0)
            self.assertIn("CRITICAL: Secret pattern", res_blocked.stderr)

            # Verify changes were unstaged
            staged_after = run_cmd(["git", "diff", "--cached", "--name-only"], tmp)
            self.assertEqual(staged_after.stdout.strip(), "")

            # 3. Deleting a secret line (only '-' lines in diff) must NOT trigger false positive
            run_cmd(["git", "add", "config.py"], tmp)
            run_cmd(["git", "commit", "-m", "seed file for deletion test"], tmp)
            secret_file.write_text("TOKEN = os.environ.get('TOKEN')\n", encoding="utf-8")
            res_del_ok = run_cmd(
                [sys.executable, str(commit_script), "-m", "remove hardcoded token"],
                tmp,
            )
            self.assertEqual(res_del_ok.returncode, 0, res_del_ok.stderr)

    def test_local_workflow_lifecycle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            init_isolated_git_repo(tmp)

            start_script = tmp / ".agents/skills/local-workflow/scripts/start_task_branch.py"
            commit_script = tmp / ".agents/skills/local-workflow/scripts/commit_wip.py"
            complete_script = tmp / ".agents/skills/local-workflow/scripts/complete_task.py"
            merge_script = tmp / ".agents/skills/local-workflow/scripts/merge_branch.py"

            # 1. Start task branch
            res_start = run_cmd(
                [
                    sys.executable,
                    str(start_script),
                    "-t",
                    "001-sample-task",
                    "--title",
                    "サンプルタスク",
                ],
                tmp,
            )
            self.assertEqual(res_start.returncode, 0, res_start.stderr)

            branch_res = run_cmd(["git", "branch", "--show-current"], tmp)
            self.assertEqual(branch_res.stdout.strip(), "task/001-sample-task")
            self.assertTrue((tmp / "docs/tasks/001-sample-task.md").exists())
            readme_active = (tmp / "docs/tasks/README.md").read_text(encoding="utf-8")
            self.assertIn("🟡 進行中: サンプルタスク", readme_active)

            # Verify main branch was not polluted before commit
            main_files = run_cmd(["git", "ls-tree", "-r", "--name-only", "main"], tmp).stdout
            self.assertNotIn("docs/tasks", main_files)

            # 2. Complete task document
            res_complete = run_cmd(
                [sys.executable, str(complete_script), "-t", "001-sample-task.md"],
                tmp,
            )
            self.assertEqual(res_complete.returncode, 0, res_complete.stderr)
            self.assertFalse((tmp / "docs/tasks/001-sample-task.md").exists())
            completed_task = tmp / "docs/tasks/completed/001-sample-task.md"
            self.assertTrue(completed_task.exists())
            completed_text = completed_task.read_text(encoding="utf-8")
            self.assertIn('status: "completed"', completed_text)
            self.assertIn("- **ステータス**: 🟢 完了", completed_text)

            readme_done = (tmp / "docs/tasks/README.md").read_text(encoding="utf-8")
            self.assertNotIn("🟡 進行中: サンプルタスク", readme_done)
            self.assertIn("[🟢 完了: サンプルタスク](completed/001-sample-task.md)", readme_done)

            # 3. Commit and merge back into main
            res_commit = run_cmd(
                [sys.executable, str(commit_script), "-m", "complete task", "-t", "001-sample-task"],
                tmp,
            )
            self.assertEqual(res_commit.returncode, 0, res_commit.stderr)

            res_merge = run_cmd(
                [sys.executable, str(merge_script), "-b", "task/001-sample-task", "--base-branch", "main"],
                tmp,
            )
            self.assertEqual(res_merge.returncode, 0, res_merge.stderr)

            cur_branch = run_cmd(["git", "branch", "--show-current"], tmp).stdout.strip()
            self.assertEqual(cur_branch, "main")
            branches = run_cmd(["git", "branch"], tmp).stdout
            self.assertNotIn("task/001-sample-task", branches)
            self.assertTrue((tmp / "docs/tasks/completed/001-sample-task.md").exists())

    def test_merge_branch_safety_guard_blocks_unmerged_deletion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            init_isolated_git_repo(tmp)
            merge_script = tmp / ".agents/skills/local-workflow/scripts/merge_branch.py"

            # Create unmerged task branch with a distinct commit
            run_cmd(["git", "checkout", "-b", "task/unmerged-task"], tmp)
            (tmp / "unmerged_file.txt").write_text("important data\n", encoding="utf-8")
            run_cmd(["git", "add", "unmerged_file.txt"], tmp)
            run_cmd(["git", "commit", "-m", "unmerged commit"], tmp)

            # Switch back to main and create a conflict
            run_cmd(["git", "checkout", "main"], tmp)
            (tmp / "unmerged_file.txt").write_text("conflicting data\n", encoding="utf-8")
            run_cmd(["git", "add", "unmerged_file.txt"], tmp)
            run_cmd(["git", "commit", "-m", "conflict on main"], tmp)

            # Attempt merge - must fail on merge conflict and keep task branch intact
            res = run_cmd(
                [sys.executable, str(merge_script), "-b", "task/unmerged-task", "--base-branch", "main"],
                tmp,
            )
            self.assertNotEqual(res.returncode, 0)
            branches = run_cmd(["git", "branch"], tmp).stdout
            self.assertIn("task/unmerged-task", branches)


if __name__ == "__main__":
    unittest.main()
