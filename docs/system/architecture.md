---
spec_id: system-architecture
title: システムアーキテクチャ ＆ コンポーネント構成
layer: 2
category: architecture
status: draft
target_files:
  - "**/*"
dependencies:
  - core-rules
  - system-overview
  - domain-rules
---
# システムアーキテクチャ ＆ コンポーネント構成

<!-- @spec:system-architecture -->

システム全体のコンポーネント分割、単方向依存グラフ、および外部入出力データフローの定義正本。

---

## 1. コンポーネント単方向依存グラフ

<!-- @spec:architecture-diagram -->

```mermaid
flowchart LR
    Entry["[要記入: エントリポイント / UI / API]"] --> Core["[要記入: コアドメイン / サービス]"]
    Core --> Infra["[要記入: 永続化 / 外部アダプタ]"]
```

---

## 2. コンポーネント責務 ＆ 仕様書マッピング

<!-- @spec:component-map -->

本表の各行は `docs/components/<id>.md` の個別仕様書と **1対1（全単射）** で対応する (**MUST**)。

| コンポーネントID | 個別仕様書 | 対象コードパス (`target_files`) | 単一責務の定義 | 依存先コンポーネント |
| :--- | :--- | :--- | :--- | :--- |
| `[要記入: <id>]` | `[要記入: [<id>.md](../components/<id>.md)]` | `[要記入: src/...]` | `[要記入: 単一責任の定義]` | `[要記入: 依存先ID または -]` |

---

## 3. 外部境界 ＆ データフロー契約

<!-- @spec:data-flow -->

| 境界区分 | プロトコル / 形式 | 入出力対象・永続化ストア | バリデーション・変換契約 (`MUST`) |
| :--- | :--- | :--- | :--- |
| **外部入力** | `[要記入: CLI / HTTP / Event / File]` | `[要記入: 入力ソース・スキーマ]` | `[要記入: 境界での型・値域検証ルール]` |
| **コア処理** | `[要記入: 内部呼び出し / 非同期等]` | `[要記入: 主要コンポーネント間経路]` | `[要記入: トランザクション・状態遷移順序]` |
| **外部出力・永続化** | `[要記入: DB / File / API Response]` | `[要記入: 保存先・出力先]` | `[要記入: 永続化整合性・タイムアウト契約]` |
