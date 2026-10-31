#!/usr/bin/env python3
"""Deterministic static verifier and synchronizer for AIDD/SDD specifications."""

import argparse
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
    "docs/specs/core-rules.md",
]

PLACEHOLDER_PATTERNS = [
    (r"\[要記入:", "Unfilled placeholder '[要記入: ...]'"),
    (r"\{\{[A-Za-z0-9_]+\}\}", "Unreplaced template token '{{...}}'"),
    (r"<!--\s*GUIDE:", "Unremoved template guide comment '<!-- GUIDE: ... -->'"),
    (r"<[^>\n]*[ぁ-んァ-ヶ一-龠々ー][^>\n]*>", "Unfilled template placeholder '<...>'"),
]


def is_template_file(rel_path: str) -> bool:
    """Check if file is a template (named '_template.md')."""
    return Path(rel_path).name == "_template.md"


def infer_category_from_path(rel_path: str) -> int | str | None:
    """Deterministically infer specification category/layer from repository-relative POSIX path."""
    if rel_path == "AGENTS.md":
        return 0
    if rel_path == "docs/specs/spec-router.md":
        return "-"
    if rel_path == "docs/specs/core-rules.md":
        return 1

    parts = Path(rel_path).parts
    if len(parts) == 3 and parts[0] == "docs" and parts[1] == "specs":
        # Any .md file directly under docs/specs/ is treated as Core (1)
        return 1

    if len(parts) >= 4 and parts[0] == "docs" and parts[1] == "specs":
        # Dynamic top-level directory under docs/specs/ (e.g. system, components, usecases, services)
        return parts[2]

    return None


def category_sort_key(cat: int | str) -> tuple[int, str]:
    """Sort key for categories: 0 -> '-' -> 1 -> directory names alphabetically."""
    if cat == 0 or cat == "0":
        return (0, "")
    if cat == "-":
        return (1, "")
    if cat == 1 or cat == "1":
        return (2, "")
    return (3, str(cat))


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


def strip_code(markdown_text: str) -> str:
    """Remove fenced code blocks and inline code."""
    text = re.sub(r"```[\s\S]*?```", "", markdown_text)
    text = re.sub(r"`[^`\n]+`", "", text)
    return text


def strip_code_and_comments(markdown_text: str) -> str:
    """Remove fenced code blocks, inline code, and HTML comments for link scanning."""
    return re.sub(r"<!--[\s\S]*?-->", "", strip_code(markdown_text))


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
    docs_dir = root / "docs" / "specs"
    if docs_dir.exists():
        for p in sorted(docs_dir.rglob("*.md")):
            rel = p.relative_to(root).as_posix()
            files.append(rel)
    return files


