# HTML Output Template Reference Guide

This guide defines the HTML markup patterns, component snippets, and document layouts for generating human-readable HTML specifications using `references/template.html`.

---

## 1. Component Reference & Snippets

### 1.1 Global Navigation (`.global-nav`) ＆ Breadcrumbs (`.breadcrumbs`)
Used across all pages. PC displays a sticky 52px single-row bar with layer dropdowns; mobile displays a 52px bar with a hamburger toggle button that expands an accordion menu. Followed immediately by `.breadcrumbs`.

```html
<nav class="global-nav">
  <div class="global-nav-inner">
    <a href="../index.html" class="nav-brand">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
      </svg>
      <span>Spec Portal</span>
    </a>

    <!-- PC Desktop Menu -->
    <ul class="nav-desktop-menu">
      <li class="nav-item"><a href="../index.html" class="nav-trigger">ホーム</a></li>
      <li class="nav-item">
        <button class="nav-trigger" type="button">
          <span>L0/L1 規範・憲法</span>
          <svg class="nav-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
        </button>
        <div class="nav-dropdown">
          <a href="../agents-guideline.html" class="nav-dropdown-item">
            <div class="nav-dropdown-title">AGENTS.md</div>
            <div class="nav-dropdown-desc">AIメタ行動規範</div>
          </a>
          <a href="../core-rules.html" class="nav-dropdown-item">
            <div class="nav-dropdown-title">core-rules.md</div>
            <div class="nav-dropdown-desc">システム不変条件</div>
          </a>
        </div>
      </li>
      <li class="nav-item">
        <button class="nav-trigger active" type="button">
          <span>L2 システム設計</span>
          <svg class="nav-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
        </button>
        <div class="nav-dropdown">
          <a href="overview.html" class="nav-dropdown-item active">
            <div class="nav-dropdown-title">overview.md ✓</div>
            <div class="nav-dropdown-desc">システム概要 ＆ スコープ</div>
          </a>
          <a href="architecture.html" class="nav-dropdown-item">
            <div class="nav-dropdown-title">architecture.md</div>
            <div class="nav-dropdown-desc">全体アーキテクチャ</div>
          </a>
          <a href="domain-rules.html" class="nav-dropdown-item">
            <div class="nav-dropdown-title">domain-rules.md</div>
            <div class="nav-dropdown-desc">ドメイン業務規則</div>
          </a>
          <a href="tech-stack.html" class="nav-dropdown-item">
            <div class="nav-dropdown-title">tech-stack.md</div>
            <div class="nav-dropdown-desc">技術スタック・検証環境</div>
          </a>
        </div>
      </li>
      <li class="nav-item">
        <button class="nav-trigger" type="button">
          <span>L3 コンポーネント</span>
          <svg class="nav-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
        </button>
        <div class="nav-dropdown">
          <a href="../components/component-a.html" class="nav-dropdown-item">
            <div class="nav-dropdown-title">component-a.md</div>
            <div class="nav-dropdown-desc">個別仕様正本（静的構造）</div>
          </a>
        </div>
      </li>
      <li class="nav-item">
        <button class="nav-trigger" type="button">
          <span>L4 ユースケース</span>
          <svg class="nav-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
        </button>
        <div class="nav-dropdown">
          <a href="../usecases/usecase-a.html" class="nav-dropdown-item">
            <div class="nav-dropdown-title">usecase-a.md</div>
            <div class="nav-dropdown-desc">ユースケース正本（動的振る舞い）</div>
          </a>
        </div>
      </li>
    </ul>

    <!-- Mobile Toggle Button -->
    <button class="nav-mobile-btn" type="button" onclick="toggleNav()">☰ メニュー</button>
  </div>

  <!-- Mobile Accordion Menu -->
  <div id="navCollapse" class="nav-mobile-collapse">
    <a href="../index.html" class="m-link" style="font-weight:700;">🏠 ポータルホーム</a>
    <div class="m-group-title">L0/L1 規範 ＆ 憲法</div>
    <a href="../agents-guideline.html" class="m-link">AGENTS.md</a>
    <a href="../core-rules.html" class="m-link">core-rules.md</a>
    <div class="m-group-title">L2 システム全体設計</div>
    <a href="overview.html" class="m-link current">overview.md ✓</a>
    <a href="architecture.html" class="m-link">architecture.md</a>
    <a href="domain-rules.html" class="m-link">domain-rules.md</a>
    <a href="tech-stack.html" class="m-link">tech-stack.md</a>
    <div class="m-group-title">L3 個別コンポーネント</div>
    <a href="../components/component-a.html" class="m-link">component-a.md</a>
    <div class="m-group-title">L4 ユースケース正本</div>
    <a href="../usecases/usecase-a.html" class="m-link">usecase-a.md</a>
  </div>
</nav>

<!-- Breadcrumbs Bar -->
<div class="breadcrumbs">
  <a href="../index.html">Portal</a>
  <span>/</span>
  <a href="overview.html">Layer 2: System</a>
  <span>/</span>
  <span class="curr">overview.html</span>
</div>
```

