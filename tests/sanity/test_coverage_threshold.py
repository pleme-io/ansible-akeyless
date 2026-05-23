# Copyright: (c) 2026, pleme-io
# MIT License
#
# Coverage-floor sanity. When `pytest-cov` has produced a coverage.xml
# (the coverage-matrix CI workflow always does; local dev runs only
# when explicitly invoked with --cov), assert that the global line
# coverage % isn't below the documented floor. Catches regressions
# where new plugin code lands without tests.
#
# When coverage.xml isn't present (typical local dev) the test SKIPS
# rather than fails -- coverage isn't measured locally by default.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
COVERAGE_XML = REPO_ROOT / "coverage.xml"

# Floor as a percentage. Bump as the test surface grows; never lower.
# Current actual coverage: undetermined until coverage-matrix CI run
# completes. Set the floor conservatively at 80% so existing CI passes
# while still catching catastrophic regressions.
MIN_LINE_COVERAGE_PCT = 80.0


def test_coverage_xml_parseable_or_skipped():
    """When coverage.xml exists it must parse + carry the line-rate
    attribute. When it doesn't, skip (local runs don't measure)."""
    if not COVERAGE_XML.exists():
        pytest.skip(
            "coverage.xml not present -- run pytest with `--cov=plugins "
            "--cov-report=xml` to generate it (the coverage-matrix CI "
            "workflow does this automatically)"
        )
    tree = ET.parse(COVERAGE_XML)
    root = tree.getroot()
    line_rate = root.attrib.get("line-rate")
    assert line_rate is not None, (
        "coverage.xml missing the `line-rate` attribute on its root "
        "element -- pytest-cov should always emit this"
    )


def test_line_coverage_above_floor():
    """Hard fail if coverage.xml exists and reports below the floor."""
    if not COVERAGE_XML.exists():
        pytest.skip("coverage.xml not present (see test_coverage_xml_parseable_or_skipped)")
    tree = ET.parse(COVERAGE_XML)
    root = tree.getroot()
    line_rate_str = root.attrib.get("line-rate", "0")
    try:
        line_rate = float(line_rate_str)
    except ValueError:
        pytest.fail(f"coverage.xml line-rate {line_rate_str!r} isn't a float")
    pct = line_rate * 100.0
    assert pct >= MIN_LINE_COVERAGE_PCT, (
        f"Line coverage {pct:.1f}% below floor of {MIN_LINE_COVERAGE_PCT}%. "
        f"Either add tests for the new uncovered code OR (deliberately) "
        f"lower MIN_LINE_COVERAGE_PCT with a documented reason."
    )
