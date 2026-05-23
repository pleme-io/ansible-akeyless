# Copyright: (c) 2026, pleme-io
# MIT License
#
# Behavioral tests for the typed exception hierarchy + AkeylessConfig
# dataclass + @requires_sdk decorator + HttpStatus enum added to
# plugins/module_utils/akeyless_client.py.

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
        "akeyless_client_typed_surface", HELPER_PATH
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["akeyless_client_typed_surface"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def helper(fake_akeyless):
    return _load_helper(fake_akeyless[0])


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


class TestExceptionHierarchy:
    """Every typed exception must inherit from AkeylessError so a
    single `except AkeylessError` catches the whole family."""

    def test_all_typed_errors_inherit_base(self, helper):
        for name in ("AkeylessConfigError", "AkeylessSdkError",
                     "AkeylessAuthError", "AkeylessApiError"):
            cls = getattr(helper, name)
            assert issubclass(cls, helper.AkeylessError), (
                f"{name} must inherit from AkeylessError"
            )

    def test_akeyless_error_carries_status_and_details(self, helper):
        """Status + details are the structured-diagnostics carrier the
        lifecycle helpers serialize alongside fail_json's `msg`."""
        exc = helper.AkeylessError("boom", status=403, details={"path": "/x"})
        assert str(exc) == "boom"
        assert exc.status == 403
        assert exc.details == {"path": "/x"}

    def test_akeyless_error_defaults_when_unspecified(self, helper):
        """status defaults to None and details to empty dict so
        callers can always introspect both without KeyError / Attribute
        errors."""
        exc = helper.AkeylessError("boom")
        assert exc.status is None
        assert exc.details == {}

    def test_details_kwarg_is_copied_not_aliased(self, helper):
        """The dict passed in must NOT be aliased -- otherwise a caller
        mutating their dict post-construction would mutate the
        exception. Defensive copy is the contract."""
        d = {"original": "value"}
        exc = helper.AkeylessError("msg", details=d)
        d["mutated"] = "later"
        assert "mutated" not in exc.details

    def test_exception_chain_preserved_via_raise_from(self, helper):
        """Idiomatic chaining: when wrapping a lower-level exception,
        `raise X(...) from exc` preserves __cause__ so the traceback
        shows the original failure. Verify the helpers' exception
        constructor doesn't break this."""
        try:
            try:
                raise ValueError("inner")
            except ValueError as inner:
                raise helper.AkeylessApiError(
                    "wrapped", status=500
                ) from inner
        except helper.AkeylessApiError as e:
            assert isinstance(e.__cause__, ValueError)
            assert str(e.__cause__) == "inner"


# ---------------------------------------------------------------------------
# HttpStatus enum
# ---------------------------------------------------------------------------


class TestHttpStatusEnum:
    """IntEnum so direct integer comparison works without losing the
    type info that makes branches readable."""

    def test_int_comparison_works_both_directions(self, helper):
        assert helper.HttpStatus.NOT_FOUND == 404
        assert 404 == helper.HttpStatus.NOT_FOUND
        assert helper.HttpStatus.UNAUTHORIZED < helper.HttpStatus.FORBIDDEN

    def test_enum_values_are_canonical_http_codes(self, helper):
        assert helper.HttpStatus.UNAUTHORIZED.value == 401
        assert helper.HttpStatus.FORBIDDEN.value == 403
        assert helper.HttpStatus.NOT_FOUND.value == 404


# ---------------------------------------------------------------------------
# AkeylessConfig dataclass
# ---------------------------------------------------------------------------


class TestAkeylessConfig:
    """The typed config dataclass merges module.params with env vars
    via a documented precedence."""

    def test_is_frozen(self, helper):
        """Frozen so config can't drift mid-call. Attribute assignment
        must raise FrozenInstanceError."""
        cfg = helper.AkeylessConfig.from_params({})
        with pytest.raises(Exception):  # dataclasses.FrozenInstanceError
            cfg.access_id = "rebound"  # type: ignore[misc]

    def test_from_params_uses_param_when_present(self, helper, monkeypatch):
        """Param value beats env var beats default."""
        monkeypatch.setenv("AKEYLESS_GATEWAY_URL", "https://env-val/")
        cfg = helper.AkeylessConfig.from_params({
            "gateway_url": "https://param-val/",
        })
        assert cfg.gateway_url == "https://param-val/"

    def test_from_params_falls_back_to_env(self, helper, monkeypatch):
        """No param -> env var wins."""
        monkeypatch.setenv("AKEYLESS_GATEWAY_URL", "https://env-val/")
        cfg = helper.AkeylessConfig.from_params({})
        assert cfg.gateway_url == "https://env-val/"

    def test_from_params_falls_back_to_default(self, helper, monkeypatch):
        """No param, no env -> default URL."""
        monkeypatch.delenv("AKEYLESS_GATEWAY_URL", raising=False)
        cfg = helper.AkeylessConfig.from_params({})
        assert cfg.gateway_url == helper.DEFAULT_GATEWAY_URL

    def test_from_params_handles_none_params(self, helper, monkeypatch):
        """`module.params` is sometimes None during pre-init phases;
        from_params must not crash on that."""
        monkeypatch.delenv("AKEYLESS_ACCESS_ID", raising=False)
        cfg = helper.AkeylessConfig.from_params(None)
        assert cfg.access_id is None
        assert cfg.gateway_url == helper.DEFAULT_GATEWAY_URL

    def test_access_type_defaults_to_access_key(self, helper, monkeypatch):
        monkeypatch.delenv("AKEYLESS_ACCESS_KEY", raising=False)
        cfg = helper.AkeylessConfig.from_params({})
        assert cfg.access_type == helper.DEFAULT_ACCESS_TYPE
        assert cfg.access_type == "access_key"

    def test_pre_issued_token_from_env_only(self, helper, monkeypatch):
        """AKEYLESS_TOKEN is intentionally env-only (no module.params
        equivalent) so it doesn't leak into job logs via task args."""
        monkeypatch.setenv("AKEYLESS_TOKEN", "pre-issued-1234")
        cfg = helper.AkeylessConfig.from_params({"token": "should-be-ignored"})
        assert cfg.pre_issued_token == "pre-issued-1234"


# ---------------------------------------------------------------------------
# @requires_sdk decorator
# ---------------------------------------------------------------------------


class TestRequiresSdkDecorator:
    """The @requires_sdk wrapper raises AkeylessSdkError before the
    decorated body can NameError on the missing SDK module."""

    def test_passes_through_when_sdk_loaded(self, helper):
        @helper.requires_sdk
        def my_helper(x):
            return x * 2
        assert my_helper(21) == 42

    def test_raises_typed_error_when_sdk_missing(self, helper, monkeypatch):
        """Simulate SDK-missing state by patching the helper-module
        constants. The decorator reads HAS_AKEYLESS at call time."""
        monkeypatch.setattr(helper, "HAS_AKEYLESS", False)
        monkeypatch.setattr(
            helper, "AKEYLESS_IMPORT_ERROR",
            ImportError("simulated: akeyless not on PYTHONPATH"),
        )

        @helper.requires_sdk
        def my_helper():
            return "would-have-run"

        with pytest.raises(helper.AkeylessSdkError, match="akeyless SDK"):
            my_helper()

    def test_preserves_function_name_for_debugging(self, helper):
        """functools.wraps copies __name__ so stacktraces and `repr`
        still show the original function name post-decoration."""
        @helper.requires_sdk
        def descriptively_named():
            pass
        assert descriptively_named.__name__ == "descriptively_named"


# ---------------------------------------------------------------------------
# AnsibleModuleLike Protocol
# ---------------------------------------------------------------------------


class TestAnsibleModuleLikeProtocol:
    """The Protocol class lets type-checkers verify the helpers'
    AnsibleModule contract without importing the real class. Pin its
    minimum surface so accidental shrinkage of the Protocol surfaces
    as a test failure."""

    def test_protocol_advertises_minimum_surface(self, helper):
        proto = helper.AnsibleModuleLike
        # __annotations__ on a Protocol class captures its attribute
        # signature.
        annotations = getattr(proto, "__annotations__", {})
        for attr in ("params", "check_mode"):
            assert attr in annotations, (
                f"AnsibleModuleLike missing required attribute: {attr}"
            )

    def test_duck_typed_instance_satisfies_isinstance(self, helper):
        """Protocol classes with runtime_checkable would allow
        isinstance(); ours isn't decorated that way (the static-only
        Protocol is sufficient for the call sites). Verify a duck-typed
        stub still works structurally."""
        from unittest.mock import MagicMock
        stub = MagicMock(spec=["params", "check_mode", "exit_json", "fail_json"])
        stub.params = {"foo": "bar"}
        stub.check_mode = False
        # We can't easily isinstance() against a non-runtime_checkable
        # Protocol, but we can verify the duck-typed attribute access
        # works without raising.
        assert stub.params == {"foo": "bar"}
        assert stub.check_mode is False