---

### 1.2 Key Takeaways (`.key-takeaway`)
3-bullet high-impact summary placed immediately after the header / TOC.

```html
<div class="key-takeaway">
  <div class="key-takeaway-title">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="12" cy="12" r="10"></circle>
      <polyline points="12 6 12 12 14 14"></polyline>
    </svg>
    <span>Key Takeaways (要点まとめ)</span>
  </div>
  <ul>
    <li><strong>責務と境界:</strong> コンポーネントXはデータ変換と検証に特化し、ストレージへの直接書き込みは行わない。</li>
    <li><strong>必須契約 (MUST):</strong> すべての外部リクエストはスキーマ検証を通過しなければならない。</li>
    <li><strong>成果・価値:</strong> 入力エラーの95%をインバウンド境界で遮断し、後続処理の耐障害性を向上させる。</li>
  </ul>
</div>
```

---

### 1.3 Why & Before/After Comparison (`.comparison-grid`)
Contrasts the system state without the specification against the state with it.

```html
<div class="comparison-grid">
  <div class="comparison-card comparison-card--before">
    <div class="comparison-header">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="15" y1="9" x2="9" y2="15"></line>
        <line x1="9" y1="9" x2="15" y2="15"></line>
      </svg>
      <span>Before (仕様なき場合のリスク)</span>
    </div>
    <div class="comparison-title">暗黙的な前提と分散した境界</div>
    <div class="comparison-body">
      <ul>
        <li>バリデーションルールが各エンドポイントに散在し、漏れや不整合が発生する。</li>
        <li>エラー時のフォールバック動作が未定義で、障害時に連鎖的なダウンタイムを招く。</li>
      </ul>
    </div>
  </div>

  <div class="comparison-card comparison-card--after">
    <div class="comparison-header">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
        <polyline points="22 4 12 14.01 9 11.01"></polyline>
      </svg>
      <span>After (本仕様による保証と価値)</span>
    </div>
    <div class="comparison-title">境界での一元集中検証と明確な契約</div>
    <div class="comparison-body">
      <ul>
        <li>Layer 1 境界で共通スキーマによる単一検証を実施し、不正データを即時拒絶する。</li>
        <li>RFC 2119 契約により各モジュールの責務が明文化され、独立した自律開発が可能になる。</li>
      </ul>
    </div>
  </div>
</div>
```

---

### 1.4 Concrete Scenario Trace (`.scenario-box`)
Step-by-step trace using concrete example data to illustrate abstract specifications.

```html
<div class="scenario-box">
  <div class="scenario-header">
    <div class="scenario-title">
      <span>実行シナリオ: 外部リクエストの正規化と検証フロー</span>
    </div>
    <span class="badge badge-inferred">[Example] 推論具象データ</span>
  </div>
  <div class="scenario-steps">
    <div class="scenario-step">
      <div class="scenario-step-num">1</div>
      <div class="scenario-step-content">
        <strong>クライアントからのペイロード受信:</strong> 未加工の JSON リクエストを受理する。
        <pre><code>{ "id": "req-1024", "action": "sync", "payload": { "val": 42 } }</code></pre>
      </div>
    </div>
    <div class="scenario-step">
      <div class="scenario-step-num">2</div>
      <div class="scenario-step-content">
        <strong>スキーマ検証とサニタイズ:</strong> 必須フィールドの存在と型適合性を検査する。
      </div>
    </div>
    <div class="scenario-step">
      <div class="scenario-step-num">3</div>
      <div class="scenario-step-content">
        <strong>ドメインエンティティへの変換と送出:</strong> 内部標準フォーマットへ変換し、処理パイプラインへ渡す。
        <pre><code>{ "trace_id": "req-1024", "status": "VALIDATED", "timestamp": "2026-10-26T00:00:00Z" }</code></pre>
      </div>
    </div>
  </div>
</div>
```

---

### 1.5 Reading Paths by Role (`.reading-paths-grid`)
Used on the Portal page (`index.html`) to guide different team members to their most relevant specifications.

