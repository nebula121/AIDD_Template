# AIDD 初期環境整備 ＆ 最新テンプレート再適用プロトコル

`ref/` 配下（例: `ref/AIDD_Template/`）にステージング配置された最新テンプレート（またはルート展開されたテンプレート）から、対象プロジェクト（**新規**・**既存未導入**・**過去AIDD適用済み**）へ最新の仕様書体系および開発環境を構築・再適用する実行手順書。
「環境整備して」「BOOTSTRAP.mdに従ってやって」「最新テンプレートを再適用して」と指示されたAIエージェントは、以下の3分類ガードおよび4フェーズを厳守すること (**MUST**)。

---

## 0. ファイル3分類 ＆ 絶対遵守ガード

| 分類 / 項目 | 対象パス | 必須契約 (`MUST` / `MUST NOT`) |
| :--- | :--- | :--- |
| **① 完全上書き（不変正本 ＆ ツール）** | [AGENTS.md](AGENTS.md)・[docs/core-rules.md](docs/core-rules.md)・[docs/components/_template.md](docs/components/_template.md)・`.agents/skills/` | ・不変3ファイルは最新テンプレート正本で **1文字の改変もなく完全上書き（100%一致）** させる (**MUST**)。<br>・`.agents/skills/` は最新テンプレート側の同名スキルディレクトリのみを上書き同期し、プロジェクト独自の追加スキルは消去せず保持する (**MUST**)。 |
| **② 既存へ最新スキーマ注入（業務資産）** | `docs/system/*.md`・`docs/components/<id>.md`・[README.md](README.md)・[.gitignore](.gitignore) | ・**【新規 / 既存未導入】**: コード調査（またはヒアリング）から高密度スキーマ（定型挨拶・散文を排し、Frontmatter・標準サブタグ・構造化表・RFC 2119契約のみ）で新規生成する (**MUST**)。<br>・**【再適用（過去AIDD適用済み）】**: 記入済みの業務仕様・契約内容を **絶対に消去・初期化せず保持** したまま、最新テンプレートのFrontmatter必須5キー（旧 `layer`/`category` 等の廃止キー除去）・必須見出し・標準サブタグ・表構造との差分のみを注入・適合させる (**MUST**)。 |
| **③ 自動生成 ＆ 残骸完全消去** | [docs/spec-router.md](docs/spec-router.md)・`BOOTSTRAP.md`・`ref/` | ・[docs/spec-router.md](docs/spec-router.md) は最新テンプレートの枠組みを配置後、`verify_specs.py --sync` で完全自動生成する（手動編集 **MUST NOT**）。<br>・完了時点で `[要記入: ...]`・`{{...}}`・`<!-- GUIDE: ... -->`、およびステージング配置された `ref/` 内のテンプレート一式と `BOOTSTRAP.md` を完全消去する (**MUST**)。 |

---

## 1. フェーズ別実行プロトコル

