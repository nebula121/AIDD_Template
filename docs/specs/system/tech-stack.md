---
spec_id: tech-stack
title: 技術スタック ＆ 開発検証環境
status: draft
target_files:
  - "**/*"
dependencies:
  - core-rules
  - system-architecture
---
# 技術スタック ＆ 開発検証環境

<!-- @spec:tech-stack -->

採用技術スタック、ディレクトリ構成、標準検証コマンド、および開発ワークフローの定義正本。

---

## 1. 技術スタック ＆ 動作環境

<!-- @spec:runtime-stack -->

| 分類 | 採用技術・バージョン | 用途・選定制約 (`MUST` / `SHOULD`) |
| :--- | :--- | :--- |
| **言語 / ランタイム** | `[要記入: 例 Python 3.12+ / TypeScript 5.x (Node 22)]` | `[要記入: 実行環境の前提]` |
| **主要パッケージ** | `[要記入: フレームワーク・主要ライブラリ]` | `[要記入: 標準ライブラリ優先・外部依存の境界]` |
| **データストア / 基盤** | `[要記入: SQLite / PostgreSQL / ローカルFS 等]` | `[要記入: 永続化・実行基盤]` |

---

## 2. ディレクトリ構成マップ

<!-- @spec:directory-structure -->

| パス | 役割・配置対象 |
| :--- | :--- |
| `AGENTS.md` | メタ行動規範（Layer 0・不変） |
| `docs/specs/spec-router.md` | ルーティング索引（Layer -・自動生成） |
| `docs/specs/core-rules.md` | システム憲法（Layer 1・不変） |
| `docs/specs/system/*.md` | システム全体設計（Layer 2・可変） |
| `docs/specs/components/*.md` | 個別仕様正本（Layer 3・可変 / `_template.md` は不変） |
| `docs/specs/usecases/*.md` | ユースケース正本（Layer 4・可変 / `_template.md` は不変） |
| `.agents/skills/` | 手順・スキル運用（(Tools)・不変） |
| `[要記入: src/ 等]` | `[要記入: アプリケーション実装コード]` |
| `[要記入: tests/ 等]` | `[要記入: 自動テストスイート]` |

---

## 3. 標準検証コマンド ＆ 開発ワークフロー

<!-- @spec:verification-commands -->

コードまたは仕様の変更後、報告前に必ず以下の全検証を実行し、合格基準を満たすこと (**MUST**)。

| 区分 | 実行コマンド / 採用スキル | 合格基準 |
| :--- | :--- | :--- |
| **仕様書整合性** | `python .agents/skills/spec-verification/scripts/verify_specs.py`（通常開発時）<br>`python .agents/skills/spec-verification/scripts/verify_specs.py --strict`（Bootstrap完了後・実運用時） | エラー `0` 件 (Exit Code `0`) |
| **ビルド / 型検査** | `[要記入: 例 npm run typecheck / mypy src / cargo check]` | エラー `0` 件 (Exit Code `0`) |
| **静的解析** | `[要記入: 例 npm run lint / ruff check . / cargo clippy]` | 警告・エラー `0` 件 (Exit Code `0`) |
| **自動テスト** | `[要記入: 例 npm test / pytest / cargo test]` | 全件 PASS (Exit Code `0`) |
| **開発ワークフロー** | `[要記入: .agents/skills/workflow (GitHub PR) または .agents/skills/local-workflow (ローカル完結)]` | ワークフロー規定の DoD 完全充足 |
