#!/usr/bin/env python3
"""Unit and integration tests for .agents/skills/spec-verification/scripts/verify_specs.py."""

import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VERIFY_SCRIPT_REL = Path(".agents/skills/spec-verification/scripts/verify_specs.py")
VERIFY_SCRIPT_PATH = REPO_ROOT / VERIFY_SCRIPT_REL

spec = importlib.util.spec_from_file_location("verify_specs", VERIFY_SCRIPT_PATH)
verify_specs = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(verify_specs)


def setup_isolated_repo(tmp: Path, strict_ready: bool = False) -> None:
    """Populate tmp directory with a copy of repo specs and required skill links."""
    for skill in ["spec-to-readable-html", "ponytail", "spec-verification", "workflow", "local-workflow"]:
        skill_dir = tmp / ".agents/skills" / skill
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(f"# {skill}\n", encoding="utf-8")
    (tmp / VERIFY_SCRIPT_REL).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(VERIFY_SCRIPT_PATH, tmp / VERIFY_SCRIPT_REL)
    shutil.copy2(REPO_ROOT / "AGENTS.md", tmp / "AGENTS.md")
    shutil.copy2(REPO_ROOT / "README.md", tmp / "README.md")
    shutil.copy2(REPO_ROOT / ".gitignore", tmp / ".gitignore")
    shutil.copytree(REPO_ROOT / "docs", tmp / "docs")
    if not strict_ready and (REPO_ROOT / "BOOTSTRAP.md").exists():
        shutil.copy2(REPO_ROOT / "BOOTSTRAP.md", tmp / "BOOTSTRAP.md")

    if strict_ready:
        (tmp / "README.md").write_text("# Test Project\n", encoding="utf-8")
        (tmp / "docs/specs/system/overview.md").write_text(
            """---
spec_id: system-overview
title: システム概要 ＆ スコープ
status: stable
target_files:
  - README.md
dependencies:
  - core-rules
---
# システム概要 ＆ スコープ

<!-- @spec:system-overview -->
<!-- @spec:system-purpose -->
<!-- @spec:system-scope -->
""",
            encoding="utf-8",
        )
        (tmp / "docs/specs/system/domain-rules.md").write_text(
            """---
spec_id: domain-rules
title: ドメイン用語 ＆ ドメイン不可侵ルール
status: stable
target_files:
  - "**/*"
dependencies:
  - core-rules
  - system-overview
---
# ドメイン用語 ＆ ドメイン不可侵ルール

<!-- @spec:domain-rules -->
<!-- @spec:domain-glossary -->
<!-- @spec:domain-invariants -->
""",
            encoding="utf-8",
        )
        (tmp / "docs/specs/system/architecture.md").write_text(
            """---
spec_id: system-architecture
title: システムアーキテクチャ ＆ コンポーネント構成
status: stable
target_files:
  - "**/*"
dependencies:
  - core-rules
  - system-overview
  - domain-rules
---
# システムアーキテクチャ ＆ コンポーネント構成

<!-- @spec:system-architecture -->

## 1. コンポーネント単方向依存グラフ

<!-- @spec:architecture-diagram -->

## 2. コンポーネント責務 ＆ 仕様書マッピング

<!-- @spec:component-map -->

| コンポーネントID | 個別仕様書 | 対象コードパス (`target_files`) | 単一責務の定義 | 依存先コンポーネント |
| :--- | :--- | :--- | :--- | :--- |
| `auth` | [auth.md](../components/auth.md) | `src/auth.py` | 認証処理 | `-` |

## 3. 外部境界 ＆ データフロー契約

<!-- @spec:data-flow -->

| 境界区分 | プロトコル / 形式 | 入出力対象・永続化ストア | バリデーション・変換契約 (`MUST`) |
| :--- | :--- | :--- | :--- |
| **外部入力** | CLI \\| HTTP | ユーザー入力 | バリデーション必須 |
""",
            encoding="utf-8",
        )
        (tmp / "docs/specs/system/tech-stack.md").write_text(
            """---
spec_id: tech-stack
title: 技術スタック ＆ 開発検証環境
status: stable
target_files:
  - "**/*"
dependencies:
  - core-rules
  - system-architecture
---
# 技術スタック ＆ 開発検証環境

<!-- @spec:tech-stack -->
<!-- @spec:runtime-stack -->
<!-- @spec:directory-structure -->
<!-- @spec:verification-commands -->
""",
            encoding="utf-8",
        )
        (tmp / "docs/specs/components/auth.md").write_text(
            """---
spec_id: component-auth
title: 認証コンポーネント
status: draft
target_files:
  - src/auth.py
dependencies:
  - core-rules
  - domain-rules
  - system-architecture
  - tech-stack
---
# 認証コンポーネント

<!-- @spec:component-auth -->

## 1. 責務と境界
<!-- @spec:component-auth-scope -->

## 2. 公開インターフェース ＆ データ構造
<!-- @spec:component-auth-interface -->

## 3. ふるまい ＆ 異常系契約
<!-- @spec:component-auth-contract -->

## 4. 受入条件 ＆ 検証基準
<!-- @spec:component-auth-verification -->
""",
            encoding="utf-8",
        )


