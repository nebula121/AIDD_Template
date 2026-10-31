# AIDD 初期環境整備 ＆ 最新テンプレート再適用プロトコル

`ref/` 配下（例: `ref/AIDD_Template/`）にステージング配置された最新テンプレート（またはルート展開されたテンプレート）から、対象プロジェクト（**新規**・**既存未導入**・**過去AIDD適用済み**）へ最新の仕様書体系および開発環境を構築・再適用する汎用実行手順書。
「環境整備して」「BOOTSTRAP.mdに従ってやって」「最新テンプレートを再適用して」と指示されたAIエージェントは、以下の3分類ガードおよび4フェーズを厳守すること (**MUST**)。

---

## 0. ファイル3分類 ＆ 絶対遵守ガード

| 分類 / 項目 | 対象パス | 必須契約 (`MUST` / `MUST NOT`) |
| :--- | :--- | :--- |
| **① 完全上書き（基盤・憲法・テンプレート・ツール）** | [AGENTS.md](AGENTS.md)・[docs/specs/core-rules.md](docs/specs/core-rules.md)・`docs/specs/**/_template.md`・`.agents/skills/` | ・基盤・憲法（Layer 0, 1）および全テンプレートひな形（`_template.md`）は最新テンプレート正本で **1文字の改変もなく完全上書き（100%一致）** させる (**MUST**)。<br>・`.agents/skills/` は最新テンプレート側の同名スキルディレクトリのみを上書き同期し、プロジェクト独自の追加スキルは消去せず保持する (**MUST**)。 |
| **② 既存へ最新スキーマ適合（業務仕様資産・環境設定）** | `docs/specs/<分類>/**/*.md`（`_template.md` 除く全ドメイン仕様正本群）・[README.md](README.md)・[.gitignore](.gitignore) | ・**【新規 / 既存未導入】**: コード調査（またはヒアリング）から最新テンプレートのスキーマ（定型挨拶・散文・ガイドコメントを排し、Frontmatter必須キー・標準サブタグ・構造化表・RFC 2119契約のみ）で新規生成する (**MUST**)。<br>・**【再適用（アップデート）】**: 記入済みの業務仕様・契約内容・受入条件を **絶対に消去・初期化せず100%保全** した上で、最新テンプレートのFrontmatter必須キー構造（未定義必須キーの補完・最新仕様で未定義の廃止キー除去）、対応する `_template.md` の見出し構造・標準サブタグ規約との差分のみを適合（マージ注入）し、不要なガイドコメントを除去する (**MUST**)。 |
| **③ 自動生成 ＆ 移行残骸完全消去** | [docs/specs/spec-router.md](docs/specs/spec-router.md)・`BOOTSTRAP.md`・`ref/` | ・[docs/specs/spec-router.md](docs/specs/spec-router.md) は最新テンプレートの枠組みを配置後、`python .agents/skills/spec-verification/scripts/verify_specs.py --sync` で完全自動生成する（手動編集 **MUST NOT**）。<br>・完了時点で未記入プレースホルダ（`[要記入: ...]`・`{{...}}`・`<!-- GUIDE: ... -->`）、およびステージング配置された `ref/` 内のテンプレート一式と `BOOTSTRAP.md` を完全消去する (**MUST**)。 |

---

## 1. フェーズ別実行プロトコル