def check_dag_cycles(specs_by_id: dict[str, dict], errors: list[str]) -> None:
    """Verify dependency references exist, protect constitutional boundaries, forbid reverse-dependency to router index, and form a valid DAG (zero cycles)."""
    for spec_id, meta in specs_by_id.items():
        src_cat = meta.get("category", meta.get("layer", 0))
        for dep_id in meta.get("dependencies", []):
            if dep_id not in specs_by_id:
                errors.append(
                    f"{meta['path']}: Unknown dependency spec_id '{dep_id}' in frontmatter."
                )
                continue

            dep_meta = specs_by_id[dep_id]
            dep_cat = dep_meta.get("category", dep_meta.get("layer", 0))

            # Specification files MUST NOT depend on the router index (Layer '-')
            if dep_id == "spec-router" or dep_cat == "-":
                errors.append(
                    f"{meta['path']}: Spec files cannot depend on router index '{dep_id}' (Layer '-')."
                )
                continue

            # Constitutional boundary check: Layer 0 and Layer 1 cannot depend on lower project specs
            if src_cat in (0, "0") and dep_cat not in (0, "0"):
                errors.append(
                    f"{meta['path']}: Meta guideline ('{spec_id}') cannot depend on lower spec '{dep_id}'."
                )
            elif src_cat in (1, "1") and dep_cat not in (0, "0", 1, "1"):
                errors.append(
                    f"{meta['path']}: Core rules ('{spec_id}') cannot depend on project spec '{dep_id}'."
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
    """Generate deterministic Mermaid flowchart grouped dynamically by categories."""
    lines = ["```mermaid", "flowchart TD"]

    # Filter out router and template specs
    active_specs = [
        meta
        for meta in specs_by_id.values()
        if not is_template_file(meta["path"]) and meta.get("category") != "-"
    ]

    categories = sorted({m["category"] for m in active_specs}, key=category_sort_key)

    for cat in categories:
        cat_specs = [m for m in active_specs if m["category"] == cat]
        if not cat_specs:
            continue
        cat_specs.sort(key=lambda m: m["path"])

        if cat in (0, "0"):
            sg_id = "L0"
            sg_title = "Meta Guideline"
        elif cat in (1, "1"):
            sg_id = "L1"
            sg_title = "Core Rules"
        else:
            sg_id = re.sub(r"[^a-zA-Z0-9_]", "_", str(cat))
            sg_title = str(cat)

        lines.append(f'    subgraph {sg_id}["{sg_title}"]')
        for meta in cat_specs:
            sid = meta["spec_id"]
            spec_path = Path(meta["path"])
            disp_path = (
                spec_path.relative_to("docs/specs").as_posix()
                if meta["path"].startswith("docs/specs/")
                else spec_path.as_posix()
            )
            lines.append(f'        {sid}["{disp_path}"]')
        lines.append("    end")

    # Dependency edges
    edges: list[tuple[str, str]] = []
    for spec_id, meta in specs_by_id.items():
        if meta.get("category") == "-" or is_template_file(meta["path"]):
            continue
        for dep_id in meta.get("dependencies", []):
            if (
                dep_id in specs_by_id
                and specs_by_id[dep_id].get("category") != "-"
                and not is_template_file(specs_by_id[dep_id]["path"])
            ):
                edges.append((spec_id, dep_id))

    edges.sort()
    for src, dst in edges:
        lines.append(f"    {src} --> {dst}")

    lines.append("```")
    return "\n".join(lines)


def generate_routing_table(root: Path, specs_by_path: dict[str, dict]) -> str:
    """Generate deterministic Markdown table for docs/specs/spec-router.md."""
    lines = [
        "| 分類 | 仕様書 | タイトル | 主タグ | セクションサブタグ | 対象スコープ | 依存仕様 |",
        "| :---: | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    router_dir = root / "docs" / "specs"

    sorted_specs = sorted(
        specs_by_path.values(),
        key=lambda m: (category_sort_key(m["category"]), m["path"]),
    )

    for meta in sorted_specs:
        cat_str = f"**{meta['category']}**"

        target_path = root / meta["path"]
        if target_path.is_relative_to(router_dir):
            rel_link = target_path.relative_to(router_dir).as_posix()
        else:
            rel_link = (Path("..") / Path("..") / target_path.relative_to(root)).as_posix()

        is_sub = target_path.is_relative_to(router_dir) and target_path.parent != router_dir
        name = rel_link if is_sub else target_path.name
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
            f"| {cat_str} | {spec_link} | {title_str} | {primary_tag} | {subtags_str} | {scopes_str} | {deps_str} |"
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
    """Synchronize or verify that docs/specs/spec-router.md matches generated DAG and routing table."""
    router_path = root / "docs" / "specs" / "spec-router.md"
    rel_path = "docs/specs/spec-router.md"
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


def check_strict_leftovers_and_placeholders(
    root: Path, spec_files: list[str], errors: list[str]
) -> None:
    """Check that BOOTSTRAP.md, staged ref/ templates, and unfilled placeholders do not remain."""
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
        if is_template_file(rel_path):
            continue
        content = normalize_text((root / rel_path).read_text(encoding="utf-8"))
        check_content = content.replace("<分類>", "")
        for pat, desc in PLACEHOLDER_PATTERNS:
            if re.search(pat, check_content):
                errors.append(f"{rel_path}: {desc} found in --strict mode.")


def check_component_mapping_and_structure(
    root: Path, spec_files: list[str], errors: list[str]
) -> None:
    """Verify 1:1 mapping between docs/specs/system/architecture.md table and linked component specs."""
    arch_path = root / "docs" / "specs" / "system" / "architecture.md"
    if not arch_path.exists():
        return

    raw_arch = normalize_text(arch_path.read_text(encoding="utf-8"))
    comp_map_match = re.search(
        r"<!--\s*@spec:component-map\s*-->([\s\S]*?)(?=\n##\s+|\n<!--\s*@spec:|\Z)",
        strip_code(raw_arch),
    )
    if not comp_map_match:
        return

    mapped_component_paths: set[str] = set()
    mapped_dirs: set[Path] = set()

    for cells in parse_markdown_table_rows(comp_map_match.group(1), 5):
        if "コンポーネントID" in cells[0] or any("[要記入:" in c for c in cells):
            continue
        link_match = re.search(r"\[[^\]]+\]\(([^)]+)\)", cells[1])
        if not link_match:
            errors.append(
                f"docs/specs/system/architecture.md: Component row '{cells[0]}' must link to a component spec in column 2."
            )
            continue
        resolved = (arch_path.parent / link_match.group(1).strip()).resolve()
        try:
            rel_comp = resolved.relative_to(root.resolve()).as_posix()
            mapped_component_paths.add(rel_comp)
            mapped_dirs.add(resolved.parent)
        except ValueError:
            errors.append(f"docs/specs/system/architecture.md: Invalid component path '{cells[1]}'.")

    # If rows exist, find all actual non-template specs in the referenced directories
    actual_components: set[str] = set()
    for d in mapped_dirs:
        if d.exists():
            for p in d.glob("*.md"):
                rel = p.relative_to(root).as_posix()
                if not is_template_file(rel):
                    actual_components.add(rel)

    for missing in sorted(mapped_component_paths - actual_components):
        errors.append(
            f"docs/specs/system/architecture.md: Mapped component '{missing}' does not exist on disk."
        )
    for unmapped in sorted(actual_components - mapped_component_paths):
        errors.append(
            f"{unmapped}: Component file is not listed in docs/specs/system/architecture.md component table."
        )

    required_headings = ["## 1.", "## 2.", "## 3.", "## 4."]
    for comp_path in sorted(actual_components):
        comp_text = normalize_text((root / comp_path).read_text(encoding="utf-8"))
        comp_stem = Path(comp_path).stem
        if "@spec:component-template" in comp_text:
            errors.append(
                f"{comp_path}: Unreplaced template tag '@spec:component-template' found in --strict mode."
            )
        if "<id>" in comp_text:
            errors.append(
                f"{comp_path}: Unreplaced template placeholder '<id>' found in --strict mode."
            )
        for h in required_headings:
            if h not in comp_text:
                errors.append(
                    f"{comp_path}: Missing required section heading starting with '{h}'."
                )


def verify_strict_mode(root: Path, spec_files: list[str], errors: list[str]) -> None:
    """Perform strict post-bootstrap checks: no BOOTSTRAP.md, no placeholders, 1:1 component map."""
    check_strict_leftovers_and_placeholders(root, spec_files, errors)
    check_component_mapping_and_structure(root, spec_files, errors)


def parse_markdown_table_rows(markdown_text: str, min_cols: int) -> list[list[str]]:
    """Extract non-separator rows from Markdown tables with at least min_cols columns."""
    no_fenced = re.sub(r"```[\s\S]*?```", "", markdown_text)
    cleaned = re.sub(
        r"(`[^`\n]+`)|<!--[\s\S]*?-->",
        lambda m: m.group(1).replace("|", r"\|") if m.group(1) else "",
        no_fenced,
    )
    rows: list[list[str]] = []
    for line in cleaned.splitlines():
        s = line.strip()
        if not s.startswith("|") or not s.endswith("|"):
            continue
        cells = [c.replace(r"\|", "|").strip() for c in re.split(r"(?<!\\)\|", s[1:-1])]
        if len(cells) < min_cols:
            continue
        if all(set(c) <= {":", "-", " "} for c in cells if c):
            continue
        rows.append(cells)
    return rows


def validate_single_spec(
    root: Path,
    rel_path: str,
    specs_by_id: dict[str, dict],
    all_spec_tags: dict[str, str],
    errors: list[str],
) -> dict | None:
    """Parse and validate frontmatter, H1, @spec tags, immutable rules, and target_files for one spec."""
    full_path = root / rel_path
    text = normalize_text(full_path.read_text(encoding="utf-8"))
    fm, body = parse_simple_yaml_frontmatter(text, rel_path, errors)
    if not fm:
        return None

    missing_keys = REQUIRED_FRONTMATTER_KEYS - set(fm.keys())
    if missing_keys:
        errors.append(
            f"{rel_path}: Missing frontmatter keys: {', '.join(sorted(missing_keys))}."
        )
        return None

    extra_keys = set(fm.keys()) - REQUIRED_FRONTMATTER_KEYS
    if extra_keys:
        errors.append(
            f"{rel_path}: Unexpected/deprecated frontmatter keys: {', '.join(sorted(extra_keys))} "
            f"(only {', '.join(sorted(REQUIRED_FRONTMATTER_KEYS))} are allowed; category is auto-derived from path)."
        )

    category = infer_category_from_path(rel_path)
    if category is None:
        errors.append(
            f"{rel_path}: Spec file is located in an unrecognized directory for category derivation."
        )
        return None

    spec_id = str(fm["spec_id"])
    title = str(fm["title"]).strip()
    status = str(fm["status"])
    target_files = fm["target_files"]
    dependencies = fm["dependencies"]

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
        return None

    if spec_id in specs_by_id:
        errors.append(
            f"{rel_path}: Duplicate spec_id '{spec_id}' (already defined in {specs_by_id[spec_id]['path']})."
        )

    tags_in_file = re.findall(
        r"<!--\s*(@spec:[a-zA-Z0-9_\-]+)\s*-->", strip_code(body)
    )
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

    is_template = is_template_file(rel_path)

    if rel_path in IMMUTABLE_FILES:
        if status != "stable":
            errors.append(f"{rel_path}: Immutable file must have 'status: stable'.")
        if not is_template:
            check_text = text.replace("<分類>", "")
            for pat, desc in PLACEHOLDER_PATTERNS:
                if re.search(pat, check_text):
                    errors.append(f"{rel_path}: Immutable file contains {desc}.")

    if status == "stable" and not is_template:
        for pattern in target_files:
            if pattern == "**/*":
                continue
            matches = list(root.glob(pattern))
            if not matches:
                errors.append(
                    f"{rel_path}: target_files pattern '{pattern}' matched 0 files on disk."
                )

    return {
        "path": rel_path,
        "spec_id": spec_id,
        "title": title,
        "category": category,
        "layer": category,  # Keep layer as alias for backward compatibility
        "status": status,
        "target_files": target_files,
        "dependencies": dependencies,
        "subtags": [t for t in tags_in_file if t != primary_tag],
    }


def check_all_relative_links(root: Path, spec_files: list[str], errors: list[str]) -> None:
    """Check relative markdown links across all spec files and root documentation."""
    for rel_path in spec_files:
        text = normalize_text((root / rel_path).read_text(encoding="utf-8"))
        _, body = parse_simple_yaml_frontmatter(text, rel_path, [])
        check_relative_links(root, rel_path, body, errors)

    for root_doc in ["README.md", "BOOTSTRAP.md"]:
        if (root / root_doc).exists():
            check_relative_links(
                root, root_doc, normalize_text((root / root_doc).read_text(encoding="utf-8")), errors
            )


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
        help="Automatically synchronize docs/specs/spec-router.md (Mermaid DAG and routing table) from spec frontmatters.",
    )
    args = parser.parse_args()

    root = find_repo_root()
    errors: list[str] = []

    for imm in IMMUTABLE_FILES:
        if not (root / imm).exists():
            errors.append(f"{imm}: Required immutable file is missing.")

    spec_files = collect_spec_files(root)
    specs_by_path: dict[str, dict] = {}
    specs_by_id: dict[str, dict] = {}
    all_spec_tags: dict[str, str] = {}

    for rel_path in spec_files:
        meta = validate_single_spec(root, rel_path, specs_by_id, all_spec_tags, errors)
        if meta is not None:
            specs_by_path[rel_path] = meta
            specs_by_id[meta["spec_id"]] = meta

    check_dag_cycles(specs_by_id, errors)
    sync_or_verify_spec_router(root, specs_by_path, specs_by_id, args.sync, errors)
    check_all_relative_links(root, spec_files, errors)

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
