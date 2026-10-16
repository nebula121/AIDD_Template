# AIDD 初期環境整備プロトコル

対象プロジェクト（既存または新規）へ適合させた仕様書群および開発環境を構築する初期実行手順書。
「環境整備して」「このプロジェクトに適合させて仕様書を生成して」と指示されたAIエージェントは、以下のガードおよび4フェーズを厳守すること (**MUST**)。

---

## 0. 絶対遵守ガード

| 項目 | 必須契約 (`MUST` / `MUST NOT`) |
| :--- | :--- |
| **不変ファイルの保護** | [AGENTS.md](AGENTS.md)・[docs/core-rules.md](docs/core-rules.md)・[docs/components/_template.md](docs/components/_template.md)・`.agents/skills/` は **1文字たりとも変更してはならない** (**MUST NOT**)。 |
| **高密度スキーマ記述** | 生成する `docs/**/*.md` は定型挨拶・要約・散文を排し、Frontmatter・標準サブタグ・構造化表・RFC 2119契約のみで記述する (**MUST**)。 |
| **テンプレート残骸の完全消去** | 完了時点で `[要記入: ...]`・`{{...}}`・`TODO`・`<!-- GUIDE: ... -->`、および本ファイル（`BOOTSTRAP.md`）を完全消去する (**MUST**)。 |

---

## 1. フェーズ別実行プロトコル

| フェーズ | 実行内容 | 完了ゲート |
| :--- | :--- | :--- |
| **Step 1: 調査** | **【既存プロジェクト】** 以下の一次情報を順番に走査する（大規模時は `research` サブエージェント［`flash` / `flash_lite`］を並列起動）：<br>① マニフェスト（`package.json`, `pyproject.toml`, `Cargo.toml` 等）＆ CI定義（`.github/workflows` 等）から技術スタックと検証コマンドを特定し、**シェルで1回実働確認する (MUST)**。<br>② コンパイラ・静的解析設定（`tsconfig.json`, `ruff.toml` 等）から型・境界制約を特定。<br>③ エントリポイント・Import依存グラフ・公開型から単一責務のコンポーネント集合を特定。<br>④ 既存テストコードの `assert` からドメイン不変条件と受入条件を抽出。<br>**【新規プロジェクト】** 指示から目的・技術スタック・主要コンポーネント・ワークフローを特定し、不足項目がある場合のみ計画提示前に最小限（1〜3問）確認する。 | 全コンポーネント境界と検証コマンドが特定されていること。 |
| **Step 2: 計画・承認** | ① システム横断定義（目的・用語・不変条件・技術スタック・検証コマンド）の要約、② [docs/system/architecture.md](docs/system/architecture.md) と1対1対応する分割コンポーネント一覧（ID・責務・`target_files`・依存先）を提示する。 | ユーザーの明示的な計画承認を得ること (**MUST**)。 |
| **Step 3: 生成・削除** | 承認後、以下の可変ファイルを一括生成・更新し（既存実装済みは `status: stable`、未実装は `status: draft`）、最後に **本ファイル（`BOOTSTRAP.md`）を削除する (MUST)**：<br>① `docs/system/` 配下の4ファイル（[overview.md](docs/system/overview.md), [domain-rules.md](docs/system/domain-rules.md), [architecture.md](docs/system/architecture.md), [tech-stack.md](docs/system/tech-stack.md)）の全テーブル記入とガイドコメント除去。<br>② [docs/components/_template.md](docs/components/_template.md) の4章スキーマ（必須サブタグ5個）に従う全 `docs/components/<id>.md` の作成（[architecture.md](docs/system/architecture.md) のコンポーネント表と1対1対応）。<br>③ [docs/spec-router.md](docs/spec-router.md) のルーティング表への全 `components/<id>.md` の追加登録（主タグ・セクションサブタグ・依存仕様を完全同期）。<br>④ [README.md](README.md) ＆ [.gitignore](.gitignore) の更新（既存プロジェクトは既存内容を保持し、`docs/spec-router.md` 案内と `diff_summary_for_agent.txt` / `docs/**/*.html` 除外設定のみマージ追記）。 | 全可変ファイルの生成と `BOOTSTRAP.md` の削除が完了していること。 |
| **Step 4: 検証・報告** | ① `git diff --exit-code AGENTS.md docs/core-rules.md docs/components/_template.md`（差分ゼロ証明）<br>② `python .agents/skills/spec-verification/scripts/verify_specs.py --strict`（エラー0件証明・失敗時は自律修復）<br>③ 上記2つのPASS結果を添えて Walkthrough を報告し、人間向け閲覧手段として `/spec-to-readable-html` を案内する。 | 上記2コマンドがともに Exit Code `0` で通過していること (**MUST**)。 |
