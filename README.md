# AIDD テンプレートリポジトリ

**3層プロンプト構造**および**仕様書駆動開発（Specification-Driven Development: SDD）**に基づくAI駆動開発テンプレートリポジトリ。

---

## 1. クイックスタート

既存プロジェクトへの導入時、または新規プロジェクトの立ち上げ時に、AIエージェントへ以下のように指示してください（`BOOTSTRAP.md` のプロトコルが自動適用されます）：

```text
BOOTSTRAP.md の手順に従い、このプロジェクトに適合させた仕様書を生成して環境整備してください。
```

---

## 2. アーキテクチャ概要

### 2.1 3層構造と不変・可変の分離

| Layer | 配置 | ファイル | 区分 | 役割 |
| :---: | :--- | :--- | :---: | :--- |
| **0** | [AGENTS.md](AGENTS.md) | `AGENTS.md` | **不変** | AI行動規範・コンテキスト制御・安全境界 |
| **-** | `docs/` | [spec-router.md](docs/spec-router.md) | **自動生成（手動編集禁止）** | 全仕様書のルーティング索引・Mermaid依存グラフ |
| **1** | `docs/` | [core-rules.md](docs/core-rules.md), [components/_template.md](docs/components/_template.md) | **不変** | 共通エンジニアリング不可侵ルール・コンポーネント仕様スキーマ |
| **1** | `docs/` | `system/*.md`, `components/<id>.md` | **可変** | プロジェクト固有のシステム仕様（4分割）および個別コンポーネント仕様（1対1対応） |
| **2** | `.agents/skills/` | `workflow`, `local-workflow`, `ponytail`, `spec-verification`, `spec-to-readable-html` 他 | **不変** | 開発ワークフロー・静的検証・HTML変換等の実行スキル群 |

### 2.2 AI用SSOTと人間用Viewの分離

- **📄 Markdown (`docs/**/*.md`) — AI・機械検証用SSOT**:
  - AIのピンポイント参照効率と [`spec-verification`](.agents/skills/spec-verification/SKILL.md) による静的検証に最適化された、装飾・要約ゼロの高密度な契約正本。
- **🌐 HTML (`/spec-to-readable-html`) — 人間閲覧用View**:
  - 人間が仕様全体を低い認知負荷（要約カード・図解・色付きバッジ・目次サイドバー）で俯瞰したい場合は、`/spec-to-readable-html` スキルを実行して閲覧用HTMLをオンデマンド生成する（生成HTMLは `.gitignore` によりGit非追跡）。

---

## 3. 仕様書整合性の機械検証

仕様書（`docs/`）のFrontmatter・SSOT（`@spec`タグ一意性）・ルーティング全単射・単方向DAG・リンク実在性は、以下のコマンドで機械検証されます：

```bash
# テンプレート状態の構造検証
python .agents/skills/spec-verification/scripts/verify_specs.py

# Bootstrap完了後・実運用時の厳格検証（未記入残存ゼロ・1:1コンポーネント対応を含む）
python .agents/skills/spec-verification/scripts/verify_specs.py --strict
```
