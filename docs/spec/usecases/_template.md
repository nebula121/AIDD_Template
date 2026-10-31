---
spec_id: usecase-template
title: ユースケース仕様書テンプレート
status: stable
target_files:
  - docs/spec/usecases/*.md
dependencies:
  - core-rules
  - domain-rules
  - system-architecture
  - tech-stack
---
# ユースケース仕様書テンプレート

<!-- @spec:usecase-template -->

`docs/spec/usecases/<id>.md` の標準スキーマ正本。新規ユースケース作成時は以下のFrontmatter・標準サブタグ・5セクション構造化表に厳密に従うこと (**MUST**)。

---

## Frontmatter ＆ 記述規約

<!-- @spec:usecase-template-schema -->

| 項目 | 規約 (`<id>` はファイル名 `<id>.md` の識別子) |
| :--- | :--- |
| **Frontmatter必須キー** | `spec_id: usecase-<id>`, `title: <ユースケース名>`, `status: draft \| stable`, `target_files: [...]`（※通常は関連テストまたは関連コード）, `dependencies: [core-rules, domain-rules, system-architecture, component-<dep1>, component-<dep2>, ...]`（※Layer 4は配置パスから自動導出） |
| **見出し1 (`#`) 規約** | Frontmatter の `title` と完全一致させる（括弧書きのファイル名や英訳は付けない）。 |
| **必須サブタグ（全6個）** | 冒頭: `usecase-<id>` / 第1章: `usecase-<id>-overview` / 第2章: `usecase-<id>-sequence` / 第3章: `usecase-<id>-scenarios` / 第4章: `usecase-<id>-state` / 第5章: `usecase-<id>-verification` |
| **シナリオ記述基準** | Given（前提・初期状態）、When（契機・アクター操作）、Then（結果・副作用）の3要素で記述し、E2E/結合テストで100%機械検証可能な受入条件とする (**MUST**)。 |

---

## 1. ユースケース概要 ＆ アクター

<!-- @spec:usecase-template-overview -->

| 項目 | 定義内容 (`MUST`) |
| :--- | :--- |
| **主要アクター / トリガー** | `<エンドユーザー / 外部システム / 定期実行Cron 等>` |
| **達成するビジネスゴール** | `<本シナリオの完了により提供される業務価値・達成状態>` |
| **前提条件 (Pre-conditions)** | `<シナリオ実行前に満たされているべきシステム状態・権限>` |
| **事後条件 (Post-conditions)** | `<シナリオ正常完了後に永続化・保証されるシステム状態>` |

---

## 2. 協調コンポーネント ＆ シーケンス

<!-- @spec:usecase-template-sequence -->

本ユースケースを構成する Layer 3 コンポーネント群と、呼び出し順序・メッセージフローの定義。

```mermaid
sequenceDiagram
    autonumber
    actor Actor as <アクター>
    participant Entry as <エントリポイント>
    participant CompA as <コンポーネントA>
    participant CompB as <コンポーネントB>

    Actor->>Entry: <操作実行>
    Entry->>CompA: <メソッド呼出>
    CompA->>CompB: <協調呼出>
    CompB-->>Entry: <処理結果>
    Entry-->>Actor: <完了レスポンス>
```

| ステップ | 呼出元 (Caller) | 呼出先 (Callee: Layer 3) | 契約・実行内容 | 失敗時ハンドリング |
| :---: | :--- | :--- | :--- | :--- |
| 1 | `<呼び出し元>` | `<呼び出し先コンポーネント>` | `<メソッド / API呼出>` | `<例外捕捉 / ロールバック>` |

---

## 3. シナリオ受入条件 (Given / When / Then)

<!-- @spec:usecase-template-scenarios -->

| シナリオID | シナリオ種別 | Given (前提条件) | When (実行契機・入力) | Then (期待結果・副作用) (`MUST`) |
| :--- | :---: | :--- | :--- | :--- |
| `SC-01` | **正常系** | `<前提状態（データ、ログイン等）>` | `<ユーザー操作・リクエスト送信>` | `<正常レスポンス・DB永続化・イベント発行> (MUST)` |
| `SC-02` | **異常系** | `<前提状態>` | `<不正入力・リソース枯渇・外部失敗>` | `<エラーレスポンス・状態不変/ロールバック> (MUST)` |
| `SC-03` | **代替系** | `<特定条件下>` | `<代替操作>` | `<代替フロー完了・期待状態> (MUST)` |

---

## 4. 状態遷移 ＆ 補償トランザクション

<!-- @spec:usecase-template-state -->

| 区分 | 遷移前状態 | 契機イベント | 遷移後状態 | 補償・ロールバック契約 (`MUST`) |
| :--- | :--- | :--- | :--- | :--- |
| **成功時遷移** | `<初期ステータス>` | `<正常完了>` | `<最終ステータス>` | - |
| **失敗時補償** | `<中間ステータス>` | `<途中エラー / タイムアウト>` | `<復帰ステータス>` | `<外部呼出取消・DB補償更新> (MUST)` |

---

## 5. 検証手順 ＆ テスト対応

<!-- @spec:usecase-template-verification -->

| シナリオID | 検証種別 | テストコードパス | 検証コマンド (`tech-stack.md` 準拠) |
| :--- | :---: | :--- | :--- |
| `SC-01` | E2E / 統合 | `<tests/integration/... 等>` | `<pytest / npm test 等>` |
| `SC-02` | 異常系結合 | `<tests/integration/... 等>` | `<pytest / npm test 等>` |
