# Copyright: (c) 2026, pleme-io
# MIT License
#
# Sanity tests for plugin DOCUMENTATION blocks. Every non-module plugin
# that ships with the collection exposes a YAML DOCUMENTATION string at
# module level for ansible-doc to render. A malformed block is silent at
# import time but breaks ansible-doc rendering, so we parse-check each
# block here.
#
# Covers: lookup (3), inventory (1), callback (1), test (4), cache (1).
# Filter plugins use FilterModule.filters() exclusively and don't ship a
# DOCUMENTATION block, so they're skipped (per-filter docs would need a
# different layout). Action plugins likewise rely on the shadow module's
# DOCUMENTATION, not their own.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
PLUGINS_DIR = REPO_ROOT / "plugins"

# Per-plugin-type minimums. Each plugin's DOCUMENTATION block must carry
# at least these top-level YAML keys (ansible-doc-required).
COMMON_REQUIRED = frozenset({"description"})

# Per-type required keys on top of COMMON_REQUIRED.
TYPE_REQUIRED: dict = {
    # lookup: ansible-doc renders short_description + name on the
    # plugin index; missing them gives a noisy 'unparsed' line.
    "lookup": frozenset({"name", "short_description", "author"}),
    "inventory": frozenset({"name", "short_description", "author"}),
    "callback": frozenset({"name", "short_description", "author"}),
    "test": frozenset({"name", "short_description", "author"}),
    "cache": frozenset({"name", "short_description", "author"}),
}


def _plugin_files():
    """Yield (plugin_type, path) for every plugin file with a
    DOCUMENTATION block, skipping action / module shadows."""
    for plugin_type, type_dir in [
        ("lookup", PLUGINS_DIR / "lookup"),
        ("inventory", PLUGINS_DIR / "inventory"),
        ("callback", PLUGINS_DIR / "callback"),
        ("test", PLUGINS_DIR / "test"),
        ("cache", PLUGINS_DIR / "cache"),
    ]:
        if not type_dir.exists():
            continue
        for path in sorted(type_dir.glob("*.py")):
            if path.name == "__init__.py":
                continue
            yield plugin_type, path


_DOC_RE_TEMPLATE = (
    # Optional r/R/u/U prefix, then triple-quote (either style), capture
    # everything up to the matching closing triple-quote.
    r"^DOCUMENTATION\s*=\s*[rRuU]?{q}{{3}}(.*?){q}{{3}}"
)


def _extract_documentation(path: Path) -> str:
    """Pull the DOCUMENTATION = (r)\"\"\"...\"\"\" string out of a plugin
    file. Tolerant of raw-prefix (`r\"\"\"...`) and both triple-quote
    styles."""
    text = path.read_text()
    for quote in ('"', "'"):
        match = re.search(
            _DOC_RE_TEMPLATE.format(q=quote),
            text,
            flags=re.DOTALL | re.MULTILINE,
        )
        if match:
            return match.group(1)
    return ""


PLUGIN_FILES = list(_plugin_files())


@pytest.mark.parametrize(
    "plugin_type,path",
    PLUGIN_FILES,
    ids=lambda v: v if isinstance(v, str) else v.parent.name + "/" + v.name,
)
def test_plugin_has_documentation_block(plugin_type, path):
    """Every non-module plugin must define a DOCUMENTATION string. Silent
    omission means the plugin renders as 'undocumented' in `ansible-doc
    -l <type>` listings."""
    raw = _extract_documentation(path)
    assert raw.strip(), (
        f"{plugin_type}/{path.name}: no DOCUMENTATION block found "
        f"(expected `DOCUMENTATION = \"\"\"...\"\"\"` at module scope)"
    )


@pytest.mark.parametrize(
    "plugin_type,path",
    PLUGIN_FILES,
    ids=lambda v: v if isinstance(v, str) else v.parent.name + "/" + v.name,
)
def test_plugin_documentation_parses_as_yaml(plugin_type, path):
    """DOCUMENTATION must be valid YAML. Indent / quote errors here
    surface as cryptic ansible-doc tracebacks; parse the YAML directly
    so failures are localised."""
    raw = _extract_documentation(path)
    if not raw.strip():
        pytest.skip("no DOCUMENTATION (covered by earlier test)")
    try:
        parsed = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        pytest.fail(
            f"{plugin_type}/{path.name}: DOCUMENTATION YAML parse error: {exc}"
        )
    assert isinstance(parsed, dict), (
        f"{plugin_type}/{path.name}: DOCUMENTATION must parse to a dict, "
        f"got {type(parsed).__name__}"
    )


@pytest.mark.parametrize(
    "plugin_type,path",
    PLUGIN_FILES,
    ids=lambda v: v if isinstance(v, str) else v.parent.name + "/" + v.name,
)
def test_plugin_documentation_has_required_keys(plugin_type, path):
    """Each plugin type has a minimum set of required top-level keys.
    Missing them means ansible-galaxy + ansible-doc render with
    placeholder values."""
    raw = _extract_documentation(path)
    if not raw.strip():
        pytest.skip("no DOCUMENTATION (covered by earlier test)")
    parsed = yaml.safe_load(raw)
    required = COMMON_REQUIRED | TYPE_REQUIRED.get(plugin_type, frozenset())
    missing = required - set(parsed.keys())
    assert not missing, (
        f"{plugin_type}/{path.name}: DOCUMENTATION missing required keys "
        f"{missing}; required for this plugin type: {sorted(required)}"
    )


@pytest.mark.parametrize(
    "plugin_type,path",
    [(t, p) for t, p in PLUGIN_FILES if t == "test"],
    ids=lambda v: v if isinstance(v, str) else v.name,
)
def test_test_plugin_doc_name_matches_filename(plugin_type, path):
    """Per-test-file layout requires `name: <test_name>` in DOCUMENTATION
    to match the filename stem -- otherwise `ansible-doc -t test
    drzln0.akeyless.<name>` returns nothing."""
    raw = _extract_documentation(path)
    parsed = yaml.safe_load(raw)
    assert parsed.get("name") == path.stem, (
        f"test plugin {path.name}: DOCUMENTATION name={parsed.get('name')!r} "
        f"must equal filename stem {path.stem!r} for ansible-doc resolution"
    )
