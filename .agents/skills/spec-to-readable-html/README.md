# Spec to Readable HTML

Markdown / テキストの仕様書を、**認知展開（Cognitive Unpacking）・図解・トレーサビリティ付きの「人間向けビジュアル HTML ドキュメント」**へ変換する [Agent Skill](https://github.com/vercel-labs/skills) です。

[nebula121/AIDD_Template](https://github.com/nebula121/AIDD_Template) をはじめとする 3層CQRS仕様書体系における **Human Read-Only View** 生成スキルとして最適化されています。単なる Markdown &rarr; HTML 変換や表層的な要約ではなく、形式知化された規則や表の背景にある「設計の意図」「導入価値」「具象データ」を紐解き、人間の迅速な理解と合意形成を支援します。

---

## 主な特長

### 1. Cognitive Unpacking（認知展開プロトコル）
- **Key Takeaways (冒頭3行まとめ)**: 仕様書の要点を3行で抽出し、最上部にハイライト表示（`.key-takeaway`）。
- **Why ＆ Before/After 比較**: 「制約がない場合のリスク（Before）」と「本仕様による保証と価値（After）」を直感的な対比カードで可視化（`.comparison-grid`）。
- **具象シナリオトレース**: 抽象的な型や状態遷移を、実例データとステップ番号で具体化（`.scenario-box`）。補足・推論箇所には `[Inferred]` / `[Example]` バッジを明記。

### 2. Visual Completeness（図解の必須化）
- すべての仕様書ページに最低1つの Mermaid 図解（システム構造、多重防御、状態遷移、パイプライン等）を必ず配置。
- 拡大・縮小・パン移動が可能なライトボックスモーダル（Pan & Zoom）を標準搭載。

### 3. ポータルモード ＆ 単一仕様書モード
- **ポータルモード**: `docs/spec-router.md` がある環境や全体指定時は、`docs/html/index.html`（DAGネットワーク図、ロール別読書順、カタログ表）と各仕様書 HTML を一括生成。全ページ共通の階層ナビゲーションバー（`.global-nav`）でシームレスに行き来可能。
- **単一仕様書モード**: 特定の1ファイルのみをピンポイントで変換可能。

### 4. レスポンシブ組版 ＆ ポータビリティ
- 幅広テーブルを横スクロールさせるコンテナ（`.table-responsive`）により、画面崩れを防止。
- CSS は単一ファイルへ埋め込み。Mermaid CDN を標準利用しつつ、オフライン/完全自己完結を要求された場合は inline SVG にフォールバック可能。

---

## インストール

[`npx skills`](https://github.com/vercel-labs/skills) を使う場合:

```bash
npx skills add nebula121/spec-to-readable-html
```

または、`SKILL.md` と `references/` をエージェントのスキルディレクトリ（`~/.claude/skills/spec-to-readable-html/` やプロジェクトの `.agents/skills/spec-to-readable-html/` など）に配置してください。

---

## 使い方

エージェント環境（Antigravity, Claude Code 等）で仕様書を指定し、本スキルを呼び出します。

```
# 全体ポータルおよび仕様書群を生成（ポータルモード）
/spec-to-readable-html

# 特定の仕様書のみを生成（単一仕様書モード）
/spec-to-readable-html docs/components/my-component.md

# 言語を指定して生成（既定: ja）
/spec-to-readable-html docs/system/overview.md en
```

---

## 出力テンプレートとカスタマイズ

`references/template.html` をベース HTML として使用します。
スタイルや配色はデザイントークンとして整理されているため、プロジェクトのブランドに合わせて容易に変更できます。

- **配色**: `:root` の `--color-*` トークンを変更
- **ロゴ**: `{{LOGO}}` に `<svg>` や `<img>` を差し込み（不要なら削除可）
- **マークアップ見本**: [references/html-output-template.md](references/html-output-template.md) を参照

---

## ライセンス

[MIT](./LICENSE) © 2026 KeMezz
