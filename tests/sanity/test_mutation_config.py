# Copyright: (c) 2026, pleme-io
# MIT License
#
# Sanity tests for [tool.mutmut] in pyproject.toml. Ensures the
# mutation-test workflow keeps targeting the critical paths even as
# the codebase grows. Catches:
#   - a critical file added to plugins/ that wasn't added to the
#     mutation paths
#   - a target file renamed or removed (stale path = silent mutation
#     skip)
#   - the mutation extra removed from the optional-dependencies block

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from pathlib import Path

import pytest

try:
    import tomllib  # py3.11+
except ImportError:  # pragma: no cover
    import tomli as tomllib

REPO_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = REPO_ROOT / "pyproject.toml"


@pytest.fixture(scope="module")
def config():
    with PYPROJECT.open("rb") as f:
        return tomllib.load(f)


def test_mutation_table_exists(config):
    """`[tool.mutmut]` section must exist so `mutmut run` finds its
    paths_to_mutate without needing a CLI argument."""
    assert "tool" in config
    assert "mutmut" in config["tool"], (
        "pyproject.toml missing [tool.mutmut] section"
    )


def test_paths_to_mutate_set(config):
    mutmut = config["tool"]["mutmut"]
    paths = mutmut.get("paths_to_mutate", "")
    assert paths, "[tool.mutmut] missing paths_to_mutate"


@pytest.mark.parametrize("expected", [
    # Helper module + lookup auth + plugin decorator suite.
    "plugins/module_utils/akeyless_client.py",
    "plugins/module_utils/akeyless_lookup_auth.py",
    "plugins/module_utils/akeyless_plugin_helpers.py",
    # Security-critical: the redactor that's the last line of defense.
    "plugins/callback/akeyless_redactor.py",
    # Filter implementations.
    "plugins/filter/akeyless.py",
    # Lookups.
    "plugins/lookup/secret.py",
    "plugins/lookup/dynamic_secret.py",
    "plugins/lookup/pki_certificate.py",
    # Inventory.
    "plugins/inventory/akeyless.py",
    # Action plugin (handles atomic write of secret).
    "plugins/action/secret_to_file.py",
    # Test plugins.
    "plugins/test/is_akeyless_path.py",
    "plugins/test/is_akeyless_access_id.py",
    "plugins/test/is_pem_block.py",
    "plugins/test/is_base64.py",
])
def test_critical_file_in_mutation_targets(config, expected):
    """Every security/correctness-critical path must be in the
    mutmut sweep. Adding a new such file means a one-line edit to
    [tool.mutmut].paths_to_mutate."""
    paths = config["tool"]["mutmut"]["paths_to_mutate"].split(",")
    paths_normalized = {p.strip() for p in paths}
    assert expected in paths_normalized, (
        f"[tool.mutmut].paths_to_mutate missing {expected!r}; "
        f"add it so the nightly mutation sweep covers this file"
    )


def test_every_targeted_path_exists(config):
    """Every path in mutmut targets must point to an existing file --
    catches a target file rename/move without a corresponding config
    update."""
    paths = config["tool"]["mutmut"]["paths_to_mutate"].split(",")
    missing = []
    for path in paths:
        p = REPO_ROOT / path.strip()
        if not p.exists():
            missing.append(path.strip())
    assert not missing, (
        f"[tool.mutmut].paths_to_mutate references non-existent files: "
        f"{missing}"
    )


def test_mutation_optional_extra_declared(config):
    """The `mutation` optional-dependencies extra must exist so the
    mutation CI workflow can install mutmut via `uv sync --extra mutation`."""
    extras = config.get("project", {}).get("optional-dependencies", {})
    assert "mutation" in extras, (
        "pyproject.toml missing [project.optional-dependencies.mutation] -- "
        "the mutation-test.yml workflow depends on it"
    )
    mutation_deps = extras["mutation"]
    assert any("mutmut" in d for d in mutation_deps), (
        f"mutation extra missing mutmut: {mutation_deps}"
    )


def test_mutation_workflow_file_exists():
    """The mutation testing workflow must exist; pyproject config is
    useless without the CI runner that consumes it."""
    wf = REPO_ROOT / ".github" / "workflows" / "mutation-test.yml"
    assert wf.exists(), (
        ".github/workflows/mutation-test.yml is missing -- "
        "without it the [tool.mutmut] config never runs"
    )
