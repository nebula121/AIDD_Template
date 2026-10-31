---
spec_id: core-rules
title: コア不可侵ルール
status: stable
target_files:
  - "**/*"
dependencies:
  - agents-guideline
---
# コア不可侵ルール

<!-- @spec:core-rules -->

全仕様書の規範キーワード（`MUST`, `MUST NOT`, `SHOULD`, `MAY`）は RFC 2119 に従う。システム固有の業務不変条件は [system/domain-rules.md](system/domain-rules.md) を正本とする。

---

## 1. アーキテクチャ ＆ セキュリティ不可侵境界

<!-- @spec:architecture-and-security-rules -->

| 領域 | 不可侵ルール契約 (`MUST` / `MUST NOT`) | 機械的検証基準 |
| :--- | :--- | :--- |
| **単方向依存** | モジュール・コンポーネント間の依存は単方向（DAG）とし、循環参照を発生させてはならない (**MUST NOT**)。コアロジックは外部I/O・具象インフラに直接依存してはならない (**MUST NOT**)。 | 静的解析・Linterで循環インポートが `0` 件であること。 |
| **仕様1対1同期** | [system/architecture.md](system/architecture.md) のコンポーネント表と `docs/spec/components/<id>.md` は1対1（全単射）で対応させなければならない (**MUST**)。 | `verify_specs.py --strict` が Exit Code `0` で通過すること。 |
| **シークレット外部化** | 認証情報（APIキー・秘密鍵・トークン・パスワード）は環境変数またはシークレットマネージャ経由でのみ読み出す (**MUST**)。コード・設定・仕様・コミットへの平文記載を禁じる (**MUST NOT**)。 | 正規表現 `(?i)(api[_-]?key\|secret\|password\|token)\s*[:=]\s*['"][a-zA-Z0-9_\-]{8,}['"]` の検知が `0` 件であること。 |
| **テストデータ隔離** | 全自動テストは隔離領域（`tmp_path`・インメモリDB・一時ディレクトリ）で実行し、終了時に自動破棄（Teardown）する (**MUST**)。実データ・DB・ローカル設定ファイルを汚染・改変・消去してはならない (**MUST NOT**)。 | テスト実行前後で実データ領域および設定ファイルのハッシュ・ファイル構成に差分が発生しないこと（差分ゼロ）。 |
| **Git履歴保護** | バージョン管理は前進的追記（Forward-only）を維持する (**MUST**)。事前合意なき `git push --force` (`-f`) 等の履歴改変・消去を禁じる (**MUST NOT**)。 | 自動化スクリプト・実行履歴に未承認の `--force` / `-f` 操作が含まれないこと。 |

---

## 2. 仕様ステータス別の変更制御マトリクス

<!-- @spec:lifecycle-and-test-rules -->

| 対象ステータス | 破壊的変更（公開IF・スキーマ刷新・削除） | 下位互換レイヤー・移行アダプタ作成 | 改定プロトコル・検証基準 |
| :--- | :--- | :--- | :--- |
| **`status: draft`**<br>（試作・仕様未作成） | **SHOULD**: Ponytail原則に従い、より単純な設計へ躊躇なく刷新・削除する。 | **MUST NOT**: 将来の技術的負債となるため作成禁止。 | 互換ラッパーを残さず、旧コード・旧定義が完全に除去されていること。 |
| **`status: stable`**<br>（確定・保護対象） | **MUST NOT**: 無断での破壊的変更、およびエラー回避目的のサイレント改変を禁じる。 | **MUST NOT**: 仕様合意なき回避実装・暫定ラッパー作成を禁じる。 | **MUST**: 事前に理由と影響を提示して承認を得てから仕様書（`docs/spec/system/*.md`, `docs/spec/components/*.md`）の改定を先行させる。 |