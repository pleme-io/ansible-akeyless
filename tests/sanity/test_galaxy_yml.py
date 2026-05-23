# Copyright: (c) 2026, pleme-io
# MIT License
#
# Sanity tests for galaxy.yml -- the collection manifest. Galaxy rejects
# missing required fields silently at upload time (returns 200 but the
# collection never appears), so we pin the invariants here BEFORE the
# auto-bump pipeline reads the file.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
GALAXY_YML = REPO_ROOT / "galaxy.yml"

# Galaxy CLI validation rejects an upload missing any of these. Adding
# a new required key here is fine; removing one would be a Galaxy
# compatibility break.
REQUIRED_KEYS = frozenset({
    "namespace", "name", "version", "readme", "authors", "description",
    "license", "repository", "documentation", "homepage", "issues",
    "dependencies", "tags",
})

# Semver-ish pattern -- Galaxy accepts X.Y.Z plus pre-release identifiers
# (e.g. 0.2.0-rc1). substrate-bump's increment never produces pre-release
# tags so the simple form is sufficient here.
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:-[\w.]+)?$")


@pytest.fixture(scope="module")
def manifest():
    """Parse galaxy.yml once per test session."""
    text = GALAXY_YML.read_text()
    return yaml.safe_load(text)


def test_galaxy_yml_exists_and_parses(manifest):
    """Sanity: the file must be valid YAML and resolve to a dict."""
    assert isinstance(manifest, dict), (
        f"galaxy.yml must parse to a top-level dict, got {type(manifest).__name__}"
    )


def test_galaxy_yml_has_all_required_keys(manifest):
    """Every key Galaxy's upload-validate step checks must be present."""
    missing = REQUIRED_KEYS - set(manifest)
    assert not missing, f"galaxy.yml missing required keys: {missing}"


def test_galaxy_yml_version_is_semver(manifest):
    """The auto-bump pipeline increments patch via substrate-bump; if
    galaxy.yml carries a non-semver value the bump step silently fails
    and the next release ships with the old version."""
    version = manifest["version"]
    assert isinstance(version, str), f"version must be a string, got {type(version).__name__}"
    assert SEMVER_RE.fullmatch(version), (
        f"version={version!r} is not semver (expected X.Y.Z or X.Y.Z-pre)"
    )


def test_galaxy_yml_namespace_matches_publishing_target(manifest):
    """Pin the namespace so an accidental edit doesn't redirect publishes
    to a different (likely unowned) Galaxy account. Changing this is a
    deliberate decision documented in provider.toml's
    [platforms.ansible] galaxy_namespace -- if the spec source says
    'drzln0', galaxy.yml had better say 'drzln0' too."""
    assert manifest["namespace"] == "drzln0", (
        f"namespace pinned to 'drzln0'; got {manifest['namespace']!r}. "
        f"To intentionally change the publishing target, edit BOTH "
        f"akeyless-terraform-resources/provider.toml AND this test."
    )


def test_galaxy_yml_name_matches_collection(manifest):
    """Collection name pinned. Same change-surface argument as namespace."""
    assert manifest["name"] == "akeyless"


def test_galaxy_yml_dependencies_is_dict(manifest):
    """Galaxy treats `dependencies: null` and `dependencies: {}` very
    differently -- the former rejects the upload with a cryptic
    'dependencies must be a dict' message. Pin to dict."""
    deps = manifest.get("dependencies")
    assert isinstance(deps, dict), (
        f"dependencies must be a dict (got {type(deps).__name__}); "
        f"use `dependencies: {{}}` for none"
    )


def test_galaxy_yml_authors_is_nonempty_list(manifest):
    """Galaxy displays the authors list on the collection's page; an
    empty list shows an awkward placeholder. Pin to non-empty."""
    authors = manifest.get("authors")
    assert isinstance(authors, list) and len(authors) > 0, (
        f"authors must be a non-empty list, got {authors!r}"
    )


def test_galaxy_yml_license_is_list(manifest):
    """Galaxy's docs require licenses as a list (even for a single
    license). Strings are silently accepted but inconsistent with the
    schema."""
    license_ = manifest.get("license")
    assert isinstance(license_, list) and len(license_) > 0, (
        f"license must be a non-empty list, got {license_!r}"
    )


def test_galaxy_yml_tags_include_security(manifest):
    """tags drive Galaxy search ranking. The minimum set we want this
    collection found for: security (the broad category) + secrets +
    akeyless (the brand)."""
    required_tags = {"security", "secrets", "akeyless"}
    actual = set(manifest.get("tags", []))
    missing = required_tags - actual
    assert not missing, (
        f"galaxy.yml tags missing {missing}; Galaxy search ranking depends on these"
    )
