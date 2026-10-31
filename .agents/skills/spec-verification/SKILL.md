---
name: spec-verification
description: 仕様書群（AGENTS.mdおよびdocs/specs/配下）のYAML Frontmatter、SSOT（@specタグ一意性）、spec-router.mdとの完全同期、単方向DAG（循環参照ゼロ）、相対リンク実在、およびarchitecture.mdとdocs/specs/components/の1対1対応を機械検証するスキル。仕様書の作成・更新時および初期環境整備（Bootstrap）完了時に必ず実行すること。
---

# 仕様書整合性検証スキル

本スキルは、プロジェクトの仕様書正本（`AGENTS.md` および `docs/specs/**/*.md`）が 4層アーキテクチャ・SSOT・単方向DAG・1対1コンポーネント対応の不変条件を満たしているかを Python 標準ライブラリのみで高速・決定論的に機械検証する。

---

## 1. 実行タイミング

1. **日常の仕様書作成・更新時（必須）**:
   - `docs/specs/system/*.md`、`docs/specs/components/*.md`、`docs/specs/spec-router.md` を新規作成または編集した直後。
2. **初期環境整備（Bootstrap）完了時（必須）**:
   - `BOOTSTRAP.md` に基づく初期仕様書群の一括生成および `BOOTSTRAP.md` 自己削除の直後（`--strict` オプションを使用）。

---

## 2. 実行コマンドと検証モード

### 2.1 通常モード（テンプレート状態・構造検証 ＆ `--sync` 自動同期）
```bash
# ルーティング索引（docs/specs/spec-router.md）の自動同期・再生成
python .agents/skills/spec-verification/scripts/verify_specs.py --sync

# 静的検証のみ実行
python .agents/skills/spec-verification/scripts/verify_specs.py
```
- **検査内容**:
  1. **Frontmatter必須項目 ＆ 見出し1一致検証**: 全仕様書が必須5キー（`spec_id`, `title`, `status`, `target_files`, `dependencies`）のみを持ち（不要な旧 `layer` / `category` 等の余分なキーを含まず）、配置パスから Layer（`0`, `-`, `1`, `2`, `3`, `4`）が自動導出され、Frontmatter の `title` と本文の `# (H1)` が完全一致し、本文に主タグを含むこと。
  2. **SSOT（一意性）検証**: 全ファイル間で `spec_id` および `<!-- @spec:... -->` タグに重複が存在しないこと。
  3. **ルーティング全単射検証**: `docs/specs/spec-router.md` の登録エントリと、実在する仕様書集合（`AGENTS.md` + `docs/specs/**/*.md` ※`docs/tasks/` 除く）が過不足なく完全一致し、Layer・タイトル・主タグ・セクションサブタグ・`dependencies` が完全一致していること。
  4. **ドキュメントDAG検証**: `dependencies` に未定義の `spec_id` がなく、レイヤー逆流やルーティング索引への逆依存、閉路（循環参照）が存在しないこと。
  5. **リンク＆パス実在検証**: Markdown内の相対ファイルリンクがすべて実在し、`status: stable` な仕様書の `target_files` が実在パス／Globにマッチすること。
  6. **不変ファイル保護検証**: 不変ファイル4種（`AGENTS.md`, `docs/specs/core-rules.md`, `docs/specs/components/_template.md`, `docs/specs/usecases/_template.md`）が `status: stable` であり、未記入プレースホルダを含まないこと。

### 2.2 厳格モード（`--strict`：Bootstrap完了後・実プロジェクト運用時）
```bash
python .agents/skills/spec-verification/scripts/verify_specs.py --strict
```
- **追加検査内容**:
  7. **`BOOTSTRAP.md` ＆ `ref/` ステージング削除確認**: リポジトリルートおよび `ref/` 配下に初期整備・再適用用の `BOOTSTRAP.md`（テンプレート残骸）が残存していないこと。
  8. **未記入プレースホルダ残存ゼロ**: 全仕様書に `[要記入:`、`{{...}}`、`<!-- GUIDE:` 等のテンプレート残骸が残っていないこと。
  9. **コンポーネント1対1対応（全単射）検証**: `docs/specs/system/architecture.md` のコンポーネント表と `docs/specs/components/*.md`（`_template.md` 除く）が1対1で完全一致し、1件以上定義されており、各コンポーネント仕様書が必須4セクション構造を満たしていること。

---

## 3. エラー発生時の自己修復プロトコル

スクリプトが非ゼロ終了コード（Exit Code `1`）を返した場合は、出力された `[FAIL]` メッセージ（対象ファイル・違反内容）に従い、全項目が `[PASS]`（Exit Code `0`）になるまで仕様書または `docs/specs/spec-router.md` を修正して再実行すること (**MUST**)。
