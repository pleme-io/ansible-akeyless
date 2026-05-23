# Copyright: (c) 2026, pleme-io
# MIT License
#
# Sanity sweep over the DOCUMENTATION YAML of every generated module.
# Catches the patterns that crash antsibull-docs but don't show up at
# argspec time:
#   - empty `options:` block -> parses as None, then `for k, v in
#     options.items()` raises "argument of type 'NoneType' is not iterable"
#   - `no_log: true` under options.<field> -> rejected as `extra_forbidden`
#     by ModuleDocSchema strict mode
#   - DOCUMENTATION YAML that doesn't parse at all

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULES_DIR = REPO_ROOT / "plugins" / "modules"

_DOC_RE = re.compile(
    r"^DOCUMENTATION\s*=\s*[rRuU]?(?P<q>'''|\"\"\")(?P<body>.*?)(?P=q)",
    re.DOTALL | re.MULTILINE,
)


def _module_files():
    return sorted(
        p for p in MODULES_DIR.glob("*.py")
        if p.name != "__init__.py"
    )


def _extract_doc(path: Path) -> str:
    match = _DOC_RE.search(path.read_text())
    if not match:
        return ""
    return match.group("body")


def _parsed_doc(path: Path):
    """Parse the DOCUMENTATION YAML and return the dict (or None)."""
    body = _extract_doc(path)
    if not body.strip():
        return None
    try:
        return yaml.safe_load(body)
    except yaml.YAMLError:
        return "PARSE_ERROR"


# ---------------------------------------------------------------------------
# Per-module DOCUMENTATION shape sanity
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "path",
    _module_files(),
    ids=lambda p: p.name,
)
def test_documentation_block_parses_as_yaml(path):
    """Every module's DOCUMENTATION block must parse to a YAML dict.
    Pickup point for any regression where the generator emits
    something the YAML parser rejects."""
    parsed = _parsed_doc(path)
    assert parsed != "PARSE_ERROR", (
        f"{path.name}: DOCUMENTATION YAML failed to parse"
    )
    assert parsed is not None, (
        f"{path.name}: missing DOCUMENTATION = r'''...''' block"
    )
    assert isinstance(parsed, dict), (
        f"{path.name}: DOCUMENTATION must parse to a dict, got "
        f"{type(parsed).__name__}"
    )


@pytest.mark.parametrize(
    "path",
    _module_files(),
    ids=lambda p: p.name,
)
def test_documentation_options_is_dict_not_none(path):
    """The `options:` key must resolve to a dict (possibly empty) --
    NEVER `None`. An empty `options:` YAML line is the antsibull-docs
    crash trigger ("argument of type 'NoneType' is not iterable")."""
    parsed = _parsed_doc(path)
    if parsed is None or parsed == "PARSE_ERROR":
        pytest.skip("doc didn't parse (covered by earlier test)")
    if "options" not in parsed:
        pytest.skip("module doesn't declare options")
    assert parsed["options"] is not None, (
        f"{path.name}: `options:` parses to None -- crashes antsibull-docs. "
        f"Use `options: {{}}` for empty option dicts."
    )
    assert isinstance(parsed["options"], dict), (
        f"{path.name}: `options:` must be a dict (got "
        f"{type(parsed['options']).__name__})"
    )


@pytest.mark.parametrize(
    "path",
    _module_files(),
    ids=lambda p: p.name,
)
def test_documentation_options_have_no_no_log_key(path):
    """`no_log: true` under options.<field> is rejected by
    antsibull-docs's ModuleDocSchema. The actual no-log behaviour
    comes from the Python argspec entry; the YAML duplicate is a
    docs-schema violation."""
    parsed = _parsed_doc(path)
    if parsed is None or parsed == "PARSE_ERROR":
        pytest.skip("doc didn't parse")
    options = parsed.get("options") or {}
    bad = []
    for opt_name, entry in options.items():
        if isinstance(entry, dict) and "no_log" in entry:
            bad.append(opt_name)
    assert not bad, (
        f"{path.name}: these options carry `no_log:` in DOCUMENTATION "
        f"({bad}); the schema rejects it. Strip the YAML key -- the "
        f"`'no_log': True` argspec entry still does the runtime masking."
    )


@pytest.mark.parametrize(
    "path",
    _module_files(),
    ids=lambda p: p.name,
)
def test_documentation_required_top_level_keys_present(path):
    """Every module needs description + short_description (per
    ansible-test sanity)."""
    parsed = _parsed_doc(path)
    if parsed is None or parsed == "PARSE_ERROR":
        pytest.skip("doc didn't parse")
    required = {"module", "short_description", "author", "description"}
    missing = required - set(parsed.keys())
    assert not missing, (
        f"{path.name}: DOCUMENTATION missing required top-level keys: {missing}"
    )
