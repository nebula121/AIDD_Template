#!/usr/bin/env python3
"""Deterministic static verifier and synchronizer for AIDD/SDD specifications."""

import argparse
import glob
import os
import re
import sys
from pathlib import Path

REQUIRED_FRONTMATTER_KEYS = {
    "spec_id",
    "title",
    "status",
    "target_files",
    "dependencies",
}

IMMUTABLE_FILES = [
    "AGENTS.md",
    "docs/core-rules.md",
    "docs/components/_template.md",
]

PLACEHOLDER_PATTERNS = [
    (r"\[要記入:", "Unfilled placeholder '[要記入: ...]'"),
    (r"\{\{[A-Za-z0-9_]+\}\}", "Unreplaced template token '{{...}}'"),
    (r"<!--\s*GUIDE:", "Unremoved template guide comment '<!-- GUIDE: ... -->'"),
]

LAYER_ORDER = {0: 0, "-": 1, 1: 2, 2: 3, 3: 4}


def infer_layer_from_path(rel_path: str) -> int | str | None:
    """Deterministically infer specification layer from repository-relative POSIX path."""
    if rel_path == "AGENTS.md":
        return 0
    if rel_path == "docs/spec-router.md":
        return "-"
    if rel_path == "docs/core-rules.md":
        return 1
    if rel_path.startswith("docs/system/"):
        return 2
    if rel_path.startswith("docs/components/"):
        return 3
    return None

DAG_START_MARKER = "<!-- @generated:spec-dag-start -->"
DAG_END_MARKER = "<!-- @generated:spec-dag-end -->"
TABLE_START_MARKER = "<!-- @generated:spec-table-start -->"
TABLE_END_MARKER = "<!-- @generated:spec-table-end -->"


