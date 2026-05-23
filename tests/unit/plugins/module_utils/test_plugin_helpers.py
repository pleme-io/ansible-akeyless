# Copyright: (c) 2026, pleme-io
# MIT License
#
# Unit tests for plugins/module_utils/akeyless_plugin_helpers.py.
# Covers the decorator suite that DRYs lookup / filter / test plugin
# boilerplate.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import importlib.util
import sys
import types
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
HELPERS_PATH = REPO_ROOT / "plugins" / "module_utils" / "akeyless_plugin_helpers.py"
LOOKUP_AUTH_PATH = REPO_ROOT / "plugins" / "module_utils" / "akeyless_lookup_auth.py"


# ---------------------------------------------------------------------------
# Stub installers (idempotent / additive: avoid clobbering sibling tests)
# ---------------------------------------------------------------------------


def _install_ansible_errors_stub():
    """Register ansible.errors with the exception classes the
    decorators raise. Idempotent merge across sibling stub installers."""
    ansible_pkg = sys.modules.setdefault("ansible", types.ModuleType("ansible"))
    errors_mod = sys.modules.get("ansible.errors")
    if errors_mod is None:
        errors_mod = types.ModuleType("ansible.errors")
        sys.modules["ansible.errors"] = errors_mod
        ansible_pkg.errors = errors_mod

    for cls_name in ("AnsibleError", "AnsibleLookupError", "AnsibleFilterError"):
        if not hasattr(errors_mod, cls_name):
            setattr(errors_mod, cls_name, type(cls_name, (Exception,), {}))


def _install_lookup_base_stub():
    """Stub ansible.plugins.lookup.LookupBase so @akeyless_lookup can
    decorate a class that mocks the get_option/set_options surface."""
    ansible_pkg = sys.modules.setdefault("ansible", types.ModuleType("ansible"))
    plugins_pkg = sys.modules.setdefault(
        "ansible.plugins", types.ModuleType("ansible.plugins")
    )
    ansible_pkg.plugins = plugins_pkg
    lookup_mod = sys.modules.setdefault(
        "ansible.plugins.lookup", types.ModuleType("ansible.plugins.lookup")
    )
    plugins_pkg.lookup = lookup_mod
    if not hasattr(lookup_mod, "LookupBase"):
        class _LookupBase:
            def set_options(self, *_, **__):
                pass

            def get_option(self, name):
                return getattr(self, f"_opt_{name}", None)
        lookup_mod.LookupBase = _LookupBase


def _install_akeyless_sdk_stub():
    """Provide akeyless.exceptions.ApiException so the lookup decorator
    can catch it without the real SDK installed."""
    akeyless_mod = sys.modules.setdefault("akeyless", types.ModuleType("akeyless"))
    exceptions_mod = sys.modules.setdefault(
        "akeyless.exceptions", types.ModuleType("akeyless.exceptions")
    )
    akeyless_mod.exceptions = exceptions_mod
    if not hasattr(exceptions_mod, "ApiException"):
        class _ApiException(Exception):
            def __init__(self, status=500, body="", reason=""):
                super().__init__(body or reason)
                self.status = status
                self.body = body
                self.reason = reason
        exceptions_mod.ApiException = _ApiException


