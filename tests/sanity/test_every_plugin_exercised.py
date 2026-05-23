# Copyright: (c) 2026, pleme-io
# MIT License
#
# Sanity sweep: every non-module plugin file must be referenced from
# at least one test file. Catches the case where someone adds a new
# plugin without any test coverage AND the case where someone deletes
# a plugin but leaves the test files orphaned.
#
# Note: per-module test coverage is enforced separately (see the
# 209-module test_every_module_loads.py + the per-family lifecycle
# tests). This sanity sweep focuses on the hand-written non-module
# plugin surface where each file is bespoke and a missed test is
# more likely to slip.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PLUGINS_DIR = REPO_ROOT / "plugins"
TESTS_DIR = REPO_ROOT / "tests"


# Plugin file -> list of test-file substrings that count as "exercising"
# it. Most plugins are exercised by a test that names them in
# `spec_from_file_location` or imports them by filename; that's what
# we grep for.
def _plugin_files():
    """Yield every non-module plugin .py file."""
    for type_dir in (
        PLUGINS_DIR / "lookup",
        PLUGINS_DIR / "inventory",
        PLUGINS_DIR / "callback",
        PLUGINS_DIR / "test",
        PLUGINS_DIR / "cache",
        PLUGINS_DIR / "action",
        PLUGINS_DIR / "filter",
        PLUGINS_DIR / "module_utils",
    ):
        if not type_dir.exists():
            continue
        for path in sorted(type_dir.glob("*.py")):
            if path.name == "__init__.py":
                continue
            yield path


PLUGIN_FILES = list(_plugin_files())


def _test_corpus():
    """Concat every test file in tests/unit + tests/sanity + tests/mock
    + tests/openapi -- the layers that can plausibly reference a plugin."""
    out = []
    for sub in ("unit", "sanity", "mock", "openapi"):
        d = TESTS_DIR / sub
        if not d.exists():
            continue
        for p in d.rglob("*.py"):
            try:
                out.append(p.read_text())
            except OSError:
                continue
    return "\n".join(out)


@pytest.fixture(scope="module")
def test_corpus():
    return _test_corpus()


# Per-filter wrapper files are simple re-exports from
# plugins/filter/akeyless.py with their own DOCUMENTATION block.
# They're tested indirectly via:
#   - tests/sanity/test_filter_per_file_structure.py (per-file
#     structure pinned, names derived dynamically from
#     FilterModule.filters())
#   - tests/sanity/test_plugin_docs.py (DOCUMENTATION YAML sanity)
#   - tests/mock/test_every_plugin_loads.py (instantiability)
# Excluded from the per-name-grep sanity below.
_PER_FILTER_WRAPPERS = frozenset({
    "b64decode_secret.py", "parse_dotenv_secret.py",
    "secret_to_json.py", "split_pem_bundle.py",
    "secret_keys_to_env.py", "mask_secret.py", "secret_strength.py",
})


@pytest.mark.parametrize(
    "plugin_path",
    PLUGIN_FILES,
    ids=lambda p: f"{p.parent.name}/{p.name}",
)
def test_plugin_referenced_by_at_least_one_test(test_corpus, plugin_path):
    """The plugin's filename (e.g. `akeyless_redactor.py`) must
    appear in at least one test file. Catches the dead-code-plugin
    case where someone adds plugins/<type>/<new>.py without any
    accompanying test."""
    needle = plugin_path.name
    if (
        plugin_path.parent.name == "filter"
        and needle in _PER_FILTER_WRAPPERS
    ):
        pytest.skip(
            "per-filter wrapper -- coverage via the structural / docs / "
            "load sanity tests (see _PER_FILTER_WRAPPERS comment)"
        )
    assert needle in test_corpus, (
        f"plugins/{plugin_path.parent.name}/{needle} is not referenced "
        f"by any test in tests/unit, tests/sanity, tests/mock, or "
        f"tests/openapi. Either add a test or remove the dead file."
    )


# Specifically guard the highest-value plugins -- they need actual
# functional coverage beyond a bare reference.
HIGH_VALUE_PLUGINS = {
    "akeyless_client.py":         ("tests/unit/plugins/module_utils",),
    "akeyless_lookup_auth.py":    ("tests/unit/plugins/module_utils/test_lookup_auth",),
    "akeyless_plugin_helpers.py": ("tests/unit/plugins/module_utils/test_plugin_helpers",),
    "akeyless_redactor.py":       ("tests/unit/plugins/callback",),
    "akeyless_token.py":          ("tests/unit/plugins/cache",),
    "secret.py":                  ("tests/mock/test_secret_lookup_integration",),
    "dynamic_secret.py":          ("tests/mock/test_dynamic_secret_lookup_integration",),
    "pki_certificate.py":         ("tests/mock/test_pki_certificate_lookup_integration",),
    "secret_to_file.py":          ("tests/unit/plugins/action/test_secret_to_file",),
}


@pytest.mark.parametrize("plugin,required_test_hints", sorted(HIGH_VALUE_PLUGINS.items()))
def test_high_value_plugin_has_dedicated_test(test_corpus, plugin, required_test_hints):
    """The plugins that handle secret values directly (helper / auth /
    decorators / redactor / cache / lookups / action plugin) must have
    a DEDICATED test file -- not just an incidental reference somewhere."""
    found = False
    for hint in required_test_hints:
        # Check for the test file path AS a substring of the test
        # corpus (the corpus contains every test file's text, so any
        # test file containing an `import` or `spec_from_file_location`
        # for the plugin counts).
        if hint in test_corpus:
            found = True
            break
        # Also check if the test path stem exists.
        if any(p.exists() for p in [
            REPO_ROOT / f"{hint}.py",
        ]):
            found = True
            break
    assert found, (
        f"high-value plugin {plugin!r} should have a dedicated test "
        f"file (one of: {required_test_hints}). Without it, regressions "
        f"in this code path only surface in the live-gateway workflow."
    )
