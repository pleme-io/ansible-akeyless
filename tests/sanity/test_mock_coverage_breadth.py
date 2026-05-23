# Copyright: (c) 2026, pleme-io
# MIT License
#
# Sanity sweep that pins the BREADTH of mock-server integration
# coverage. Three major helper shapes:
#   - run_standard_crud (157 modules)
#   - run_action_module (26 modules)
#   - run_info_module (25 modules)
# At least one representative for EACH shape must have a mock-server
# lifecycle test. Catches the case where someone adds a new helper
# shape (e.g. a hypothetical run_batch_module) without thinking
# about wire-level integration coverage.
#
# Also pins lookup-plugin wire-level coverage (all 3 lookups must
# have at least one mock-server-style integration test).

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MOCK_DIR = REPO_ROOT / "tests" / "mock"


def _mock_test_text():
    """Concat every mock test file so we can grep for SDK method
    names + module filenames."""
    return "\n".join(p.read_text() for p in MOCK_DIR.glob("test_*.py"))


@pytest.fixture(scope="module")
def mock_corpus():
    return _mock_test_text()


# ---------------------------------------------------------------------------
# Helper-shape coverage
# ---------------------------------------------------------------------------


def test_run_standard_crud_has_mock_lifecycle(mock_corpus):
    """At least one mock-server CRUD lifecycle must exist for the
    run_standard_crud path. Currently covered by:
      - test_role_lifecycle.py
      - test_static_secret_lifecycle.py
      - test_target_db_lifecycle.py
      - test_auth_method_lifecycle.py
      - test_dynamic_secret_lifecycle.py
    """
    # We grep for the canonical CRUD-shape SDK method pairs. Any of
    # these confirms a CRUD lifecycle exists.
    crud_signatures = (
        "get_role",                # role
        "describe_item",           # static_secret
        "target_get",              # target_*
        "get_auth_method",         # auth_method_*
        "dynamic_secret_get",      # dynamic_secret_*
    )
    found = [sig for sig in crud_signatures if sig in mock_corpus]
    assert found, (
        f"no mock-server CRUD lifecycle found in tests/mock/ -- need "
        f"coverage for at least one of {crud_signatures}"
    )


def test_run_action_module_has_mock_lifecycle(mock_corpus):
    """At least one mock-server test for the run_action_module path.
    Currently covered by test_uid_action.py + test_crypto_action_lifecycle.py."""
    action_signatures = (
        "uid_generate_token",
        "uid_rotate_token",
        "encrypt",
        "decrypt",
        "sign_data_with_classic_key",
    )
    found = [sig for sig in action_signatures if sig in mock_corpus]
    assert found, (
        f"no mock-server action test found -- need coverage for at least "
        f"one of {action_signatures}"
    )


def test_run_info_module_has_mock_lifecycle(mock_corpus):
    """At least one mock-server test for run_info_module.
    Currently covered by test_role_info.py."""
    info_signatures = (
        "role_info.py",
        "policies_info.py",
    )
    found = [sig for sig in info_signatures if sig in mock_corpus]
    assert found, (
        f"no mock-server info-module test found -- need coverage for at "
        f"least one of {info_signatures}"
    )


# ---------------------------------------------------------------------------
# Lookup wire-level coverage
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("lookup_name", [
    "secret", "dynamic_secret", "pki_certificate",
])
def test_lookup_has_wire_level_integration_test(lookup_name):
    """Each of the 3 lookup plugins must have at least one mock-server-
    style integration test (not just unit-stub coverage)."""
    # Convention: tests/mock/test_<lookup_name>_lookup_integration.py.
    # The `secret` lookup is the only one whose file name differs
    # slightly (test_secret_lookup_integration.py) because the
    # `secret_lookup` naming predates the per-lookup expansion.
    candidates = (
        MOCK_DIR / f"test_{lookup_name}_lookup_integration.py",
    )
    assert any(p.exists() for p in candidates), (
        f"no mock-server wire-level test for the {lookup_name} lookup. "
        f"Add tests/mock/test_{lookup_name}_lookup_integration.py covering "
        f"the @akeyless_lookup -> fetch() -> SDK path."
    )


# ---------------------------------------------------------------------------
# Per-CRUD-family coverage matrix
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("family,representative_sdk_call", [
    ("role",                   "get_role"),
    ("static_secret",          "describe_item"),
    ("target_*",               "target_get"),
    ("auth_method_*",          "get_auth_method"),
    ("dynamic_secret_*",       "dynamic_secret_get"),
    ("rotated_secret_*",       "rotated_secret_create_postgresql"),
])
def test_module_family_has_lifecycle(mock_corpus, family, representative_sdk_call):
    """The 5 most-used CRUD families each must have a representative
    lifecycle test. Adding a new family means a new lifecycle test
    file (cheap, ~80 LOC) -- this sanity sweep makes the omission
    visible."""
    assert representative_sdk_call in mock_corpus, (
        f"missing mock lifecycle for the {family} family "
        f"(no test references the {representative_sdk_call!r} SDK call)"
    )
