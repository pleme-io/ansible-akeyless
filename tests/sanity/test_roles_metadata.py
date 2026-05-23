# Copyright: (c) 2026, pleme-io
# MIT License
#
# Sanity tests for every role under roles/. Galaxy's role uploader
# silently accepts roles missing meta/main.yml (treating them as
# generic content) but the Galaxy UI hides them from search results,
# so the role effectively disappears. Catch metadata regressions here
# before they ship.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
ROLES_DIR = REPO_ROOT / "roles"

# Galaxy role metadata required fields (per current Galaxy schema).
REQUIRED_GALAXY_INFO_KEYS = frozenset({
    "role_name", "namespace", "author", "description",
    "license", "min_ansible_version", "platforms", "galaxy_tags",
})

ROLE_DIRS = sorted([d for d in ROLES_DIR.iterdir() if d.is_dir()]) if ROLES_DIR.is_dir() else []


@pytest.fixture(scope="module")
def role_metas():
    """Parse meta/main.yml for every role once per test session."""
    out = {}
    for role_dir in ROLE_DIRS:
        meta_path = role_dir / "meta" / "main.yml"
        if not meta_path.exists():
            out[role_dir.name] = None
            continue
        out[role_dir.name] = yaml.safe_load(meta_path.read_text())
    return out


@pytest.mark.parametrize("role_name", [d.name for d in ROLE_DIRS], ids=str)
def test_role_has_meta_main(role_name, role_metas):
    """Every role must ship a meta/main.yml so Galaxy indexes it."""
    assert role_metas[role_name] is not None, (
        f"roles/{role_name}/meta/main.yml is missing"
    )


@pytest.mark.parametrize("role_name", [d.name for d in ROLE_DIRS], ids=str)
def test_role_meta_has_galaxy_info_block(role_name, role_metas):
    """The top-level `galaxy_info:` block is what Galaxy's role
    importer reads. Missing it means the role uploads but doesn't
    show up in search."""
    meta = role_metas[role_name]
    assert meta is not None
    assert "galaxy_info" in meta, (
        f"roles/{role_name}/meta/main.yml missing top-level galaxy_info block"
    )


@pytest.mark.parametrize("role_name", [d.name for d in ROLE_DIRS], ids=str)
def test_role_galaxy_info_has_required_keys(role_name, role_metas):
    """Every Galaxy-required field present on galaxy_info."""
    meta = role_metas[role_name]
    info = (meta or {}).get("galaxy_info") or {}
    missing = REQUIRED_GALAXY_INFO_KEYS - set(info)
    assert not missing, (
        f"roles/{role_name}/meta/main.yml galaxy_info missing keys: {missing}"
    )


@pytest.mark.parametrize("role_name", [d.name for d in ROLE_DIRS], ids=str)
def test_role_meta_role_name_matches_directory(role_name, role_metas):
    """The role_name in meta/main.yml must match the directory name
    so `ansible-galaxy install` resolves correctly."""
    meta = role_metas[role_name]
    declared = ((meta or {}).get("galaxy_info") or {}).get("role_name")
    assert declared == role_name, (
        f"roles/{role_name}/meta/main.yml declares role_name={declared!r}, "
        f"expected {role_name!r} (directory name)"
    )


@pytest.mark.parametrize("role_name", [d.name for d in ROLE_DIRS], ids=str)
def test_role_has_tasks_main(role_name):
    """tasks/main.yml is the role's entry point; a role without it
    is a no-op the user can't tell apart from a typo."""
    tasks_path = ROLES_DIR / role_name / "tasks" / "main.yml"
    assert tasks_path.exists(), (
        f"roles/{role_name}/tasks/main.yml is missing"
    )


@pytest.mark.parametrize("role_name", [d.name for d in ROLE_DIRS], ids=str)
def test_role_tasks_main_yaml_parses(role_name):
    """The tasks file must be valid YAML and parse to a list."""
    tasks_path = ROLES_DIR / role_name / "tasks" / "main.yml"
    parsed = yaml.safe_load(tasks_path.read_text())
    assert isinstance(parsed, list), (
        f"roles/{role_name}/tasks/main.yml must parse to a list, "
        f"got {type(parsed).__name__}"
    )
    assert len(parsed) > 0, (
        f"roles/{role_name}/tasks/main.yml is an empty list (no tasks)"
    )


@pytest.mark.parametrize("role_name", [d.name for d in ROLE_DIRS], ids=str)
def test_role_meta_namespace_matches_collection(role_name, role_metas):
    """namespace in meta/main.yml must match the collection's
    namespace (drzln0) so role refs resolve as
    `drzln0.akeyless.<role_name>`."""
    info = (role_metas[role_name] or {}).get("galaxy_info") or {}
    assert info.get("namespace") == "drzln0", (
        f"roles/{role_name} galaxy_info.namespace={info.get('namespace')!r}, "
        f"expected 'drzln0' to match the collection namespace"
    )


@pytest.mark.parametrize("role_name", [d.name for d in ROLE_DIRS], ids=str)
def test_role_meta_license_is_gpl3(role_name, role_metas):
    """All roles in this collection use GPL-3.0-or-later (consistent
    with module headers + ansible-core's runtime license)."""
    info = (role_metas[role_name] or {}).get("galaxy_info") or {}
    license_ = info.get("license", "")
    assert "GPL-3.0" in license_ or license_ == "GPL-3.0-or-later", (
        f"roles/{role_name} galaxy_info.license={license_!r}, "
        f"expected 'GPL-3.0-or-later' (matches module headers)"
    )
