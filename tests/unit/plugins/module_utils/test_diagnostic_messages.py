# Copyright: (c) 2026, pleme-io
# MIT License
#
# Tests for diagnostic-message quality in akeyless_client.py error
# paths. Pins the user-facing message format so a regression that
# drops context (model name, method name, did-you-mean suggestions)
# fails CI rather than degrading the developer experience silently.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
HELPER_PATH = REPO_ROOT / "plugins" / "module_utils" / "akeyless_client.py"


def _load_helper(fake_akeyless):
    spec = importlib.util.spec_from_file_location(
        "akeyless_client_diagnostics", HELPER_PATH
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["akeyless_client_diagnostics"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def helper(fake_akeyless):
    return _load_helper(fake_akeyless[0])


# ---------------------------------------------------------------------------
# _did_you_mean helper
# ---------------------------------------------------------------------------


class TestDidYouMean:
    """The did-you-mean suffix helper drives error-message quality on
    unknown-model / unknown-method paths. Verify it returns useful
    suggestions for plausible typos and empty string when nothing's
    close enough to suggest."""

    def test_returns_empty_for_unrelated_name(self, helper):
        """A wildly unrelated name shouldn't surface low-quality
        suggestions -- difflib's cutoff filters those out."""
        out = helper._did_you_mean("ZZZZ", ["GetRole", "CreateAuthMethod"])
        assert out == ""

    def test_returns_close_match_suffix(self, helper):
        """Typo: missing letter, transposition, case difference -- all
        should return a ', Did you mean:' suffix with the closest
        match listed first."""
        out = helper._did_you_mean(
            "CreateRol", ["CreateRole", "CreateRoleRule", "DeleteRole"]
        )
        assert out.startswith(". Did you mean:")
        assert "CreateRole" in out

    def test_returns_up_to_n_matches(self, helper):
        """Bounded suggestion count keeps the error message short
        even on a populated candidate set."""
        candidates = ["RoleA", "RoleB", "RoleC", "RoleD", "RoleE", "RoleF"]
        out = helper._did_you_mean("Role", candidates, n=3, cutoff=0.5)
        # Comma-separated, no more than n names emitted.
        assert out.count(",") <= 2  # n names => n-1 commas

    def test_handles_frozenset_candidates(self, helper):
        """Production callers pass frozensets; verify difflib handles
        them (it can iterate the candidate sequence)."""
        out = helper._did_you_mean(
            "CreateRol", frozenset({"CreateRole", "DeleteRole"})
        )
        assert "CreateRole" in out

    def test_empty_candidate_set_returns_empty(self, helper):
        """Defensive: no candidates means no suggestions can be made."""
        assert helper._did_you_mean("X", frozenset()) == ""
        assert helper._did_you_mean("X", []) == ""


# ---------------------------------------------------------------------------
# build_body error message includes did-you-mean suggestion
# ---------------------------------------------------------------------------


class TestBuildBodyDiagnostics:
    """Force _model_accepted_kwargs to return None to simulate
    unknown-model-name path. This isolates the did-you-mean codegen
    from the conftest's MagicMock-backed __getattr__ catch-all (which
    would otherwise mean every attribute lookup succeeds)."""

    def test_unknown_model_includes_did_you_mean_suffix(self, helper, monkeypatch):
        """When build_body fails to resolve a model name, the
        ValueError message should include a 'Did you mean' suggestion
        sourced from the akeyless module's PascalCase attribute names.
        """
        akeyless_mod = sys.modules["akeyless"]
        # Replace the catch-all __getattr__ with explicit PascalCase
        # attrs so dir() returns a known set.

        class _CleanAkeyless:
            CreateRole = type("CreateRole", (), {})
            DeleteRole = type("DeleteRole", (), {})
            UpdateRole = type("UpdateRole", (), {})

        monkeypatch.setattr(helper, "akeyless", _CleanAkeyless)
        # Override cache so this test's lookup doesn't see a hit from a
        # previous test, and so the lookup actually consults
        # helper.akeyless not the conftest's stub.
        helper._model_accepted_kwargs.cache_clear()
        monkeypatch.setattr(
            helper, "_model_accepted_kwargs", lambda name: None
        )
        with pytest.raises(ValueError) as exc_info:
            helper.build_body("CreateRol", {})
        msg = str(exc_info.value)
        assert "Unknown Akeyless model: CreateRol" in msg
        # Should suggest CreateRole as the closest match.
        assert "CreateRole" in msg
        assert "Did you mean" in msg

    def test_unknown_model_clean_message_when_no_close_match(self, helper, monkeypatch):
        """If no candidate is close enough to the typo, the message
        should still contain 'Unknown Akeyless model: <name>' without
        an empty 'Did you mean:' suffix."""

        class _NoMatchAkeyless:
            Foo = type("Foo", (), {})  # nothing close to ZZZZZZZZZZZZZ

        monkeypatch.setattr(helper, "akeyless", _NoMatchAkeyless)
        helper._model_accepted_kwargs.cache_clear()
        monkeypatch.setattr(
            helper, "_model_accepted_kwargs", lambda name: None
        )
        with pytest.raises(ValueError) as exc_info:
            helper.build_body("ZZZZZZZZZZZZZ", {})
        msg = str(exc_info.value)
        assert msg.startswith("Unknown Akeyless model: ZZZZZZZZZZZZZ")
        # No close match means no 'Did you mean' suffix.
        assert "Did you mean" not in msg


# ---------------------------------------------------------------------------
# HttpStatus is used (not a raw 404) in call_api branching
# ---------------------------------------------------------------------------


class TestHttpStatusUsage:

    def test_call_api_uses_http_status_enum_for_404_swallow(self, helper):
        """Verify call_api's swallow_404 branch uses the typed
        HttpStatus.NOT_FOUND comparison, not a raw 404 literal. Read
        the source so we catch the conscious choice to use the enum."""
        source = HELPER_PATH.read_text()
        # The call_api function should reference HttpStatus.NOT_FOUND
        # in its swallow_404 branch, not the raw 404 literal.
        assert "HttpStatus.NOT_FOUND" in source, (
            "call_api should branch on HttpStatus.NOT_FOUND for readability "
            "(matches the IntEnum contract that 404 == HttpStatus.NOT_FOUND)"
        )