```html
<div class="reading-paths-grid">
  <div class="reading-path-card">
    <div class="reading-path-role">Developer / 実装者</div>
    <div class="reading-path-title">新規機能実装・コンポーネント開発</div>
    <div class="reading-path-desc">アーキテクチャの境界制約とコンポーネント契約を理解するための最短ルート。</div>
    <ul class="reading-path-steps">
      <li>1. <a href="system/tech-stack.html">Tech Stack</a></li>
      <li>2. <a href="system/architecture.html">System Architecture</a></li>
      <li>3. <a href="components/skill-definition.html">Skill Definition</a></li>
    </ul>
  </div>

  <div class="reading-path-card">
    <div class="reading-path-role">Reviewer / アーキテクト</div>
    <div class="reading-path-title">整合性検証・設計レビュー</div>
    <div class="reading-path-desc">ドメインルールと不可侵制約（Core Rules）の遵守状況を確認する監査ルート。</div>
    <ul class="reading-path-steps">
      <li>1. <a href="core-rules.html">Core Rules</a></li>
      <li>2. <a href="system/domain-rules.html">Domain Rules</a></li>
      <li>3. <a href="system/architecture.html">System Architecture</a></li>
    </ul>
  </div>
</div>
```

---

### 1.6 Responsive Table Container (`.table-responsive`) ＆ Sticky Column (`.table-sticky-col`)
Wraps any structured specification table to ensure horizontal scrolling on narrow viewports with sticky header and scroll hint shadow. Adding `.table-sticky-col` freezes the first column (guarded with `max-width: 180px` and unwrapped on <=640px).

```html
<div class="table-responsive">
  <table class="spec-table table-sticky-col">
    <thead>
      <tr>
        <th>シンボル / メソッド</th>
        <th>入力型</th>
        <th>戻り値 / 状態</th>
        <th>制約レベル</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><code>executePipeline(ctx)</code></td>
        <td><code>PipelineContext</code></td>
        <td><code>Result&lt;Summary, Error&gt;</code></td>
        <td><span class="badge badge-must">MUST</span></td>
      </tr>
    </tbody>
  </table>
</div>
```

---

### 1.7 Diagrams with Lightbox Modal (`.diagram-container`)
Mandatory on every page. Constrained to `max-height: 520px` with a subtle static badge (Ponytail principle: no bounce or heavy animations). Supports pan, zoom, and fullscreen inspection.

```html
<figure class="diagram-container" tabindex="0">
  <div class="diagram-badge">🔍 拡大表示</div>
  <div class="mermaid">
flowchart TD
    Client["Client / Invoker"] --> Gateway["API Gateway / Boundary"]
    Gateway --> Pipeline["Execution Pipeline"]
    Pipeline --> Storage[("State / DB")]
  </div>
  <figcaption>図1: システムデータフローと実行境界</figcaption>
</figure>
```

---

### 1.8 Ancillary Components
- **Badges**: `.badge-must`, `.badge-should`, `.badge-confirmed`, `.badge-inferred`, `.badge-open`, `.badge-risk-high`
- **Status Badges**: `.badge-status.badge-status-stable`, `.badge-status.badge-status-draft`, `.badge-status.badge-status-deprecated`
- **Callouts (GitHub Alerts 5種)**:
  - NOTE (青): `.callout.callout-note` + Octicon Info SVG
  - TIP (緑): `.callout.callout-tip` + Octicon Lightbulb SVG
  - IMPORTANT (紫): `.callout.callout-important` + Octicon Report/Alert SVG
  - WARNING (橙): `.callout.callout-warning` + Octicon Triangle-alert SVG
  - CAUTION (赤): `.callout.callout-caution` + Octicon Stop SVG
- **Glossary**: `.glossary > .glossary-item > (.glossary-term, .glossary-def)`
- **Risk Cards**: `.risk-card.risk-card--high > (.risk-header, .risk-body)`
- **Directory Tree**: `.tree-view` (`white-space: pre`)

### 1.9 Collapsible TOC for Mobile (`.toc-details`)
Wraps the table of contents to provide accordion collapse on mobile (auto-closes on link click via minimal JS).

```html
<nav class="toc" aria-label="Table of contents">
  <details class="toc-details" open>
    <summary class="toc-summary">目次 (Table of Contents)</summary>
    <div class="toc-content">
      <div class="toc-title">Contents</div>
      <ol>
        <li><a href="#section-1">1. 要約</a></li>
        <li><a href="#section-2">2. アーキテクチャ</a></li>
      </ol>
    </div>
  </details>
</nav>
```

---

## 2. Portal Page (`docs/specs-html/index.html`) Recommended Structure

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>仕様書ポータル — プロジェクト仕様書体系</title>
  <!-- template.html CSS -->
