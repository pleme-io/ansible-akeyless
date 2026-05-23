"""
Auto-generates per-plugin and per-module reference pages from the
DOCUMENTATION YAML blocks that already live in every plugin / module
file.

Runs at mkdocs build time via the mkdocs-gen-files plugin. The
generated files are written to a virtual `docs/reference/{plugins,modules}/`
tree; they're NOT checked into the repo (regenerate on every build).

Why this approach (instead of antsibull-docs):
- antsibull-docs renders to RST + assumes the Ansible sphinx pipeline.
  This collection wants Markdown so mkdocs-material renders it natively.
- The DOCUMENTATION YAML is the single source of truth; sanity tests
  already enforce its presence, parseability, and required-keys.
  Reading it directly removes a translation layer.
- 209 modules + 17 non-module plugins is too many to maintain by hand;
  one Python script regenerates everything in <1s.

The script discovers plugins/modules by walking plugins/ and looking
for DOCUMENTATION = '...' assignments, then renders them through a
small Markdown template. No new dependencies beyond PyYAML.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

try:
    import mkdocs_gen_files  # type: ignore[import-not-found]
    _USING_GEN_FILES = True
except ImportError:
    # When run standalone for testing (e.g. via `python scripts/build_reference_docs.py`),
    # write straight to disk under docs/reference/. The mkdocs-gen-files
    # plugin redirects writes to the virtual tree when imported.
    _USING_GEN_FILES = False


REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGINS_DIR = REPO_ROOT / "plugins"
NAMESPACE = "drzln0"
COLLECTION = "akeyless"

# Mapping of plugins/ subdirectory -> (display name, doc URL slug).
PLUGIN_TYPES = [
    ("lookup",     "Lookup plugins",     "lookup"),
    ("inventory",  "Inventory plugins",  "inventory"),
    ("filter",     "Filter plugins",     "filter"),
    ("test",       "Test plugins",       "test"),
    ("callback",   "Callback plugins",   "callback"),
    ("action",     "Action plugins",     "action"),
    ("cache",      "Cache plugins",      "cache"),
]


# ---------------------------------------------------------------------------
# DOCUMENTATION extraction
# ---------------------------------------------------------------------------


_DOC_RE = re.compile(
    r"^(?P<key>DOCUMENTATION|EXAMPLES|RETURN)\s*=\s*[rRuU]?(?P<q>'''|\"\"\")"
    r"(?P<body>.*?)(?P=q)",
    re.DOTALL | re.MULTILINE,
)


def extract_blocks(path: Path) -> Dict[str, str]:
    """Return {DOCUMENTATION, EXAMPLES, RETURN} -> raw body strings."""
    text = path.read_text(encoding="utf-8")
    blocks: Dict[str, str] = {}
    for m in _DOC_RE.finditer(text):
        blocks[m.group("key")] = m.group("body")
    return blocks


def parse_doc(body: str) -> Optional[Dict[str, Any]]:
    """Parse a DOCUMENTATION YAML body into a dict. Returns None on
    parse failure (skip the page rather than crash the docs build)."""
    if not body.strip():
        return None
    try:
        parsed = yaml.safe_load(body)
    except yaml.YAMLError:
        return None
    if not isinstance(parsed, dict):
        return None
    return parsed


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------


def render_options(options: Dict[str, Any], indent: int = 0) -> str:
    """Render an options dict as a markdown definition list. Supports
    nested options via the standard Ansible `options:` recursion."""
    if not options:
        return "_No options._\n"
    out: List[str] = []
    prefix = "  " * indent
    for name, opt in options.items():
        if not isinstance(opt, dict):
            continue
        out.append(f"{prefix}### `{name}`\n")
        desc = opt.get("description", "_no description_")
        if isinstance(desc, list):
            desc = " ".join(str(d) for d in desc)
        out.append(f"{prefix}{desc}\n")
        meta: List[Tuple[str, Any]] = []
        for key in ("type", "default", "choices", "required", "elements"):
            if key in opt:
                meta.append((key, opt[key]))
        if meta:
            badges = " ".join(
                f"**{k}**: `{v}`" for k, v in meta
            )
            out.append(f"{prefix}{badges}\n")
        # Env vars (lookup / inventory plugins commonly declare these).
        env_entries = opt.get("env")
        if env_entries:
            env_names = [e.get("name") if isinstance(e, dict) else str(e)
                          for e in env_entries]
            out.append(f"{prefix}_env_: " + ", ".join(f"`{n}`" for n in env_names) + "\n")
        # Nested options.
        nested = opt.get("options")
        if isinstance(nested, dict):
            out.append(f"\n{prefix}{render_options(nested, indent + 1)}\n")
        out.append("")
    return "\n".join(out)


def render_examples(examples_body: Optional[str]) -> str:
    if not examples_body or not examples_body.strip():
        return ""
    return f"## Examples\n\n```yaml\n{examples_body.strip()}\n```\n"


def render_returns(returns_body: Optional[str]) -> str:
    if not returns_body or not returns_body.strip():
        return ""
    try:
        parsed = yaml.safe_load(returns_body)
    except yaml.YAMLError:
        return f"## Return values\n\n```yaml\n{returns_body.strip()}\n```\n"
    if not isinstance(parsed, dict):
        return ""
    out = ["## Return values\n"]
    for name, info in parsed.items():
        if not isinstance(info, dict):
            continue
        desc = info.get("description", "")
        if isinstance(desc, list):
            desc = " ".join(str(d) for d in desc)
        t = info.get("type", "any")
        returned = info.get("returned", "")
        out.append(f"### `{name}` _({t})_\n")
        if returned:
            out.append(f"_returned: {returned}_\n")
        out.append(f"{desc}\n")
    return "\n".join(out) + "\n"


def render_plugin_page(
    plugin_type: str,
    plugin_name: str,
    blocks: Dict[str, str],
) -> str:
    """Generate the per-plugin markdown page."""
    doc = parse_doc(blocks.get("DOCUMENTATION", "")) or {}
    short = doc.get("short_description", "")
    description = doc.get("description") or ""
    if isinstance(description, list):
        description = "\n\n".join(str(d) for d in description)
    author = doc.get("author") or []
    if isinstance(author, list):
        author = ", ".join(str(a) for a in author)
    version_added = doc.get("version_added", "")
    options = doc.get("options") or {}

    fqcn = f"{NAMESPACE}.{COLLECTION}.{plugin_name}"

    lines = [
        f"# `{fqcn}` — {plugin_type} plugin",
        "",
        f"> {short}" if short else "",
        "",
    ]
    if version_added:
        lines.append(f"_Available since version: {version_added}_\n")
    if author:
        lines.append(f"_Authors: {author}_\n")
    lines.append("")
    lines.append("## Description")
    lines.append(description if description else "_no description_")
    lines.append("")
    lines.append("## Options")
    lines.append(render_options(options))
    lines.append(render_examples(blocks.get("EXAMPLES")))
    lines.append(render_returns(blocks.get("RETURN")))
    lines.append("---")
    lines.append(
        f"_Auto-generated from "
        f"[plugins/{plugin_type}/{plugin_name}.py]"
        f"(https://github.com/pleme-io/ansible-akeyless/blob/main/plugins/{plugin_type}/{plugin_name}.py)._"
    )
    return "\n".join(lines)


def render_module_page(module_name: str, blocks: Dict[str, str]) -> str:
    """Generate the per-module markdown page. Almost identical to
    the plugin renderer; modules use `module:` + `extends_documentation_fragment:`."""
    doc = parse_doc(blocks.get("DOCUMENTATION", "")) or {}
    short = doc.get("short_description", "")
    description = doc.get("description") or ""
    if isinstance(description, list):
        description = "\n\n".join(str(d) for d in description)
    author = doc.get("author") or []
    if isinstance(author, list):
        author = ", ".join(str(a) for a in author)
    options = doc.get("options") or {}

    fqcn = f"{NAMESPACE}.{COLLECTION}.{module_name}"

    lines = [
        f"# `{fqcn}`",
        "",
        f"> {short}" if short else "",
        "",
    ]
    if author:
        lines.append(f"_Authors: {author}_\n")
    lines.append("")
    lines.append("## Description")
    lines.append(description if description else "_no description_")
    lines.append("")
    lines.append("## Auth options")
    lines.append(
        "This module inherits the standard Akeyless auth options "
        "(`gateway_url`, `access_id`, `access_key`, `access_type`, `token`) "
        "via the `drzln0.akeyless.auth` doc fragment."
    )
    lines.append("")
    lines.append("## Module-specific options")
    lines.append(render_options(options))
    lines.append(render_examples(blocks.get("EXAMPLES")))
    lines.append(render_returns(blocks.get("RETURN")))
    lines.append("---")
    lines.append(
        f"_Auto-generated from "
        f"[plugins/modules/{module_name}.py]"
        f"(https://github.com/pleme-io/ansible-akeyless/blob/main/plugins/modules/{module_name}.py)._"
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------


def _write(virtual_path: str, content: str) -> None:
    """Write `content` to the virtual mkdocs path (via mkdocs-gen-files
    when running under mkdocs build) or to disk (when run standalone)."""
    if _USING_GEN_FILES:
        with mkdocs_gen_files.open(virtual_path, "w") as fh:
            fh.write(content)
    else:
        out = REPO_ROOT / "docs" / virtual_path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content)


# ---------------------------------------------------------------------------
# Build entry-point
# ---------------------------------------------------------------------------


def build_plugin_pages() -> List[Tuple[str, str, str]]:
    """Render per-plugin pages + return [(type, name, page_path)] for
    the nav summary."""
    nav_entries: List[Tuple[str, str, str]] = []
    for type_dir, display, slug in PLUGIN_TYPES:
        plugin_path = PLUGINS_DIR / type_dir
        if not plugin_path.exists():
            continue
        for p in sorted(plugin_path.glob("*.py")):
            if p.name == "__init__.py":
                continue
            # For filter type, skip the impl-only akeyless.py
            if type_dir == "filter" and p.name == "akeyless.py":
                continue
            blocks = extract_blocks(p)
            if not blocks.get("DOCUMENTATION"):
                continue
            page = render_plugin_page(type_dir, p.stem, blocks)
            virtual = f"reference/plugins/{type_dir}/{p.stem}.md"
            _write(virtual, page)
            nav_entries.append((display, p.stem, virtual))
    return nav_entries


def build_module_pages() -> List[Tuple[str, str]]:
    """Render per-module pages + return [(name, page_path)] for the
    nav summary."""
    nav_entries: List[Tuple[str, str]] = []
    modules_dir = PLUGINS_DIR / "modules"
    for p in sorted(modules_dir.glob("*.py")):
        if p.name == "__init__.py":
            continue
        blocks = extract_blocks(p)
        if not blocks.get("DOCUMENTATION"):
            continue
        page = render_module_page(p.stem, blocks)
        virtual = f"reference/modules/{p.stem}.md"
        _write(virtual, page)
        nav_entries.append((p.stem, virtual))
    return nav_entries


def build_nav_indices(
    plugin_nav: List[Tuple[str, str, str]],
    module_nav: List[Tuple[str, str]],
) -> None:
    """Write a per-section SUMMARY.md the literate-nav mkdocs plugin
    consumes, plus per-type index pages."""
    # Plugins index, grouped by type.
    by_type: Dict[str, List[Tuple[str, str]]] = {}
    for display, name, path in plugin_nav:
        by_type.setdefault(display, []).append((name, path))
    index_lines = ["# Plugins reference\n",
                    "Auto-generated from each plugin's DOCUMENTATION YAML.\n"]
    summary_lines = []
    for display in sorted(by_type):
        entries = sorted(by_type[display])
        index_lines.append(f"## {display}\n")
        for name, path in entries:
            rel = path.replace("reference/plugins/", "")
            index_lines.append(f"- [{name}]({rel})")
        index_lines.append("")
        summary_lines.append(f"* [{display}](index.md)")
        for name, path in entries:
            rel = path.replace("reference/plugins/", "")
            summary_lines.append(f"  * [{name}]({rel})")
    _write("reference/plugins/index.md", "\n".join(index_lines))
    _write("reference/plugins/SUMMARY.md", "\n".join(summary_lines))

    # Modules index.
    modules_index = ["# Modules reference\n",
                      f"_Total: {len(module_nav)} modules._\n",
                      "Auto-generated from each module's DOCUMENTATION YAML.\n",
                      "## Modules\n"]
    for name, path in module_nav:
        rel = path.replace("reference/modules/", "")
        modules_index.append(f"- [{name}]({rel})")
    _write("reference/modules/index.md", "\n".join(modules_index))
    summary_mods = [f"* [{n}]({p.replace('reference/modules/', '')})"
                     for n, p in module_nav]
    _write("reference/modules/SUMMARY.md",
           "\n".join(["* [Modules](index.md)"] + ["  " + s for s in summary_mods]))


def main() -> None:
    plugin_nav = build_plugin_pages()
    module_nav = build_module_pages()
    build_nav_indices(plugin_nav, module_nav)
    if not _USING_GEN_FILES:
        print(f"Wrote {len(plugin_nav)} plugin + {len(module_nav)} module pages")


# Always-run entry point (mkdocs-gen-files invokes the file at import time).
main()