def run_verifier(tmp: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(tmp / VERIFY_SCRIPT_REL), *args],
        cwd=tmp,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


class TestVerifySpecsUnit(unittest.TestCase):
    """Unit tests for pure helper functions in verify_specs.py."""

    def test_strip_code_and_comments_order(self) -> None:
        raw = (
            "Inline opener `<!--` should not swallow [link](a.md) before `-->`.\n"
            "<!-- real comment [ignored](b.md) -->\n"
            "```markdown\n"
            "<!-- @spec:in-code -->\n"
            "[code-link](c.md)\n"
            "```\n"
        )
        code_stripped = verify_specs.strip_code(raw)
        self.assertIn("[link](a.md)", code_stripped)
        self.assertNotIn("@spec:in-code", code_stripped)

        fully_stripped = verify_specs.strip_code_and_comments(raw)
        self.assertIn("[link](a.md)", fully_stripped)
        self.assertNotIn("[ignored](b.md)", fully_stripped)
        self.assertNotIn("[code-link](c.md)", fully_stripped)

    def test_parse_markdown_table_rows_escaped_pipes(self) -> None:
        table_md = (
            "| Col1 | Col2 | Col3 | Col4 |\n"
            "| :--- | :--- | :--- | :--- |\n"
            "| A | CLI \\| HTTP | `x | y` | D |\n"
        )
        self.assertEqual(verify_specs.parse_markdown_table_rows(table_md, 5), [])
        rows_4 = verify_specs.parse_markdown_table_rows(table_md, 4)
        self.assertEqual(len(rows_4), 2)
        self.assertEqual(rows_4[1][1], "CLI | HTTP")
        self.assertEqual(rows_4[1][2], "`x | y`")

    def test_dag_validation_inversions_and_cycles(self) -> None:
        specs_by_id = {
            "core-rules": {"path": "docs/specs/core-rules.md", "category": 1, "dependencies": ["comp-a"]},
            "comp-a": {"path": "docs/specs/components/a.md", "category": "components", "dependencies": ["comp-b", "spec-router"]},
            "comp-b": {"path": "docs/specs/components/b.md", "category": "components", "dependencies": ["comp-a", "unknown-id"]},
            "spec-router": {"path": "docs/specs/spec-router.md", "category": "-", "dependencies": []},
        }
        errors: list[str] = []
        verify_specs.check_dag_cycles(specs_by_id, errors)
        joined = "\n".join(errors)
        self.assertIn("cannot depend on project spec", joined)
        self.assertIn("cannot depend on router index", joined)
        self.assertIn("Unknown dependency spec_id 'unknown-id'", joined)
        self.assertIn("Document DAG cycle detected", joined)

    def test_dynamic_category_and_template_dag(self) -> None:
        specs_by_id = {
            "agents-guideline": {"path": "AGENTS.md", "category": 0, "spec_id": "agents-guideline", "dependencies": []},
            "core-rules": {"path": "docs/specs/core-rules.md", "category": 1, "spec_id": "core-rules", "dependencies": ["agents-guideline"]},
            "service-auth": {"path": "docs/specs/services/auth.md", "category": "services", "spec_id": "service-auth", "dependencies": ["core-rules"]},
            "service-template": {"path": "docs/specs/services/_template.md", "category": "services", "spec_id": "service-template", "dependencies": ["core-rules"]},
        }
        mermaid_dag = verify_specs.generate_mermaid_dag(specs_by_id)
        self.assertIn('subgraph services["services"]', mermaid_dag)
        self.assertIn('service-auth["services/auth.md"]', mermaid_dag)
        self.assertNotIn("service-template", mermaid_dag)


