# Copyright: (c) 2026, pleme-io
# MIT License
#
# Sanity tests for README.md. The README is the collection's public face
# on Galaxy + GitHub; if its counts and pin examples drift from reality
# we look stale on a docs-only PR. These checks pin the README to the
# current state of the repo.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
README = REPO_ROOT / "README.md"
GALAXY_YML = REPO_ROOT / "galaxy.yml"
MODULES_DIR = REPO_ROOT / "plugins" / "modules"
LOOKUP_DIR = REPO_ROOT / "plugins" / "lookup"
FILTER_DIR = REPO_ROOT / "plugins" / "filter"
TEST_DIR = REPO_ROOT / "plugins" / "test"


@pytest.fixture(scope="module")
def readme_text():
    return README.read_text()


@pytest.fixture(scope="module")
def galaxy_version():
    return yaml.safe_load(GALAXY_YML.read_text())["version"]


def _modules_count():
    """Count generated module files (excluding __init__.py)."""
    return sum(
        1
        for p in MODULES_DIR.glob("*.py")
        if p.name != "__init__.py"
    )


def _lookup_count():
    return sum(
        1
        for p in LOOKUP_DIR.glob("*.py")
        if p.name != "__init__.py"
    )


def _test_plugin_count():
    """Per-test files (split for ansible-doc resolution). Skip __init__."""
    return sum(
        1
        for p in TEST_DIR.glob("*.py")
        if p.name not in ("__init__.py", "akeyless.py")
    )


def test_readme_exists_and_nonempty(readme_text):
    assert readme_text.strip(), "README.md must be non-empty"


def test_readme_module_count_matches_reality(readme_text):
    """`Modules (CRUD, action, info) | **N** | plugins/modules/` must
    name the actual number of generated module files. Stale claims here
    are the first thing reviewers notice."""
    actual = _modules_count()
    match = re.search(
        r"\|\s*Modules\s*\(CRUD,\s*action,\s*info\)\s*\|\s*\*\*(\d+)\*\*\s*\|",
        readme_text,
    )
    assert match, (
        "README missing the 'Modules (CRUD, action, info) | **N**' row "
        "in the 'What ships' table"
    )
    claimed = int(match.group(1))
    assert claimed == actual, (
        f"README claims {claimed} modules; plugins/modules/ has {actual}. "
        f"Update the 'What ships' row."
    )


def test_readme_header_module_count_matches_reality(readme_text):
    """The README's opening paragraph quotes a module count too. Pin
    both to the same number so a docs PR doesn't ship a contradiction."""
    actual = _modules_count()
    match = re.search(r"(\d+)\s+modules\s+at\s+100%\s+V2\s+SDK", readme_text)
    assert match, "README opener missing 'N modules at 100% V2 SDK ...'"
    claimed = int(match.group(1))
    assert claimed == actual, (
        f"README opener claims {claimed} modules; actual: {actual}"
    )


def test_readme_lookup_count_matches_reality(readme_text):
    """The 'What ships' row for lookups must match plugins/lookup/."""
    actual = _lookup_count()
    match = re.search(
        r"\|\s*Lookup\s*plugins?\s*\|\s*(\d+)\s*\|",
        readme_text,
    )
    assert match, "README missing 'Lookup plugin(s) | N' row"
    claimed = int(match.group(1))
    assert claimed == actual, (
        f"README claims {claimed} lookups; plugins/lookup/ has {actual}"
    )


def test_readme_test_plugin_count_matches_reality(readme_text):
    """One-file-per-test plugin layout. The README's count must match
    the count of per-test files."""
    actual = _test_plugin_count()
    match = re.search(
        r"\|\s*Test\s*plugins\s*\|\s*(\d+)\s*\|",
        readme_text,
    )
    assert match, "README missing 'Test plugins | N' row"
    claimed = int(match.group(1))
    assert claimed == actual, (
        f"README claims {claimed} test plugins; plugins/test/ has {actual} "
        f"per-test files"
    )


def test_readme_pin_example_is_present_and_well_formed(readme_text, galaxy_version):
    """The README must show a version-pin example so new users know
    how to pin in requirements.yml. We accept either:

      - a major.minor range (`>=0.2,<0.3`) -- preferred because patches
        get auto-published every few hours via the auto-bump pipeline
        and a `==0.2.X` pin goes stale on every release; OR
      - a strict `==X.Y.Z` pin whose major.minor matches galaxy.yml's
        major.minor (patch-level drift allowed, since users
        intentionally pinning to a specific patch can lag).

    A nailed-to-exact-galaxy `==X.Y.Z` pin was tried first; it broke
    the sanity check on every auto-bump because the README wasn't
    edited in lockstep. Major.minor matching is the right contract.
    """
    range_match = re.search(
        r"version:\s*['\"]>=\s*(\d+\.\d+)\s*,\s*<\s*(\d+\.\d+)['\"]",
        readme_text,
    )
    strict_match = re.search(
        r"version:\s*['\"]==(\d+\.\d+)\.(\d+)['\"]",
        readme_text,
    )
    assert range_match or strict_match, (
        "README missing a `version: '...'` pin example; users need an "
        "example to copy into requirements.yml"
    )

    galaxy_major_minor = ".".join(galaxy_version.split(".")[:2])
    if range_match:
        # Must include galaxy's current major.minor.
        lower = range_match.group(1)
        upper = range_match.group(2)
        # Naive: lower <= galaxy_major_minor < upper, lexicographic ok for X.Y
        assert (
            tuple(int(p) for p in lower.split("."))
            <= tuple(int(p) for p in galaxy_major_minor.split("."))
            < tuple(int(p) for p in upper.split("."))
        ), (
            f"README range pin '>= {lower}, < {upper}' does not cover "
            f"galaxy.yml's current {galaxy_major_minor}.x line"
        )
    else:
        pinned_major_minor = strict_match.group(1)
        assert pinned_major_minor == galaxy_major_minor, (
            f"README strict pin is v{pinned_major_minor}.X but galaxy.yml is "
            f"on v{galaxy_major_minor}.X. Update the README example (or "
            f"switch to a range pin like '>=0.2,<0.3' that absorbs auto-bumps)"
        )


def test_readme_mentions_each_plugin_type(readme_text):
    """The README must mention every plugin type we ship. New plugin
    types tend to land without README updates -- pin them so the omission
    fails CI rather than going unnoticed."""
    required_phrases = {
        "lookup": "lookup",
        "inventory": "inventory",
        "filter": "filter",
        "test": " test ",  # avoid matching 'tests'
        "callback": "callback",
        "action": "action",
        "cache": "cache",
        "roles": "role",
    }
    lowered = readme_text.lower()
    missing = [
        label
        for label, phrase in required_phrases.items()
        if phrase not in lowered
    ]
    assert not missing, (
        f"README does not mention these plugin types: {missing}"
    )


def test_readme_install_uses_correct_namespace(readme_text):
    """The install snippet must say `ansible-galaxy collection install
    drzln0.akeyless`. Anyone copy-pasting an outdated namespace into
    `ansible-galaxy install` gets a 404 from Galaxy."""
    match = re.search(
        r"ansible-galaxy\s+collection\s+install\s+(\S+)",
        readme_text,
    )
    assert match, "README missing 'ansible-galaxy collection install' line"
    target = match.group(1)
    assert target == "drzln0.akeyless", (
        f"README install line targets {target!r}; expected 'drzln0.akeyless'"
    )
