---
spec_id: spec-router
title: 仕様書ルーティングマップ (Spec Router)
layer: 1
category: index
status: stable
target_files:
  - docs/**/*.md
dependencies:
  - agents-guideline
---

# {{PROJECT_NAME}} - 仕様書ルーティングマップ (Spec Router)
<!-- @spec:spec-router -->

本ドキュメントは、プロジェクト全体の**仕様書インデックス正本（SSOT）**である。
各仕様書の配置パス、主要 `@spec` タグ、対象成果物、および仕様間の依存関係をマッピングする。

---

## 仕様書ルーティングマップ (Spec Routing Map)

| Layer | 仕様書 (Path) | 主要 `@spec` タグ | 対象ファイル (Scope) | 依存仕様 (`dependencies`) |
| :---: | :--- | :--- | :--- | :--- |
| **0** | [AGENTS.md](../AGENTS.md) | `@spec:agents-guideline` | プロジェクト全体 | - |
| **1** | [core-rules.md](core-rules.md) | `@spec:core-rules` | プロジェクト全体 | `agents-guideline` |
| **1** | [spec-router.md](spec-router.md) | `@spec:spec-router` | `docs/**/*.md` | `agents-guideline` |
| **1** | [overview.md](overview.md) | `@spec:system-architecture` | `src/` | `core-rules` |
| **1** | [architecture/domain-rules.md](architecture/domain-rules.md) | `@spec:domain-rules` | `src/` | `core-rules`, `system-architecture` |
| **1** | [specs/_template.md](specs/_template.md) | `@spec:spec-template` | `docs/specs/*.md` | `core-rules`, `system-architecture` |

<!--
【新規機能仕様追加時の登録フォーマット】
| 1 | [specs/<feature-id>.md](specs/<feature-id>.md) | `@spec:<feature-id>` | `<対象コードパス>`, `<対象テストパス>` | `invincible-rules`, `system-architecture` |
-->