class TestVerifySpecsIntegration(unittest.TestCase):
    """Integration tests running verify_specs.py in isolated temporary directories."""

    def test_template_standard_and_strict_modes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            setup_isolated_repo(tmp, strict_ready=False)

            res_std = run_verifier(tmp)
            self.assertEqual(res_std.returncode, 0, res_std.stderr)

            res_strict = run_verifier(tmp, "--strict")
            self.assertNotEqual(res_strict.returncode, 0)
            self.assertIn("BOOTSTRAP.md: File still exists", res_strict.stderr)
            self.assertNotIn("Mapped component 'docs/specs/components/<id>.md' does not exist", res_strict.stderr)

    def test_frontmatter_h1_and_ssot_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            setup_isolated_repo(tmp, strict_ready=True)
            self.assertEqual(run_verifier(tmp, "--sync").returncode, 0)

            bad_comp = tmp / "docs/specs/components/bad.md"
            bad_comp.write_text(
                """---
spec_id: component-auth
title: タイトルA
layer: 3
status: invalid_status
target_files:
  - src/bad.py
dependencies:
  - core-rules
---
# 異なるH1見出し

<!-- @spec:component-auth -->
""",
                encoding="utf-8",
            )
            res = run_verifier(tmp)
            self.assertNotEqual(res.returncode, 0)
            self.assertIn("Unexpected/deprecated frontmatter keys: layer", res.stderr)
            self.assertIn("H1 heading '異なるH1見出し' does not match Frontmatter title 'タイトルA'", res.stderr)
            self.assertIn("Invalid status 'invalid_status'", res.stderr)
            self.assertIn("Duplicate spec_id 'component-auth'", res.stderr)
            self.assertIn("Duplicate tag '@spec:component-auth'", res.stderr)

    def test_strict_mode_draft_vs_stable_and_template_placeholders(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            setup_isolated_repo(tmp, strict_ready=True)
            self.assertEqual(run_verifier(tmp, "--sync").returncode, 0)

            # 1. Draft component with non-existent target_files passes --strict
            res_pass = run_verifier(tmp, "--strict")
            self.assertEqual(res_pass.returncode, 0, res_pass.stderr)

            # 2. Stable component with non-existent target_files fails
            auth_path = tmp / "docs/specs/components/auth.md"
            orig_auth = auth_path.read_text(encoding="utf-8")
            auth_path.write_text(orig_auth.replace("status: draft", "status: stable"), encoding="utf-8")
            res_stable_fail = run_verifier(tmp, "--strict")
            self.assertNotEqual(res_stable_fail.returncode, 0)
            self.assertIn("target_files pattern 'src/auth.py' matched 0 files", res_stable_fail.stderr)

            # 3. Leftover _template.md placeholders and tags fail in --strict
            auth_path.write_text(
                orig_auth + "\n| `<関数名 / クラス名 / API>` |\n<!-- @spec:component-template -->\n",
                encoding="utf-8",
            )
            res_tmpl_fail = run_verifier(tmp, "--strict")
            self.assertNotEqual(res_tmpl_fail.returncode, 0)
            self.assertIn("Unfilled template placeholder '<...>'", res_tmpl_fail.stderr)
            self.assertIn("Unreplaced template tag '@spec:component-template'", res_tmpl_fail.stderr)

    def test_sync_after_spec_deletion_and_mermaid_dag_filtering(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            setup_isolated_repo(tmp, strict_ready=True)
            auth_text = (tmp / "docs/specs/components/auth.md").read_text(encoding="utf-8")
            extra_path = tmp / "docs/specs/components/extra.md"
            extra_path.write_text(
                auth_text.replace("auth", "extra").replace("認証", "追加"),
                encoding="utf-8",
            )
            self.assertEqual(run_verifier(tmp, "--sync").returncode, 0)

            router_text = (tmp / "docs/specs/spec-router.md").read_text(encoding="utf-8")
            self.assertIn('component-auth["components/auth.md"]', router_text)
            self.assertIn('component-extra["components/extra.md"]', router_text)
            self.assertNotIn('component-template["components/_template.md"]', router_text)
            self.assertIn("[components/_template.md](components/_template.md)", router_text)

            # Delete extra.md and verify first --sync succeeds with Exit Code 0
            extra_path.unlink()
            res_sync = run_verifier(tmp, "--sync")
            self.assertEqual(res_sync.returncode, 0, res_sync.stderr)


if __name__ == "__main__":
    unittest.main()
