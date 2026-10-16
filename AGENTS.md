---
spec_id: agents-guideline
title: AI行動規範
layer: 0
category: guideline
status: stable
target_files:
  - AGENTS.md
dependencies: []
---
# AI行動規範

<!-- @spec:agents-guideline -->

## 1. 3層アーキテクチャ ＆ CQRS仕様分離

<!-- @spec:agent-three-layer-structure -->

| Layer | 分類 | 配置パス | 対象読者 | 責務と安全境界 |
| :---: | :--- | :--- | :--- | :--- |
| **0** | **メタ行動規範** | `AGENTS.md` | AI | 思考・コンテキスト制御・実行プロトコル（常時適用・不変） |
| **1** | **仕様・制約正本** | `docs/**/*.md` | AI / 検証器 | 高密度な契約・不変条件・受入条件（Normalized SSOT・部分参照） |
| **2** | **手順・スキル運用** | `.agents/skills/` | AI / 人間 | 開発ワークフロー・静的検証・人間向けHTML変換（オンデマンド実行） |

| 表現形式 | 役割 (CQRS) | 記述・運用規約 | Git管理 |
| :--- | :--- | :--- | :---: |
| **Markdown (`docs/**/*.md`)** | **Write & AI Read Model (SSOT)** | 装飾・要約・定型挨拶を排し、Frontmatter・タグ・構造化表・RFC 2119契約のみを記述する (**MUST**)。 | 追跡対象 |
| **HTML (`spec-to-readable-html`)** | **Human Read-Only View** | 人間の視覚的俯瞰用。[spec-to-readable-html](.agents/skills/spec-to-readable-html/SKILL.md) でオンデマンド生成し、直接編集してはならない (**MUST NOT**)。 | 非追跡 |

---

## 2. コンテキスト取得 ＆ 常時適用の絶対境界

<!-- @spec:agent-invincible-rules -->

### 2.1 ピンポイント部分読込プロトコル

<!-- @spec:agent-context-retrieval -->

1. **一括読込の禁止**: 通常開発時における仕様書群の全件読込・連鎖読込を禁じる (**MUST NOT**)。
2. **タグ検索＋スライス読込**: [spec-router.md](docs/spec-router.md) で対象仕様書とセクションタグを特定し、タグを `grep` して行番号を取得した上で、行範囲指定（`StartLine` / `EndLine`）により該当セクションのみを部分読込すること (**MUST**)。
3. **初期環境整備（Bootstrap）の例外起点**: ルートに `BOOTSTRAP.md` が存在し、プロジェクト適合・初期環境整備を指示された場合は、`BOOTSTRAP.md` を読み込んでその手順に従うこと (**MUST**)。

### 2.2 常時行動制約マトリクス

| 領域 | 必須アクション (`MUST` / `SHOULD`) | 絶対禁止事項 (`MUST NOT`) |
| :--- | :--- | :--- |
| **不可侵境界の事前確認** | コード・仕様変更前に [core-rules.md](docs/core-rules.md) と [domain-rules.md](docs/system/domain-rules.md) の該当セクションを確認する (**MUST**)。 | 不可侵ルール・不変条件に反するコードや仕様の生成 (**MUST NOT**)。 |
| **調査と変更の分離** | 指示が「調査・確認・質問」の場合は結果報告のみに留める (**MUST**)。 | 実装計画の事前承認なきコード・仕様の自律変更 (**MUST NOT**)。 |
| **Ponytail最小構成** | [ponytail](.agents/skills/ponytail/SKILL.md) に従い最短・最小差分で実装する (**MUST**)。 | 仕様にない抽象化・単一実装IF・過剰ボイラープレートの作成 (**MUST NOT**)。 |
| **SDD ＆ SSOT** | 実装前に仕様書の受入条件と検証テストを揃える (**MUST**)。仕様変更時は [spec-verification](.agents/skills/spec-verification/SKILL.md) を実行する (**MUST**)。 | 仕様なき実装（No Spec, No Code）、仕様の重複定義、派生HTMLの編集・コミット (**MUST NOT**)。 |
| **ドキュメントDAG** | Layer 0 を最上位とする単方向依存（DAG）を維持する (**MUST**)。案内リンクと仕様依存（`dependencies`）を区別する (**MUST**)。 | 同一・異なるレイヤー間の循環依存、下位文書による上位規範の上書き (**MUST NOT**)。 |
| **サブエージェント協調** | 親は対話・統制・設計・受入を担い、起動コストを上回る実益（並列化・コンテキスト節約・客観検証）がある独立課題を子へ委任する (**MUST**)。リサーチ等は軽量モデル（`flash` / `flash_lite` 等）を指定する (**SHOULD**)。 | 曖昧な責務での委任、サブエージェント成果物の無検証受入 (**MUST NOT**)。 |
| **言語・エンコード** | チャットおよび作成ドキュメントは日本語、文字コードは UTF-8 を標準とする (**MUST**)。 | 既存ファイルの意図しないエンコード・改行コード変更 (**MUST NOT**)。 |

---

## 3. フェーズ別実行プロトコル

<!-- @spec:agent-task-execution -->

すべての変更タスクは以下の5フェーズを順守し、各完了ゲートを満たしてから次フェーズへ進むこと (**MUST**)。

| フェーズ | 参照正本・使用スキル | 必須アクション | 完了ゲート（次フェーズ移行条件） |
| :--- | :--- | :--- | :--- |
| **1. 調査** | [spec-router.md](docs/spec-router.md) | 要求分析、関連タグの部分読込、変更対象と受入条件の特定（未整備なら仕様案作成）。 | 変更対象スコープと受入条件が特定されていること。 |
| **2. 計画・承認** | [ponytail](.agents/skills/ponytail/SKILL.md) | 変更内容・対象ファイル・検証方法を実装計画として提示する。 | ユーザーから明示的な計画承認を得ること（スコープ拡大時は再承認 **MUST**）。 |
| **3. 変更** | `workflow` / `local-workflow` | 承認範囲内で最小差分の仕様・テスト・コード変更を実施する。 | 承認スコープ外の無断変更が含まれていないこと。 |
| **4. 検証** | [spec-verification](.agents/skills/spec-verification/SKILL.md) | [tech-stack.md](docs/system/tech-stack.md) の標準検証コマンド（`verify_specs.py`・Test・Lint）を実行・自己修復する。 | 全検証コマンドが Exit Code `0` で通過していること。 |
| **5. 報告・承認** | `workflow` / `local-workflow` | 変更点・検証結果エビデンス・残課題を Walkthrough として提示する。 | ユーザーの最終承認をもってタスク完了とする。 |
