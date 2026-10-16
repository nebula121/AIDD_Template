---
spec_id: spec-router
title: 仕様書ルーティングマップ
layer: 1
category: index
status: stable
target_files:
  - docs/**/*.md
dependencies:
  - agents-guideline
---
# 仕様書ルーティングマップ

<!-- @spec:spec-router -->

プロジェクト全体の仕様書インデックス正本（SSOT）。部分読込時は以下の主タグまたはセクションサブタグを `grep` して行番号を特定すること (**MUST**)。

---

## 1. 仕様書ルーティング ＆ サブタグ一覧

<!-- @spec:spec-routing-table -->

新規コンポーネント仕様書（`docs/components/<id>.md`）を追加した際は、必ず本表に行を追加し、Frontmatterおよびファイル内のサブタグ（`component-<id>-scope`, `component-<id>-interface`, `component-<id>-contract`, `component-<id>-verification`）と完全一致させること (**MUST**)。

| Layer | 仕様書 | 主タグ | セクションサブタグ | 対象スコープ | 依存仕様 |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **0** | [AGENTS.md](../AGENTS.md) | `@spec:agents-guideline` | `agent-three-layer-structure`, `agent-invincible-rules`, `agent-context-retrieval`, `agent-task-execution` | `AGENTS.md` | `-` |
| **1** | [core-rules.md](core-rules.md) | `@spec:core-rules` | `architecture-and-security-rules`, `lifecycle-and-test-rules` | `**/*` | `agents-guideline` |
| **1** | [spec-router.md](spec-router.md) | `@spec:spec-router` | `spec-routing-table` | `docs/**/*.md` | `agents-guideline` |
| **1** | [system/overview.md](system/overview.md) | `@spec:system-overview` | `system-purpose`, `system-scope` | `README.md` | `core-rules` |
| **1** | [system/domain-rules.md](system/domain-rules.md) | `@spec:domain-rules` | `domain-glossary`, `domain-invariants` | `**/*` | `core-rules`, `system-overview` |
| **1** | [system/architecture.md](system/architecture.md) | `@spec:system-architecture` | `architecture-diagram`, `component-map`, `data-flow` | `**/*` | `core-rules`, `system-overview`, `domain-rules` |
| **1** | [system/tech-stack.md](system/tech-stack.md) | `@spec:tech-stack` | `runtime-stack`, `directory-structure`, `verification-commands` | `**/*` | `core-rules`, `system-architecture` |
| **1** | [components/_template.md](components/_template.md) | `@spec:component-template` | `component-template-schema`, `component-template-scope`, `component-template-interface`, `component-template-contract`, `component-template-verification` | `docs/components/*.md` | `core-rules`, `domain-rules`, `system-architecture`, `tech-stack` |