# ---------------------------------------------------------------------------
# Loader fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def helpers():
    _install_ansible_errors_stub()
    _install_lookup_base_stub()
    _install_akeyless_sdk_stub()

    # Pre-install a stub for the lookup_auth helper so the decorator's
    # lazy import resolves without the real ansible_collections layout.
    fake_auth_mod = types.ModuleType(
        "ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_lookup_auth"
    )
    def _fake_authenticated_client(opts):
        return (opts.get("_fake_client"), opts.get("token") or "FAKE-TOKEN")
    fake_auth_mod.authenticated_client = _fake_authenticated_client
    # Build the path-style fake module hierarchy so the absolute import resolves.
    for parent in (
        "ansible_collections",
        "ansible_collections.drzln0",
        "ansible_collections.drzln0.akeyless",
        "ansible_collections.drzln0.akeyless.plugins",
        "ansible_collections.drzln0.akeyless.plugins.module_utils",
    ):
        sys.modules.setdefault(parent, types.ModuleType(parent))
    sys.modules[
        "ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_lookup_auth"
    ] = fake_auth_mod

    spec = importlib.util.spec_from_file_location(
        "akeyless_plugin_helpers_under_test", HELPERS_PATH
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------


class TestNormalizeSdkResult:

    def test_calls_to_dict_when_present(self, helpers):
        class FakeModel:
            def to_dict(self):
                return {"a": 1}
        assert helpers.normalize_sdk_result(FakeModel()) == {"a": 1}

    def test_passes_through_plain_dict(self, helpers):
        assert helpers.normalize_sdk_result({"a": 1}) == {"a": 1}

    def test_passes_through_string(self, helpers):
        assert helpers.normalize_sdk_result("plain-value") == "plain-value"

    def test_passes_through_none(self, helpers):
        assert helpers.normalize_sdk_result(None) is None


class TestCompactKwargs:

    def test_drops_none(self, helpers):
        opts = {"a": 1, "b": None, "c": "x"}
        assert helpers.compact_kwargs(opts, ("a", "b", "c")) == {"a": 1, "c": "x"}

    def test_drops_empty_string(self, helpers):
        opts = {"a": "x", "b": ""}
        assert helpers.compact_kwargs(opts, ("a", "b")) == {"a": "x"}

    def test_skips_missing_keys(self, helpers):
        opts = {"a": 1}
        assert helpers.compact_kwargs(opts, ("a", "missing")) == {"a": 1}

    def test_zero_is_kept(self, helpers):
        """0 is a legit value (e.g. ttl=0 = unlimited). Don't drop it."""
        opts = {"a": 0}
        assert helpers.compact_kwargs(opts, ("a",)) == {"a": 0}

    def test_false_is_kept(self, helpers):
        """False is a legit boolean. Don't drop it."""
        opts = {"a": False}
        assert helpers.compact_kwargs(opts, ("a",)) == {"a": False}


# ---------------------------------------------------------------------------
# @akeyless_lookup class decorator
# ---------------------------------------------------------------------------


class _FakeApiException(Exception):
    def __init__(self, status, body):
        super().__init__(body)
        self.status = status
        self.body = body
        self.reason = body


def _make_lookup_class(helpers, *, per_term=True, extra_opts=(), fetch_impl=None):
    """Build a fresh @akeyless_lookup-decorated class with a stub
    LookupBase parent and configurable fetch implementation."""
    LookupBase = sys.modules["ansible.plugins.lookup"].LookupBase
    fetch_fn = fetch_impl or (lambda self, client, token, opts, term: f"value-{term}")

    # Build the class via type() so we can inject the closure-captured
    # `fetch_fn` as a method without Python's class-scoping rules
    # shadowing it (`fetch = fetch_fn` inside `class` body doesn't
    # see the outer name).
    body = {
        "fetch": fetch_fn,
        "get_option": lambda self, name: getattr(self, f"_opt_{name}", None),
    }
    cls = type("_Lookup", (LookupBase,), body)
    return helpers.akeyless_lookup(per_term=per_term, extra_opts=extra_opts)(cls)


class TestAkeylessLookupClassDecorator:

    def test_injects_run_method(self, helpers):
        cls = _make_lookup_class(helpers)
        assert callable(cls.run), "@akeyless_lookup must inject a run method"

    def test_missing_fetch_method_raises_at_decoration(self, helpers):
        LookupBase = sys.modules["ansible.plugins.lookup"].LookupBase
        with pytest.raises(TypeError, match="missing required method"):
            @helpers.akeyless_lookup()
            class _Bad(LookupBase):
                pass  # no `fetch` method

    def test_per_term_returns_list_aligned_to_input(self, helpers):
        cls = _make_lookup_class(helpers)
        result = cls().run(terms=["a", "b", "c"])
        assert result == ["value-a", "value-b", "value-c"]

    def test_per_term_normalises_to_dict_models(self, helpers):
        class _Model:
            def __init__(self, v): self._v = v
            def to_dict(self): return {"k": self._v}

        cls = _make_lookup_class(
            helpers,
            fetch_impl=lambda self, c, t, o, term: _Model(term),
        )
        assert cls().run(terms=["x", "y"]) == [{"k": "x"}, {"k": "y"}]

    def test_api_exception_per_term_translated_with_term_in_context(self, helpers):
        AnsibleLookupError = sys.modules["ansible.errors"].AnsibleLookupError
        ApiException = sys.modules["akeyless.exceptions"].ApiException

        def fetch(self, c, t, o, term):
            raise ApiException(status=403, body="forbidden")

        cls = _make_lookup_class(helpers, fetch_impl=fetch)
        with pytest.raises(AnsibleLookupError, match=r"403.*forbidden"):
            cls().run(terms=["bad"])

    def test_api_exception_includes_call_label(self, helpers):
        """The translated error must mention the fetch method name +
        the term it failed on -- otherwise users hit "Akeyless API
        failed" with no idea which secret broke."""
        AnsibleLookupError = sys.modules["ansible.errors"].AnsibleLookupError
        ApiException = sys.modules["akeyless.exceptions"].ApiException

        def fetch(self, c, t, o, term):
            raise ApiException(status=404, body="not-found")

        cls = _make_lookup_class(helpers, fetch_impl=fetch)
        with pytest.raises(AnsibleLookupError, match=r"fetch\('bad'\).*404"):
            cls().run(terms=["bad"])

    def test_batch_mode_calls_fetch_once_with_full_terms(self, helpers):
        calls = []

        def fetch(self, c, t, o, terms):
            calls.append(list(terms))
            return ["a-result", "b-result"]

        cls = _make_lookup_class(helpers, per_term=False, fetch_impl=fetch)
        result = cls().run(terms=["a", "b"])
        assert calls == [["a", "b"]]
        assert result == ["a-result", "b-result"]

    def test_run_method_passes_auth_opts_into_authenticated_client(self, helpers, monkeypatch):
        captured = {}

        def _capture(opts):
            captured.update(opts)
            return ("FAKE_CLIENT", "FAKE_TOKEN")

        monkeypatch.setattr(
            sys.modules[
                "ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_lookup_auth"
            ],
            "authenticated_client",
            _capture,
        )

        cls = _make_lookup_class(helpers, extra_opts=("custom_arg",))
        instance = cls()
        instance._opt_gateway_url = "https://example.com"
        instance._opt_access_id = "p-abc"
        instance._opt_custom_arg = "hello"
        instance.run(terms=["t"])

        assert captured["gateway_url"] == "https://example.com"
        assert captured["access_id"] == "p-abc"
        assert captured["custom_arg"] == "hello"


# ---------------------------------------------------------------------------
# @akeyless_filter function decorator
# ---------------------------------------------------------------------------


class TestAkeylessFilterDecorator:

    def test_wraps_function_preserves_name(self, helpers):
        @helpers.akeyless_filter
        def my_filter(value):
            return value.upper()
        assert my_filter.__name__ == "my_filter"

    def test_rejects_non_string_with_filter_error(self, helpers):
        AnsibleFilterError = sys.modules["ansible.errors"].AnsibleFilterError

        @helpers.akeyless_filter
        def my_filter(value):
            return value.upper()

        with pytest.raises(AnsibleFilterError, match=r"my_filter expects.*got int"):
            my_filter(123)

    def test_passes_string_through(self, helpers):
        @helpers.akeyless_filter
        def my_filter(value):
            return value.upper()
        assert my_filter("hello") == "HELLO"

    def test_expects_can_be_overridden(self, helpers):
        AnsibleFilterError = sys.modules["ansible.errors"].AnsibleFilterError

        @helpers.akeyless_filter(expects=dict)
        def my_filter(value):
            return list(value)

        assert my_filter({"a": 1}) == ["a"]
        with pytest.raises(AnsibleFilterError, match=r"expects a dict"):
            my_filter("not-a-dict")

    def test_exception_translated_to_filter_error_with_chain(self, helpers):
        AnsibleFilterError = sys.modules["ansible.errors"].AnsibleFilterError

        @helpers.akeyless_filter
        def my_filter(value):
            raise ValueError("internal failure")

        with pytest.raises(AnsibleFilterError, match=r"my_filter failed: internal") as excinfo:
            my_filter("anything")
        # Exception chain preserved
        assert isinstance(excinfo.value.__cause__, ValueError)

    def test_filter_error_passes_through_unmodified(self, helpers):
        """A filter that raises AnsibleFilterError already produces the
        right error -- don't re-wrap it (avoids 'my_filter failed:
        my_filter expects...' nested messages)."""
        AnsibleFilterError = sys.modules["ansible.errors"].AnsibleFilterError

        @helpers.akeyless_filter
        def my_filter(value):
            raise AnsibleFilterError("explicit user message")

        with pytest.raises(AnsibleFilterError) as excinfo:
            my_filter("anything")
        assert str(excinfo.value) == "explicit user message"

    def test_label_overrides_function_name_in_message(self, helpers):
        AnsibleFilterError = sys.modules["ansible.errors"].AnsibleFilterError

        @helpers.akeyless_filter(label="custom_name")
        def my_filter(value):
            return value

        with pytest.raises(AnsibleFilterError, match=r"custom_name expects"):
            my_filter(None)

    def test_extra_args_kwargs_forwarded(self, helpers):
        @helpers.akeyless_filter
        def my_filter(value, *, prefix=""):
            return f"{prefix}{value}"
        assert my_filter("x", prefix="P_") == "P_x"

    def test_bare_decorator_form(self, helpers):
        """@akeyless_filter (no parens) and @akeyless_filter() must both work."""
        @helpers.akeyless_filter
        def a(v): return v
        @helpers.akeyless_filter()
        def b(v): return v
        assert a("x") == "x"
        assert b("x") == "x"


# ---------------------------------------------------------------------------
# @akeyless_test function decorator
# ---------------------------------------------------------------------------


class TestAkeylessTestDecorator:

    def test_returns_predicate_result_for_string(self, helpers):
        @helpers.akeyless_test
        def is_short(value):
            return len(value) < 5
        assert is_short("hi") is True
        assert is_short("longer") is False

    def test_returns_false_for_non_string_when_requires_string_true(self, helpers):
        @helpers.akeyless_test
        def predicate(value):
            return True  # always true; non-string should still return False
        assert predicate(None) is False
        assert predicate(123) is False
        assert predicate(["list"]) is False

    def test_returns_predicate_result_when_requires_string_false(self, helpers):
        @helpers.akeyless_test(requires_string=False)
        def is_truthy(value):
            return bool(value)
        assert is_truthy(0) is False
        assert is_truthy([]) is False
        assert is_truthy({"x": 1}) is True

    def test_exception_in_predicate_returns_false_never_raises(self, helpers):
        """Tests are predicates; an unexpected exception means the
        value doesn't satisfy the predicate."""
        @helpers.akeyless_test
        def broken_predicate(value):
            raise ValueError("regex compile failed")
        assert broken_predicate("anything") is False

    def test_coerces_truthy_return_to_bool(self, helpers):
        @helpers.akeyless_test
        def fn(value):
            return "truthy-string-not-bool"  # not literally True
        assert fn("input") is True  # coerced via bool()

    def test_bare_decorator_form(self, helpers):
        @helpers.akeyless_test
        def a(v): return True
        @helpers.akeyless_test()
        def b(v): return True
        assert a("x") is True
        assert b("x") is True

    def test_preserves_function_name(self, helpers):
        @helpers.akeyless_test
        def my_predicate(value):
            return True
        assert my_predicate.__name__ == "my_predicate"


# ---------------------------------------------------------------------------
# Module surface
# ---------------------------------------------------------------------------


class TestModuleSurface:

    def test_all_exports_match(self, helpers):
        """Pin __all__ so accidental removal of an exported symbol is
        caught at import time."""
        expected = {
            "akeyless_lookup",
            "AUTH_OPT_KEYS",
            "akeyless_filter",
            "akeyless_test",
            "normalize_sdk_result",
            "compact_kwargs",
        }
        assert set(helpers.__all__) == expected

    def test_auth_opt_keys_contents(self, helpers):
        assert set(helpers.AUTH_OPT_KEYS) == {
            "gateway_url", "access_id", "access_key", "access_type", "token",
        }

    def test_every_exported_symbol_resolves(self, helpers):
        for name in helpers.__all__:
            assert hasattr(helpers, name), f"{name} in __all__ but missing"