</head>
<body>
  <!-- 1. Global Navigation -->
  <nav class="global-nav">...</nav>

  <!-- 2. Hero Header -->
  <header class="doc-header">
    <h1>仕様書ポータル (Specification Portal)</h1>
    <p class="subtitle">4層CQRSアーキテクチャに基づく仕様書ビジュアルネットワーク</p>
    <div class="doc-meta">
      <span class="doc-meta-item"><strong>Status:</strong> Stable</span>
      <span class="doc-meta-item"><strong>Updated:</strong> 2026-10-26</span>
    </div>
  </header>

  <div class="doc-layout" style="grid-template-columns: 1fr;">
    <main class="doc-main" style="max-width: 100%;">
      <!-- 3. Key Takeaways -->
      <section>
        <div class="key-takeaway">...</div>
      </section>

      <!-- 4. Architecture & Dependency Network (Mermaid) -->
      <section>
        <h2>1. 仕様書依存ネットワークマップ</h2>
        <figure class="diagram-container">
          <div class="mermaid">
            <!-- Mermaid DAG from spec-router.md -->
          </div>
          <figcaption>仕様書間単方向依存グラフ (DAG)</figcaption>
        </figure>
      </section>

      <!-- 5. Reading Paths by Role -->
      <section>
        <h2>2. ロール別推奨読書ルート</h2>
        <div class="reading-paths-grid">...</div>
      </section>

      <!-- 6. Specification Catalog -->
      <section>
        <h2>3. 仕様書カタログ一覧</h2>
        <div class="table-responsive">
          <table class="spec-table">
            <thead>
              <tr>
                <th>Layer</th>
                <th>仕様書</th>
                <th>タイトル</th>
                <th>ステータス</th>
                <th>対象ファイル</th>
              </tr>
            </thead>
            <tbody>
              <!-- Catalog rows with links -->
            </tbody>
          </table>
        </div>
      </section>
    </main>
  </div>
  <!-- template.html Footer & Modal Scripts -->
</body>
</html>
```

---

## 3. Individual Specification Page Recommended Structure

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>{{TITLE}} — 仕様書</title>
  <!-- template.html CSS -->
</head>
<body>
  <!-- 1. Global Navigation -->
  <nav class="global-nav">...</nav>

  <!-- 2. Header -->
  <header class="doc-header">
    <h1>{{TITLE}}</h1>
    <p class="subtitle">{{SUBTITLE}}</p>
    <div class="doc-meta">
      <span class="doc-meta-item"><strong>Status:</strong> <span class="badge-status badge-status-{{STATUS_CLASS}}">{{STATUS}}</span></span>
      <span class="doc-meta-item"><strong>Spec ID:</strong> {{SPEC_ID}}</span>
      <span class="doc-meta-item"><strong>Target:</strong> <code>{{TARGET_FILES}}</code></span>
      <span class="doc-meta-item"><strong>Dependencies:</strong> {{DEPENDENCIES}}</span>
    </div>
  </header>

  <div class="doc-layout">
    <!-- 3. TOC Sidebar -->
    <aside class="toc">...</aside>

    <!-- 4. Main Content -->
    <main class="doc-main">
      <!-- 4.1 Key Takeaways (Mandatory) -->
      <div class="key-takeaway">...</div>

      <!-- 4.2 Mandatory Diagram -->
      <section id="architecture">
        <h2>1. 構造・ワークフロー図解</h2>
        <figure class="diagram-container">
          <div class="mermaid">...</div>
          <figcaption>図1: コンポーネント構造と処理パイプライン</figcaption>
        </figure>
      </section>

      <!-- 4.3 Why & Before/After (Mandatory) -->
      <section id="why-and-comparison">
        <h2>2. 背景 ＆ 導入効果（Before / After）</h2>
        <div class="comparison-grid">...</div>
      </section>

      <!-- 4.4 Public Interfaces & Contracts -->
      <section id="interfaces">
        <h2>3. 公開インターフェース ＆ 契約</h2>
        <div class="table-responsive">
          <table class="spec-table">...</table>
        </div>
      </section>

      <!-- 4.5 Concrete Scenario Trace (Mandatory) -->
      <section id="scenario">
        <h2>4. 具象実行シナリオ</h2>
        <div class="scenario-box">...</div>
      </section>

      <!-- 4.6 Acceptance Criteria & Verification -->
      <section id="verification">
        <h2>5. 受入条件 ＆ 検証基準</h2>
        <div class="table-responsive">
          <table class="spec-table">...</table>
        </div>
      </section>

      <!-- 4.7 Source Traceability -->
      <section id="traceability">
        <h2>6. 元仕様トレーサビリティ</h2>
        <p>Source Spec: <a href="../../docs/...">docs/...</a> (Tag: <code>@spec:...</code>)</p>
      </section>
    </main>
  </div>
  <!-- template.html Footer & Modal Scripts -->
</body>
</html>
```