def find_repo_root() -> Path:
    """Find repository root by looking for .git or AGENTS.md in parents."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / ".git").exists() or (parent / "AGENTS.md").exists():
            return parent
    return Path.cwd()


def normalize_text(text: str) -> str:
    """Normalize CRLF to LF for cross-platform deterministic comparison."""
    return text.replace("\r\n", "\n")


def parse_simple_yaml_frontmatter(text: str, rel_path: str, errors: list[str]) -> tuple[dict, str]:
    """Parse YAML frontmatter without external dependencies."""
    norm_text = normalize_text(text)
    if not norm_text.startswith("---\n"):
        errors.append(f"{rel_path}: Missing YAML frontmatter opening '---' at line 1.")
        return {}, norm_text

    lines = norm_text.splitlines()
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        errors.append(f"{rel_path}: Missing YAML frontmatter closing '---'.")
        return {}, norm_text

    fm_lines = lines[1:end_idx]
    body = "\n".join(lines[end_idx + 1 :])
    data: dict = {}
    current_list_key: str | None = None

    for raw_line in fm_lines:
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if stripped.startswith("- ") and current_list_key is not None:
            item = stripped[2:].strip().strip("'\"")
            data[current_list_key].append(item)
            continue

        if ":" in stripped:
            key, val = stripped.split(":", 1)
            key = key.strip()
            val = val.strip()
            if val == "":
                data[key] = []
                current_list_key = key
            elif val.startswith("[") and val.endswith("]"):
                inner = val[1:-1].strip()
                if not inner:
                    data[key] = []
                else:
                    data[key] = [
                        x.strip().strip("'\"") for x in inner.split(",") if x.strip()
                    ]
                current_list_key = None
            else:
                clean_val = val.strip("'\"")
                if clean_val.isdigit():
                    data[key] = int(clean_val)
                else:
                    data[key] = clean_val
                current_list_key = None
        else:
            errors.append(f"{rel_path}: Invalid frontmatter line: '{raw_line}'")

    return data, body


def strip_code_and_comments(markdown_text: str) -> str:
    """Remove fenced code blocks, HTML comments, and inline code for link scanning."""
    text = re.sub(r"```[\s\S]*?```", "", markdown_text)
    text = re.sub(r"<!--[\s\S]*?-->", "", text)
    text = re.sub(r"`[^`\n]+`", "", text)
    return text


def check_relative_links(root: Path, rel_path: str, text: str, errors: list[str]) -> None:
    """Verify all relative markdown file links exist on disk."""
    cleaned = strip_code_and_comments(text)
    base_dir = (root / rel_path).parent
    for match in re.finditer(r"!?\[[^\]]*\]\(([^)]+)\)", cleaned):
        raw_target = match.group(1).strip()
        if (
            not raw_target
            or raw_target.startswith("#")
            or "://" in raw_target
            or raw_target.startswith("mailto:")
        ):
            continue
        path_part = raw_target.split("#", 1)[0].strip()
        if not path_part:
            continue
        resolved = (base_dir / path_part).resolve()
        if not resolved.exists():
            errors.append(
                f"{rel_path}: Broken relative link '({raw_target})' -> target does not exist."
            )


def collect_spec_files(root: Path) -> list[str]:
    """Return sorted relative POSIX paths of AGENTS.md and all docs/**/*.md (excluding docs/tasks/)."""
    files = []
    if (root / "AGENTS.md").exists():
        files.append("AGENTS.md")
    docs_dir = root / "docs"
    if docs_dir.exists():
        for p in sorted(docs_dir.rglob("*.md")):
            rel = p.relative_to(root).as_posix()
            if rel.startswith("docs/tasks/"):
                continue
            files.append(rel)
    return files


def check_dag_cycles(specs_by_id: dict[str, dict], errors: list[str]) -> None:
    """Verify dependency references exist, respect layer order, forbid reverse-dependency to router index, and form a valid DAG."""
    for spec_id, meta in specs_by_id.items():
        src_layer = meta.get("layer", 0)
        for dep_id in meta.get("dependencies", []):
            if dep_id not in specs_by_id:
                errors.append(
                    f"{meta['path']}: Unknown dependency spec_id '{dep_id}' in frontmatter."
                )
                continue

            dep_meta = specs_by_id[dep_id]
            dep_layer = dep_meta.get("layer", 0)

            # Specification files MUST NOT depend on the router index (Layer '-')
            if dep_id == "spec-router" or dep_layer == "-":
                errors.append(
                    f"{meta['path']}: Spec files cannot depend on router index '{dep_id}' (Layer '-')."
                )
                continue

            # Layer order check: higher layer cannot depend on lower layer (e.g. Layer 2 cannot depend on Layer 3)
            if isinstance(src_layer, int) and isinstance(dep_layer, int):
                if dep_layer > src_layer:
                    errors.append(
                        f"{meta['path']}: Layer inversion in DAG: layer {src_layer} ('{spec_id}') "
                        f"cannot depend on lower layer {dep_layer} ('{dep_id}')."
                    )

    # 0 = unvisited, 1 = visiting, 2 = visited
    state: dict[str, int] = {k: 0 for k in specs_by_id}
    path_stack: list[str] = []

    def dfs(node: str) -> None:
        state[node] = 1
        path_stack.append(node)
        for dep in specs_by_id[node].get("dependencies", []):
            if dep not in specs_by_id:
                continue
            if state[dep] == 1:
                cycle_start = path_stack.index(dep)
                cycle_chain = " -> ".join(path_stack[cycle_start:] + [dep])
                errors.append(f"Document DAG cycle detected: {cycle_chain}")
            elif state[dep] == 0:
                dfs(dep)
        path_stack.pop()
        state[node] = 2

    for node in specs_by_id:
        if state[node] == 0:
            dfs(node)


def generate_mermaid_dag(specs_by_id: dict[str, dict]) -> str:
    """Generate deterministic Mermaid flowchart grouped by layers."""
    layers_def = [
        (0, "L0", "Layer 0: Meta Guideline"),
        (1, "L1", "Layer 1: Core Rules"),
        (2, "L2", "Layer 2: System Architecture"),
        (3, "L3", "Layer 3: Components"),
    ]
    lines = ["```mermaid", "flowchart TD"]

    for layer_num, sg_id, sg_title in layers_def:
        layer_specs = [
            meta for meta in specs_by_id.values() if meta.get("layer") == layer_num
        ]
        if not layer_specs:
            continue
        layer_specs.sort(key=lambda m: m["path"])
        lines.append(f'    subgraph {sg_id}["{sg_title}"]')
        for meta in layer_specs:
            sid = meta["spec_id"]
            disp_path = meta["path"]
            if disp_path.startswith("docs/"):
                disp_path = disp_path[5:]
            lines.append(f'        {sid}["{disp_path}"]')
        lines.append("    end")

    # Dependency edges
    edges: list[tuple[str, str]] = []
    for spec_id, meta in specs_by_id.items():
        if meta.get("layer") == "-":
            continue
        for dep_id in meta.get("dependencies", []):
            if dep_id in specs_by_id and specs_by_id[dep_id].get("layer") != "-":
                edges.append((spec_id, dep_id))

    edges.sort()
    for src, dst in edges:
        lines.append(f"    {src} --> {dst}")

    lines.append("```")
    return "\n".join(lines)


def generate_routing_table(root: Path, specs_by_path: dict[str, dict]) -> str:
    """Generate deterministic Markdown table for docs/spec-router.md."""
    lines = [
        "| Layer | 仕様書 | タイトル | 主タグ | セクションサブタグ | 対象スコープ | 依存仕様 |",
        "| :---: | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    router_dir = root / "docs"

    sorted_specs = sorted(
        specs_by_path.values(),
        key=lambda m: (LAYER_ORDER.get(m["layer"], 99), m["path"]),
    )

    for meta in sorted_specs:
        layer_str = f"**{meta['layer']}**"

        # Compute relative link from docs/ to file
        target_path = root / meta["path"]
        try:
            rel_link = os.path.relpath(target_path, router_dir).replace("\\", "/")
        except ValueError:
            rel_link = meta["path"]
        name = target_path.name if meta["path"] != "AGENTS.md" else "AGENTS.md"
        if meta["path"].startswith("docs/system/") or meta["path"].startswith("docs/components/"):
            name = meta["path"][5:]
        spec_link = f"[{name}]({rel_link})"

        title_str = meta.get("title", "").strip()

        primary_tag = f"`@spec:{meta['spec_id']}`"

        # Subtags
        subtags = meta.get("subtags", [])
        if subtags:
            clean_subtags = [t.removeprefix("@spec:") for t in subtags]
            clean_subtags.sort()
            subtags_str = ", ".join(f"`{t}`" for t in clean_subtags)
        else:
            subtags_str = "-"

        # Scopes (target_files)
        target_files = meta.get("target_files", [])
        if target_files:
            scopes_str = ", ".join(f"`{tf}`" for tf in target_files)
        else:
            scopes_str = "-"

        # Dependencies
        deps = meta.get("dependencies", [])
        if deps:
            deps_str = ", ".join(f"`{d}`" for d in deps)
        else:
            deps_str = "-"

        lines.append(
            f"| {layer_str} | {spec_link} | {title_str} | {primary_tag} | {subtags_str} | {scopes_str} | {deps_str} |"
        )

    return "\n".join(lines)


def replace_slot(
    text: str, start_marker: str, end_marker: str, replacement: str, errors: list[str], rel_path: str
) -> str:
    """Safely replace content between start_marker and end_marker using string slicing."""
    s_idx = text.find(start_marker)
    e_idx = text.find(end_marker)
    if s_idx == -1 or e_idx == -1 or s_idx >= e_idx:
        errors.append(
            f"{rel_path}: Missing or malformed marker pair '{start_marker}' ... '{end_marker}'."
        )
        return text
    after_start = s_idx + len(start_marker)
    return text[:after_start] + "\n" + replacement + "\n" + text[e_idx:]


def sync_or_verify_spec_router(
    root: Path,
    specs_by_path: dict[str, dict],
    specs_by_id: dict[str, dict],
    sync: bool,
    errors: list[str],
) -> None:
    """Synchronize or verify that docs/spec-router.md matches generated DAG and routing table."""
    router_path = root / "docs" / "spec-router.md"
    rel_path = "docs/spec-router.md"
    if not router_path.exists():
        errors.append(f"{rel_path}: Missing required routing index file.")
        return

    raw_bytes = router_path.read_bytes()
    line_ending = "\r\n" if b"\r\n" in raw_bytes else "\n"
    current_text = normalize_text(raw_bytes.decode("utf-8"))

    expected_dag = generate_mermaid_dag(specs_by_id)
    expected_table = generate_routing_table(root, specs_by_path)

    temp_errors: list[str] = []
    text_with_dag = replace_slot(
        current_text, DAG_START_MARKER, DAG_END_MARKER, expected_dag, temp_errors, rel_path
    )
    expected_full_text = replace_slot(
        text_with_dag, TABLE_START_MARKER, TABLE_END_MARKER, expected_table, temp_errors, rel_path
    )

    if temp_errors:
        errors.extend(temp_errors)
        return

    if sync:
        router_path.write_text(expected_full_text, encoding="utf-8", newline=line_ending)
        print(f"Synchronized {rel_path} successfully (Mermaid DAG & Routing table).")
    else:
        if current_text != expected_full_text:
            errors.append(
                f"{rel_path}: Router DAG or routing table is out of sync with spec frontmatters. "
                f"Run 'python .agents/skills/spec-verification/scripts/verify_specs.py --sync' to update."
            )


def verify_strict_mode(root: Path, spec_files: list[str], errors: list[str]) -> None:
    """Perform strict post-bootstrap checks: no BOOTSTRAP.md, no placeholders, 1:1 component map."""
    if (root / "BOOTSTRAP.md").exists():
        errors.append(
            "BOOTSTRAP.md: File still exists in root. Delete BOOTSTRAP.md upon completing bootstrap."
        )
    ref_dir = root / "ref"
    if ref_dir.exists():
        for leftover in sorted(ref_dir.rglob("BOOTSTRAP.md")):
            rel_leftover = leftover.relative_to(root).as_posix()
            errors.append(
                f"{rel_leftover}: Template directory still exists in ref/. Delete the staged template in ref/ upon completion."
            )

    check_files = list(spec_files)
    if (root / "README.md").exists():
        check_files.append("README.md")

    for rel_path in check_files:
        content = normalize_text((root / rel_path).read_text(encoding="utf-8"))
        for pat, desc in PLACEHOLDER_PATTERNS:
            if re.search(pat, content):
                errors.append(f"{rel_path}: {desc} found in --strict mode.")

    # Verify 1:1 mapping between docs/system/architecture.md table and docs/components/*.md
    arch_path = root / "docs" / "system" / "architecture.md"
    if not arch_path.exists():
        errors.append("docs/system/architecture.md: Missing architecture spec.")
        return

    raw_arch = normalize_text(arch_path.read_text(encoding="utf-8"))
    mapped_component_paths: set[str] = set()

    for cells in parse_markdown_table_rows(raw_arch, 5):
        if "コンポーネントID" in cells[0]:
            continue
        link_match = re.search(r"\[[^\]]+\]\(([^)]+)\)", cells[1])
        if not link_match:
            errors.append(
                f"docs/system/architecture.md: Component row '{cells[0]}' must link to "
                f"'[...](../components/<id>.md)' in column 2."
            )
            continue
        resolved = (arch_path.parent / link_match.group(1).strip()).resolve()
        try:
            rel_comp = resolved.relative_to(root.resolve()).as_posix()
            mapped_component_paths.add(rel_comp)
        except ValueError:
            errors.append(f"docs/system/architecture.md: Invalid component path '{cells[1]}'.")

    actual_components = {
        p for p in spec_files if p.startswith("docs/components/") and p != "docs/components/_template.md"
    }

    if not actual_components:
        errors.append(
            "docs/components/: No component specs found in --strict mode (at least 1 required)."
        )

    for missing in sorted(mapped_component_paths - actual_components):
        errors.append(
            f"docs/system/architecture.md: Mapped component '{missing}' does not exist in docs/components/."
        )
    for unmapped in sorted(actual_components - mapped_component_paths):
        errors.append(
            f"{unmapped}: Component file is not listed in docs/system/architecture.md component table."
        )

    required_headings = ["## 1.", "## 2.", "## 3.", "## 4."]
    for comp_path in sorted(actual_components):
        comp_text = normalize_text((root / comp_path).read_text(encoding="utf-8"))
        comp_stem = Path(comp_path).stem
        for h in required_headings:
            if h not in comp_text:
                errors.append(
                    f"{comp_path}: Missing required section heading starting with '{h}' (per _template.md)."
                )
        for suffix in ["scope", "interface", "contract", "verification"]:
            expected_subtag = f"@spec:component-{comp_stem}-{suffix}"
            if expected_subtag not in comp_text:
                errors.append(
                    f"{comp_path}: Missing standardized section tag '<!-- {expected_subtag} -->' (per _template.md)."
                )


def parse_markdown_table_rows(markdown_text: str, min_cols: int) -> list[list[str]]:
    """Extract non-separator rows from Markdown tables with at least min_cols columns."""
    cleaned = re.sub(r"```[\s\S]*?```", "", re.sub(r"<!--[\s\S]*?-->", "", markdown_text))
    rows: list[list[str]] = []
    for line in cleaned.splitlines():
        s = line.strip()
        if not s.startswith("|") or not s.endswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < min_cols:
            continue
        if all(set(c) <= {":", "-", " "} for c in cells if c):
            continue
        rows.append(cells)
    return rows


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Verify AIDD/SDD specification integrity.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enable strict post-bootstrap checks (no placeholders, no BOOTSTRAP.md, 1:1 component map).",
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Automatically synchronize docs/spec-router.md (Mermaid DAG and routing table) from spec frontmatters.",
    )
    args = parser.parse_args()

    root = find_repo_root()
    errors: list[str] = []

    # 1. Check immutable files exist
    for imm in IMMUTABLE_FILES:
        if not (root / imm).exists():
            errors.append(f"{imm}: Required immutable file is missing.")

    spec_files = collect_spec_files(root)
    specs_by_path: dict[str, dict] = {}
    specs_by_id: dict[str, dict] = {}
    all_spec_tags: dict[str, str] = {}

    # 2. Parse and validate each spec file
    for rel_path in spec_files:
        full_path = root / rel_path
        text = normalize_text(full_path.read_text(encoding="utf-8"))
        fm, body = parse_simple_yaml_frontmatter(text, rel_path, errors)
        if not fm:
            continue

        missing_keys = REQUIRED_FRONTMATTER_KEYS - set(fm.keys())
        if missing_keys:
            errors.append(
                f"{rel_path}: Missing frontmatter keys: {', '.join(sorted(missing_keys))}."
            )
            continue

        extra_keys = set(fm.keys()) - REQUIRED_FRONTMATTER_KEYS
        if extra_keys:
            errors.append(
                f"{rel_path}: Unexpected/deprecated frontmatter keys: {', '.join(sorted(extra_keys))} "
                f"(only {', '.join(sorted(REQUIRED_FRONTMATTER_KEYS))} are allowed; layer is auto-derived from path)."
            )

        layer = infer_layer_from_path(rel_path)
        if layer is None:
            errors.append(
                f"{rel_path}: Spec file is located in an unrecognized directory for layer derivation."
            )
            continue

        spec_id = str(fm["spec_id"])
        title = str(fm["title"]).strip()
        status = str(fm["status"])
        target_files = fm["target_files"]
        dependencies = fm["dependencies"]

        # Verify H1 heading matches Frontmatter title
        h1_match = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
        if not h1_match:
            errors.append(f"{rel_path}: Missing level-1 heading ('# <Title>') in document body.")
        else:
            h1_title = h1_match.group(1).strip()
            if h1_title != title:
                errors.append(
                    f"{rel_path}: H1 heading '{h1_title}' does not match Frontmatter title '{title}'."
                )

        if status not in {"draft", "stable"}:
            errors.append(f"{rel_path}: Invalid status '{status}' (must be 'draft' or 'stable').")
        if not isinstance(target_files, list) or not isinstance(dependencies, list):
            errors.append(f"{rel_path}: 'target_files' and 'dependencies' must be lists.")
            continue

        if spec_id in specs_by_id:
            errors.append(
                f"{rel_path}: Duplicate spec_id '{spec_id}' (already defined in {specs_by_id[spec_id]['path']})."
            )

        # Check @spec tags in body
        tags_in_file = re.findall(r"<!--\s*(@spec:[a-zA-Z0-9_\-]+)\s*-->", body)
        primary_tag = f"@spec:{spec_id}"
        if primary_tag not in tags_in_file:
            errors.append(
                f"{rel_path}: Missing primary tag '<!-- {primary_tag} -->' in document body."
            )
        for tag in tags_in_file:
            if tag in all_spec_tags:
                errors.append(
                    f"{rel_path}: Duplicate tag '{tag}' (already defined in {all_spec_tags[tag]})."
                )
            all_spec_tags[tag] = rel_path

        meta = {
            "path": rel_path,
            "spec_id": spec_id,
            "title": title,
            "layer": layer,
            "status": status,
            "target_files": target_files,
            "dependencies": dependencies,
            "subtags": [t for t in tags_in_file if t != primary_tag],
        }
        specs_by_path[rel_path] = meta
        specs_by_id[spec_id] = meta

        # Check immutable files integrity
        if rel_path in IMMUTABLE_FILES:
            if status != "stable":
                errors.append(f"{rel_path}: Immutable file must have 'status: stable'.")
            for pat, desc in PLACEHOLDER_PATTERNS:
                if re.search(pat, text):
                    errors.append(f"{rel_path}: Immutable file contains {desc}.")

        # Check target_files existence when status is stable or in strict mode
        if status == "stable" or args.strict:
            for pattern in target_files:
                if pattern == "**/*":
                    continue
                matches = glob.glob(str(root / pattern), recursive=True)
                if not matches:
                    errors.append(
                        f"{rel_path}: target_files pattern '{pattern}' matched 0 files on disk."
                    )

        # Check relative links
        check_relative_links(root, rel_path, body, errors)

    # Check relative links in README.md and BOOTSTRAP.md if present
    for root_doc in ["README.md", "BOOTSTRAP.md"]:
        if (root / root_doc).exists():
            check_relative_links(
                root, root_doc, normalize_text((root / root_doc).read_text(encoding="utf-8")), errors
            )

    # 3. Verify DAG (cycles & layer inversions & router reverse dependencies)
    check_dag_cycles(specs_by_id, errors)

    # 4. Synchronize or verify spec-router.md
    sync_or_verify_spec_router(root, specs_by_path, specs_by_id, args.sync, errors)

    # 5. Strict checks if requested
    if args.strict:
        verify_strict_mode(root, spec_files, errors)

    mode_label = "STRICT MODE" if args.strict else "STANDARD MODE"
    if errors:
        print(f"=== Spec Verification FAILED ({mode_label}): {len(errors)} error(s) ===", file=sys.stderr)
        for err in errors:
            print(f"  [FAIL] {err}", file=sys.stderr)
        return 1

    print(
        f"=== Spec Verification PASSED ({mode_label}): "
        f"{len(specs_by_path)} specs, {len(all_spec_tags)} @spec tags, DAG & Router 100% valid ==="
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
