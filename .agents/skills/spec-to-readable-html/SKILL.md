---
name: spec-to-readable-html
description: Transform Markdown or text specifications into human-readable HTML documents with cognitive unpacking (key takeaways, before/after comparisons, concrete scenarios, mandatory diagrams) and portal navigation. Optimized for 3-layer CQRS specification frameworks.
argument-hint: "[target] [lang]"
arguments: target, lang
---

# Spec to Readable HTML

This skill transforms formal, dense, and structured specifications (Markdown or plain text) into visually engaging, human-readable HTML documents optimized for quick comprehension, decision-making, and alignment.

It operates as the **Human Read-Only View** in a CQRS specification architecture (e.g., [nebula121/AIDD_Template](https://github.com/nebula121/AIDD_Template)). It does **not** perform literal Markdown-to-HTML conversion or lossy superficial summarization. Instead, it systematically applies **Cognitive Unpacking** to reveal the *intent*, *value*, and *concrete reality* behind abstract rules and schemas.

When invoked:
- `$target` sets the target specification file, directory, or scope (default: auto-detected from environment).
- `$lang` sets the output language (default: `ja`). If omitted, Japanese is used.

---

## Operating Modes

Before generating HTML, inspect the environment and arguments to choose the operating mode:

### 1. Portal Mode (`docs/html/index.html` + Multi-Spec Hierarchy)
- **Trigger**: When `docs/spec-router.md` exists in the repository, or when the user requests generating views for the full project / multiple specifications.
- **Output Structure**:
  - `docs/html/index.html` (Portal page: Hero, dependency DAG network diagram, role-based reading routes, specifications catalog table).
  - `docs/html/<relative-path-to-spec>.html` (Individual specification pages mirroring the source hierarchy, e.g., `docs/html/system/overview.html`).
- **Navigation Contract**:
  - Every generated page (including `index.html`) MUST include the shared top navigation bar (`.global-nav`).
  - `.global-nav` groups links hierarchically (e.g., `Home`, `Layer 1: Core`, `Layer 2: System`, `Layer 3: Components`) and marks the current page with `.active`.

### 2. Single Spec Mode (Single Portable HTML)
- **Trigger**: When a specific single specification file is targeted and portal mode is not requested.
- **Output Structure**:
  - A single self-contained HTML file (e.g., `<spec-name>.html` or `docs/html/<spec-name>.html`).
  - Contains `.global-nav` with home/relative navigation if part of a project, or standalone header if independent.

---

## Core Protocol: Cognitive Unpacking

Structured tables and RFC 2119 keywords (`MUST`, `MUST NOT`, `SHOULD`) are efficient for verification tools and AI parsers, but impose high cognitive load on human readers. When encountering formal contracts, tables, and rules, **unpack** them into human-friendly cognitive representations:

### 1. Key Takeaways (`.key-takeaway`) — Mandatory
- Always place a 3-bullet summary box immediately after the header/TOC.
- Summarize: (1) Core purpose/scope, (2) Most critical constraint or guarantee, (3) Key stakeholder outcome.

### 2. Visual Completeness (Mandatory Diagram) — Mandatory
- **Every specification page MUST contain at least one Mermaid diagram** (or inline SVG).
- Choose the diagram type that clarifies the core cognitive bottleneck:
  - System topology / Component relationships: `flowchart TD` or `graph TD`
  - Lifecycle / State transitions: `stateDiagram-v2`
  - Sequence / Protocol exchanges: `sequenceDiagram`
  - Data models / Entities: `erDiagram`
  - Multi-layer defense / Security boundaries: `flowchart LR` / `flowchart TD` with subgraphs
- Wrap diagrams in `<figure class="diagram-container"><div class="mermaid">...</div><figcaption>Caption</figcaption></figure>`.
- Use the base template's pan & zoom lightbox (click or `Enter`/`Space` to inspect complex diagrams).

### 3. Why & Before/After Comparison (`.comparison-grid`) — Mandatory
- Contrast the state **without** this specification against the state **with** it:
  - `.comparison-card--before`: Risks, ambiguities, vulnerabilities, or team friction absent this constraint.
  - `.comparison-card--after`: Guarantees, consistency, developer autonomy, and stability achieved with this specification.

### 4. Concrete Scenario Trace (`.scenario-box`) — Mandatory
- Anchor abstract types, APIs, or schemas with concrete, step-by-step example data.
- Clearly annotate non-normative or deduced examples with the `[Inferred]` or `[Example]` status badge.
- Number each step (`.scenario-step-num`) and show input/output payloads or execution effects.

### 5. Responsive Tables (`.table-responsive`) — Mandatory
- Every structured table (`.spec-table` or standard `table`) MUST be wrapped in `<div class="table-responsive">...</div>` to enable clean horizontal scrolling on narrow viewports without breaking page layout.

---

## Individual Specification Layout Standard

Follow this cognitive sequence for individual specification HTML documents:

```
1. Global Navigation (`.global-nav`)
2. Document Header (`.doc-header`: Title, Subtitle, Meta badges)
3. TOC Sidebar (`.toc`: Sticky on desktop, inline on mobile)
4. Key Takeaways (`.key-takeaway`: 3-bullet core summary)
5. Visual Architecture / Workflow (Mandatory Mermaid Diagram)
6. Why & Before/After Comparison (`.comparison-grid`: Before vs. After)
7. Public Interfaces & Contracts (`.table-responsive` > `.spec-table`)
8. Concrete Scenario Trace (`.scenario-box`: Step-by-step example)
9. Acceptance Criteria & Edge Cases (Tables with badges / Risk cards)
10. Source Traceability & Appendix (Mapping back to original Markdown / RFC tags)
11. Footer (`.doc-footer`: Generation metadata & copyright)
```

---

## Portal Page (`index.html`) Layout Standard

When in Portal Mode, generate `docs/html/index.html` with this structure:

```
1. Global Navigation (`.global-nav` with Home marked `.active`)
2. Hero Section (System Title, Architecture Vision, Last Updated, Status)
3. Architecture & Dependency Network (Interactive Mermaid DAG from spec-router.md)
4. Reading Paths by Role (`.reading-paths-grid` > `.reading-path-card`: e.g., Onboarding, Core Dev, Reviewer, Ops)
5. Specification Catalog (`.table-responsive` > `.spec-table` listing Layer, Title, Scope, Status, and Links)
6. System-wide Invariants & Core Constraints Summary
7. Footer
```

---

## Badges & Status Annotations

Maintain strict semantic distinctions using badges:

| Category | Class | Usage |
| :--- | :--- | :--- |
| **Requirement** | `.badge-must` / `.badge-should` / `.badge-could` / `.badge-wont` | RFC 2119 normative constraints |
| **Epistemic Status** | `.badge-confirmed` | Verified directly from source specification |
| | `.badge-inferred` / `.badge-assumption` | Deduced by AI / scenario examples (MUST NOT present as confirmed) |
| | `.badge-open` | Unresolved questions, missing decisions |
| **Risk / Severity** | `.badge-risk-high` / `.badge-risk-medium` / `.badge-risk-low` | Risk assessments and security impact |

---

## Security & Safety Guardrails

- **XSS Prevention**: Always escape user/source strings (`&amp;`, `&lt;`, `&gt;`, `&quot;`, `&#39;`). Never inject unsanitized HTML into content placeholders.
- **Traceability**: Never alter or drop normative RFC 2119 keywords or identifier names. Maintain explicit mapping to original `@spec:` tags or file headings in the traceability appendix.
- **Domain Neutrality**: Do not hardcode domain-specific concepts (e.g., medical, financial, specific app models) into this skill definition or templates. Keep all prompts, examples, and styles completely project-agnostic.

---

## Pre-Delivery Quality Checklist

Before finalizing any generated HTML document, verify:

- [ ] **Mode**: Correctly selected Portal Mode vs. Single Spec Mode.
- [ ] **Navigation**: `.global-nav` is present, correctly categorized, and highlights the current document as `.active`.
- [ ] **Key Takeaways**: `.key-takeaway` provides a clear 3-bullet executive summary at the top.
- [ ] **Visual Completeness**: Every page has at least one valid Mermaid diagram enclosed in `<figure class="diagram-container">`.
- [ ] **Before/After**: `.comparison-grid` clearly contrasts risks without the spec vs. value with it.
- [ ] **Scenario**: `.scenario-box` traces an end-to-end example with `[Inferred]` / `[Example]` badges.
- [ ] **Table Responsiveness**: Every table is wrapped in `.table-responsive`.
- [ ] **Integrity**: Mermaid syntax parses without syntax errors; Pan & Zoom modal functions properly.