| フェーズ | 実行内容 | 完了ゲート |
| :--- | :--- | :--- |
| **Step 1: 調査（モード自動判別）** | プロジェクトルートの状態から以下の3モードを自動判別して調査する：<br>**【再適用（過去AIDD適用済み）】**（ルートに記入済みの `docs/system/*.md` が存在する場合）：<br>① 既存の `docs/system/*.md` ＆ `docs/components/<id>.md` と、最新テンプレート（[overview.md](docs/system/overview.md), [domain-rules.md](docs/system/domain-rules.md), [architecture.md](docs/system/architecture.md), [tech-stack.md](docs/system/tech-stack.md), [_template.md](docs/components/_template.md)）を比較し、Frontmatter必須5キー（廃止キー `layer`/`category` 等の有無）・標準サブタグ・見出し構造の差分を特定する。<br>② [architecture.md](docs/system/architecture.md) と `docs/components/<id>.md` の1対1対応およびDAG依存方向に不整合がないか確認する。<br>**【既存プロジェクト（AIDD未導入）】**（既存コードはあるが記入済み `docs/system/` が不在の場合）：<br>以下の一次情報を順番に走査する（大規模時は `research` サブエージェント［`flash` / `flash_lite`］を並列起動）：<br>① マニフェスト（`package.json`, `pyproject.toml`, `Cargo.toml` 等）＆ CI定義から技術スタックと検証コマンドを特定し、**シェルで1回実働確認する (MUST)**。<br>② コンパイラ・静的解析設定（`tsconfig.json`, `ruff.toml` 等）から型・境界制約を特定。<br>③ エントリポイント・Import依存グラフ・公開型から単一責務のコンポーネント集合を特定。<br>④ 既存テストコードの `assert` からドメイン不変条件と受入条件を抽出。<br>**【新規プロジェクト】**（コードも記入済み仕様書も不在の場合）：<br>指示から目的・技術スタック・主要コンポーネント・ワークフローを特定し、不足項目がある場合のみ計画提示前に最小限（1〜3問）確認する。 | 適用モード（再適用 / 既存未導入 / 新規）および全変更対象・境界が特定されていること。 |
| **Step 2: 計画・承認** | **【再適用】** ① 完全上書きする不変ファイル・スキル一覧、② 既存仕様書（`docs/system/*.md`, `docs/components/<id>.md`）へ注入・適合するスキーマ変更点（業務記述は保持）、③ 自動生成・クリーンアップ対象を提示する。<br>**【新規 / 既存未導入】** ① システム横断定義（目的・用語・不変条件・技術スタック・検証コマンド）の要約、② [docs/system/architecture.md](docs/system/architecture.md) と1対1対応する分割コンポーネント一覧（ID・責務・`target_files`・依存先）を提示する。 | ユーザーの明示的な計画承認を得ること (**MUST**)。 |
| **Step 3: 同期・生成・削除** | 承認後、以下の処理を順に行い、最後に **ステージングされた `ref/` 内のテンプレート一式および `BOOTSTRAP.md` を削除する (MUST)**：<br>① **完全上書き同期**: 最新テンプレートから [AGENTS.md](AGENTS.md)・[docs/core-rules.md](docs/core-rules.md)・[docs/components/_template.md](docs/components/_template.md)・[docs/spec-router.md](docs/spec-router.md)（枠組み）をルート側へ完全上書きコピーし、`.agents/skills/` の同名スキルを上書き同期する（独自追加スキルは保持）。<br>② **仕様書の生成またはスキーマ注入**:<br>・**【再適用】**: 既存の `docs/system/*.md` ＆ `docs/components/<id>.md` の業務記述を保持したまま、Frontmatter必須5キーへの正規化（旧 `layer`/`category` 等の除去）・不足サブタグや見出し構造の注入・ガイドコメント除去を実施。<br>・**【新規 / 既存未導入】**: `docs/system/` 配下の4ファイル（[overview.md](docs/system/overview.md), [domain-rules.md](docs/system/domain-rules.md), [architecture.md](docs/system/architecture.md), [tech-stack.md](docs/system/tech-stack.md)）の全テーブル記入とガイドコメント除去、および [docs/components/_template.md](docs/components/_template.md) の4章スキーマ（必須サブタグ5個）に従う全 `docs/components/<id>.md` の作成（既存実装済みは `status: stable`、未実装は `status: draft`）。<br>③ **ルーティング自動生成**: `python .agents/skills/spec-verification/scripts/verify_specs.py --sync` を実行し、Frontmatter と配置パスから [docs/spec-router.md](docs/spec-router.md)（Mermaidネットワークグラフおよびルーティング表）を完全自動同期・最新化。<br>④ **環境設定マージ**: [README.md](README.md) ＆ [.gitignore](.gitignore) の更新（既存内容を保持し、`docs/spec-router.md` 案内と `ref/`・`diff_summary_for_agent.txt`・`docs/**/*.html` 除外設定のみマージ追記）。<br>⑤ **残骸消去**: `ref/` 内のテンプレートディレクトリおよびルートの `BOOTSTRAP.md` を完全削除する。 | 3分類の同期・適合・生成、および `ref/` テンプレートと `BOOTSTRAP.md` の削除が完了していること。 |
| **Step 4: 検証・報告** | ① 不変3ファイル（[AGENTS.md](AGENTS.md), [docs/core-rules.md](docs/core-rules.md), [docs/components/_template.md](docs/components/_template.md)）が最新テンプレート正本と差分ゼロで一致していることの確認<br>② `python .agents/skills/spec-verification/scripts/verify_specs.py --strict`（エラー0件証明・失敗時は自律修復）<br>③ 上記のPASS結果を添えて Walkthrough を報告し、人間向け閲覧手段として `/spec-to-readable-html` を案内する。 | `verify_specs.py --strict` が Exit Code `0` で通過していること (**MUST**)。 |
