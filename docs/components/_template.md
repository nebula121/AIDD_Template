---
spec_id: component-template
title: コンポーネント仕様書テンプレート
layer: 1
category: template
status: stable
target_files:
  - docs/components/*.md
dependencies:
  - core-rules
  - domain-rules
  - system-architecture
  - tech-stack
---
# コンポーネント仕様書テンプレート

<!-- @spec:component-template -->

`docs/components/<id>.md` の標準スキーマ正本。新規コンポーネント作成時は以下のFrontmatter・標準サブタグ・4セクション構造化表に厳密に従うこと (**MUST**)。

---

## Frontmatter ＆ 記述規約

<!-- @spec:component-template-schema -->

| 項目 | 規約 (`<id>` はファイル名 `<id>.md` の識別子) |
| :--- | :--- |
| **Frontmatter必須キー** | `spec_id: component-<id>`, `title: <コンポーネント名>`, `layer: 1`, `category: component`, `status: draft \| stable`, `target_files: [...]`, `dependencies: [core-rules, domain-rules, system-architecture, tech-stack, ...]` |
| **見出し1 (`#`) 規約** | Frontmatter の `title` と完全一致させる（括弧書きのファイル名や英訳は付けない）。 |
| **必須サブタグ（全5個）** | 冒頭: `component-<id>` / 第1章: `component-<id>-scope` / 第2章: `component-<id>-interface` / 第3章: `component-<id>-contract` / 第4章: `component-<id>-verification` |
| **受入条件の記述基準** | 曖昧な形容詞（「適切に」「安全に」「高速に」）の使用を禁じ、自動テストで100%機械判定可能な条件のみを記述する (**MUST**)。<br>❌ **Bad**: 不正な入力時は適切にエラー処理し、安全に終了すること。<br>✅ **Good**: 入力が空または256文字超過時、`ValidationError` を送出し、DB書き込み件数が `0` であること (**MUST**)。 |

---

## 1. 責務と境界

<!-- @spec:component-template-scope -->

| 区分 | 対象範囲・境界契約 (`MUST` / `MUST NOT`) |
| :--- | :--- |
| **対象範囲（単一責務）** | `<当該コンポーネントが担う中核責務を定義> (MUST)` |
| **対象外（非責務・委譲先）** | `<当該コンポーネントでは実装せず他コンポーネントへ委譲する処理を定義> (MUST NOT)` |

---

## 2. 公開インターフェース ＆ データ構造

<!-- @spec:component-template-interface -->

内部プライベート実装は記載せず、外部公開シンボル・API・主要データ構造のみを定義する (**MUST**)。

| 公開シンボル / エンドポイント | 入力（型・値域制約） | 出力（戻り値 / レスポンス型） | 事前条件・事後条件 |
| :--- | :--- | :--- | :--- |
| `<関数名 / クラス名 / API>` | `<引数名: 型, 制約>` | `<出力型>` | `<事前条件と完了後の保証状態>` |

---

## 3. ふるまい ＆ 異常系契約

<!-- @spec:component-template-contract -->

| 区分 | トリガー・入力条件 | 期待動作・送出エラー (`MUST`) | 状態不変・副作用保証 |
| :---: | :--- | :--- | :--- |
| **正常系** | `<有効入力・通常イベント>` | `<状態遷移・戻り値・永続化処理> (MUST)` | `<保証されるデータ整合性>` |
| **異常系** | `<境界値超過・不正入力・外部失敗>` | `<送出する具象例外型 / エラーコード> (MUST)` | `<状態変更なし / ロールバック保証> (MUST NOT)` |

---

## 4. 受入条件 ＆ 検証基準

<!-- @spec:component-template-verification -->

| 条件ID | シナリオ（前提・実行操作） | 期待される検証結果 (`MUST`) | 検証テストファイル / ケース |
| :--- | :--- | :--- | :--- |
| `AC-01` | `<前提状態と実行操作>` | `<アサートすべき具体的な出力・状態> (MUST)` | `<tests/test_<id>.py 等>` |