| フェーズ | 実行内容 | 完了ゲート |
| :--- | :--- | :--- |
| **Step 1: 調査（モード自動判別）** | プロジェクトルートの状態から以下の3モードを自動判別して調査する：<br>**【再適用（過去AIDD適用済み）】**（ルートに記入済みの `docs/specs/<分類>/**/*.md` が存在する場合）：<br>① 既存仕様書群（分類②）と最新テンプレート（Frontmatter必須キーセットおよび各 `_template.md`）を比較し、注入すべきスキーマ差分を特定する。<br>② [architecture.md](docs/specs/system/architecture.md) 等のコンポーネント表と個別仕様書の全単射対応、および全仕様書間のDAG依存方向に不整合がないか確認する。<br>**【既存プロジェクト（AIDD未導入）】**（既存コードはあるが記入済み `docs/specs/<分類>/**/*.md` が不在の場合）：<br>以下の一次情報を順番に走査する（大規模時は `research` サブエージェント［`flash` / `flash_lite`］を並列起動）：<br>① マニフェスト（`package.json`, `pyproject.toml`, `Cargo.toml` 等）＆ CI定義から技術スタックと検証コマンドを特定し、**シェルで1回実働確認する (MUST)**。<br>② コンパイラ・静的解析設定（`tsconfig.json`, `ruff.toml` 等）から型・境界制約を特定。<br>③ エントリポイント・Import依存グラフ・公開型から単一責務の仕様正本集合を特定。<br>④ 既存テストコードの `assert` からドメイン不変条件と受入条件を抽出。<br>**【新規プロジェクト】**（コードも記入済み仕様書も不在の場合）：<br>指示から目的・技術スタック・主要仕様正本・ワークフローを特定し、不足項目がある場合のみ計画提示前に最小限（1〜3問）確認する。 | 適用モード（再適用 / 既存未導入 / 新規）および全変更対象・境界が特定されていること。 |
| **Step 2: 計画・承認** | **【再適用】** 分類①の上書き対象、分類②の既存仕様書へ注入するスキーマ差分（業務記述は保持）、分類③の自動生成・削除対象を提示する。<br>**【新規 / 既存未導入】** ① システム横断定義（目的・用語・不変条件・技術スタック・検証コマンド）の要約、② 分割仕様正本一覧（ID・責務・`target_files`・依存先）を提示する。 | ユーザーの明示的な計画承認を得ること (**MUST**)。 |
| **Step 3: 同期・適合・削除** | 承認後、第0章の3分類ガードに従い以下を順に行う (**MUST**)：<br>① **分類①（完全上書き同期）**: 基盤・憲法（Layer 0, 1）、全テンプレートひな形（`docs/specs/**/_template.md`）、[docs/specs/spec-router.md](docs/specs/spec-router.md)（枠組み）、`.agents/skills/`（同名スキルのみ）を最新テンプレート正本と同期する。<br>② **分類②（仕様書生成 / スキーマ適合）**: 判別モードに従い、新規生成または既存の業務記述を完全保全した上で最新スキーマ構造（Frontmatter必須キー、各分類ディレクトリに対応する最新 `_template.md` の見出し構造・標準サブタグ規約）へ差分適合させる（実装済みは `status: stable`、未実装は `status: draft`）。<br>③ **分類②（環境設定マージ）**: [README.md](README.md) ＆ [.gitignore](.gitignore) の既存内容を保持し、最新テンプレートが要求するルーティング案内および除外設定（`ref/`・`diff_summary_for_agent.txt`・`docs/specs-html/`・`docs/**/*.html` 等）のみをマージ追記する。<br>④ **分類③（自動生成 ＆ 残骸消去）**: `python .agents/skills/spec-verification/scripts/verify_specs.py --sync` で [docs/specs/spec-router.md](docs/specs/spec-router.md) を自動生成後、`ref/` 内のテンプレート一式と `BOOTSTRAP.md` を完全削除する (**MUST**)。 | 3分類の同期・適合・生成、および `ref/` テンプレートと `BOOTSTRAP.md` の削除が完了していること。 |
| **Step 4: 検証・報告** | ① 分類①の基盤・憲法・テンプレート群が最新テンプレート正本と差分ゼロで一致していることを確認する。<br>② `python .agents/skills/spec-verification/scripts/verify_specs.py --strict` を実行する（エラー0件証明・失敗時は自律修復）。<br>③ 上記のPASS結果を添えて Walkthrough を報告し、人間向け閲覧手段として `/spec-to-readable-html` を案内する。 | `verify_specs.py --strict` が Exit Code `0` で通過していること (**MUST**)。 |
