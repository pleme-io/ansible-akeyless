# Copyright: (c) 2026, pleme-io
# MIT License
#
# Sanity tests for CHANGELOG.md. Keep a Changelog format is human-edited
# (the auto-bump pipeline only stamps galaxy.yml + git tags). Drift between
# galaxy.yml and CHANGELOG silently produces an under-documented release,
# so we pin the basics here.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CHANGELOG = REPO_ROOT / "CHANGELOG.md"
GALAXY_YML = REPO_ROOT / "galaxy.yml"

VERSION_HEADER_RE = re.compile(
    r"^##\s+\[(?P<version>[^\]]+)\](?:\s+[-—]\s+(?P<date>\S+.*?))?\s*$",
    re.MULTILINE,
)


@pytest.fixture(scope="module")
def changelog_text():
    return CHANGELOG.read_text()


@pytest.fixture(scope="module")
def galaxy_version():
    return yaml.safe_load(GALAXY_YML.read_text())["version"]


@pytest.fixture(scope="module")
def version_headers(changelog_text):
    """Collect every `## [version] — date` heading in the changelog."""
    return [
        (m.group("version"), (m.group("date") or "").strip())
        for m in VERSION_HEADER_RE.finditer(changelog_text)
    ]


def test_changelog_exists_and_nonempty(changelog_text):
    assert changelog_text.strip(), "CHANGELOG.md must be non-empty"


def test_changelog_has_unreleased_section(version_headers):
    """Keep a Changelog convention: an [Unreleased] section captures
    in-flight work before the next version stamp. Missing it means a
    PR landed without a docs-side bump and the next release will ship
    silent."""
    versions = [v for v, _ in version_headers]
    assert "Unreleased" in versions, (
        f"CHANGELOG.md missing `## [Unreleased]` heading; "
        f"current top-level versions: {versions}"
    )


def test_changelog_includes_current_galaxy_version_or_unreleased(
    version_headers, galaxy_version
):
    """Either the current galaxy.yml version is documented as a released
    section, OR the version is still listed under [Unreleased]. Anything
    else means CHANGELOG and galaxy.yml have diverged silently.

    Note: '0.2.x' is allowed as an in-flight bucket header for the 0.2
    line (matches anything starting with '0.2.')."""
    versions = [v for v, _ in version_headers]
    if "Unreleased" in versions:
        # OK — pending entries gathered under [Unreleased] is the
        # standard pre-bump state.
        return
    matches_buckets = [
        v
        for v in versions
        if v == galaxy_version
        or (v.endswith(".x") and galaxy_version.startswith(v[:-1]))
    ]
    assert matches_buckets, (
        f"galaxy.yml version {galaxy_version!r} not in CHANGELOG headings "
        f"and no [Unreleased] section; documented: {versions}"
    )


def test_changelog_unreleased_appears_before_releases(changelog_text, version_headers):
    """The [Unreleased] section must be the top-most version heading.
    Putting it below a numbered release inverts the Keep-a-Changelog
    convention and confuses readers about what's pending."""
    versions = [v for v, _ in version_headers]
    if "Unreleased" not in versions:
        pytest.skip("no [Unreleased] section to order-check")
    assert versions[0] == "Unreleased", (
        f"first version heading must be [Unreleased]; got {versions[0]!r}"
    )


def test_changelog_versions_are_semver_or_buckets(version_headers):
    """Every numeric version heading must be SemVer X.Y.Z OR a bucket
    label of the form X.Y.x (an in-flight 0.2.x line). Anything else
    means a typo / inconsistent format."""
    semver = re.compile(r"^\d+\.\d+\.\d+$")
    bucket = re.compile(r"^\d+\.\d+\.x$")
    bad = []
    for v, _ in version_headers:
        if v == "Unreleased":
            continue
        if not (semver.fullmatch(v) or bucket.fullmatch(v)):
            bad.append(v)
    assert not bad, (
        f"CHANGELOG version headings not semver-or-bucket: {bad}; "
        f"expected X.Y.Z or X.Y.x or Unreleased"
    )


def test_changelog_no_placeholder_lines(changelog_text):
    """The Unreleased section often picks up a `- (placeholder)` bullet
    during scaffolding. Strip those before publishing — they ship to
    Galaxy and look unprofessional."""
    placeholder_re = re.compile(r"^\s*-\s*\(?placeholder", re.IGNORECASE | re.MULTILINE)
    matches = placeholder_re.findall(changelog_text)
    assert not matches, (
        f"CHANGELOG.md contains {len(matches)} placeholder bullet(s); "
        f"replace with actual content before release"
    )


def test_changelog_unreleased_section_has_content(changelog_text, version_headers):
    """If [Unreleased] exists it should have at least one body line OR
    be the only section (fresh-init state). An [Unreleased] heading
    followed immediately by another `##` heading means scaffolding,
    not actual deferred work."""
    versions = [v for v, _ in version_headers]
    if "Unreleased" not in versions:
        pytest.skip("no [Unreleased] section to check")

    # Find the [Unreleased] heading and the next ## heading.
    match = re.search(r"^##\s+\[Unreleased\].*$", changelog_text, re.MULTILINE)
    assert match, "[Unreleased] heading regex failed (shouldn't happen)"
    after = changelog_text[match.end():]
    next_section = re.search(r"^##\s+\[", after, re.MULTILINE)
    body = after[: next_section.start()] if next_section else after
    # Strip blank lines and the heading. Body should have something.
    has_substance = any(
        line.strip() and not line.strip().startswith("###")
        for line in body.splitlines()
    )
    if not has_substance:
        # Only OK if there is no other release yet (fresh repo).
        other_versions = [v for v in versions if v != "Unreleased"]
        assert not other_versions, (
            f"[Unreleased] is empty but releases exist {other_versions}; "
            f"either fill it in or remove the heading"
        )
