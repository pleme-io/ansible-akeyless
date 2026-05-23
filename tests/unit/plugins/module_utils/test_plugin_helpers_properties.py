# Copyright: (c) 2026, pleme-io
# MIT License
#
# Hypothesis property tests for plugins/module_utils/akeyless_plugin_helpers.py.
# Complements test_plugin_helpers.py (which uses fixed cases) with random
# inputs that surface edge cases hand-written tests miss.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import importlib.util
import sys
import types
from pathlib import Path

import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

REPO_ROOT = Path(__file__).resolve().parents[4]
HELPERS_PATH = REPO_ROOT / "plugins" / "module_utils" / "akeyless_plugin_helpers.py"


def _install_ansible_errors():
    ansible_pkg = sys.modules.setdefault("ansible", types.ModuleType("ansible"))
    errors_mod = sys.modules.get("ansible.errors")
    if errors_mod is None:
        errors_mod = types.ModuleType("ansible.errors")
        sys.modules["ansible.errors"] = errors_mod
        ansible_pkg.errors = errors_mod
    for cls_name in ("AnsibleError", "AnsibleLookupError", "AnsibleFilterError"):
        if not hasattr(errors_mod, cls_name):
            setattr(errors_mod, cls_name, type(cls_name, (Exception,), {}))


@pytest.fixture(scope="module")
def helpers():
    _install_ansible_errors()
    spec = importlib.util.spec_from_file_location(
        "akeyless_plugin_helpers_props_under_test", HELPERS_PATH
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


_PROP_SETTINGS = dict(
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)


# ---------------------------------------------------------------------------
# normalize_sdk_result properties
# ---------------------------------------------------------------------------


class TestNormalizeSdkResultProperties:

    @given(value=st.one_of(
        st.none(), st.integers(), st.text(max_size=50),
        st.booleans(), st.floats(allow_nan=False, allow_infinity=False),
    ))
    @settings(max_examples=100, **_PROP_SETTINGS)
    def test_plain_scalars_pass_through_unchanged(self, helpers, value):
        """Property: anything without a .to_dict() method must round-trip."""
        assert helpers.normalize_sdk_result(value) == value

    @given(payload=st.dictionaries(
        st.text(max_size=10),
        st.one_of(st.text(max_size=20), st.integers(), st.none()),
        max_size=10,
    ))
    @settings(max_examples=100, **_PROP_SETTINGS)
    def test_to_dict_models_unwrapped_to_their_dict(self, helpers, payload):
        """Property: .to_dict() result is returned verbatim."""
        class _Model:
            def __init__(self, d): self._d = d
            def to_dict(self): return self._d
        assert helpers.normalize_sdk_result(_Model(payload)) == payload


# ---------------------------------------------------------------------------
# compact_kwargs properties
# ---------------------------------------------------------------------------


class TestCompactKwargsProperties:

    @given(
        opts=st.dictionaries(
            st.text(min_size=1, max_size=10, alphabet="abc"),
            st.one_of(st.text(min_size=1, max_size=20), st.integers(),
                      st.booleans()),
            max_size=20,
        ),
    )
    @settings(max_examples=200, **_PROP_SETTINGS)
    def test_output_keys_subset_of_input_keys(self, helpers, opts):
        """compact_kwargs(opts, keys) must never invent keys not in opts."""
        out = helpers.compact_kwargs(opts, list(opts.keys()))
        assert set(out.keys()).issubset(set(opts.keys()))

    @given(opts=st.dictionaries(
        st.text(min_size=1, max_size=10),
        st.text(min_size=1, max_size=10),
        max_size=10,
    ))
    @settings(max_examples=100, **_PROP_SETTINGS)
    def test_non_empty_strings_preserved(self, helpers, opts):
        """Strings with len >= 1 must survive the filter."""
        out = helpers.compact_kwargs(opts, list(opts.keys()))
        # Every non-empty string in opts must appear in out.
        for k, v in opts.items():
            if v != "":
                assert k in out
                assert out[k] == v

    @given(
        opts=st.dictionaries(
            st.text(min_size=1, max_size=10),
            st.one_of(st.just(None), st.just("")),
            max_size=10,
        ),
    )
    @settings(max_examples=100, **_PROP_SETTINGS)
    def test_only_none_and_empty_string_filtered(self, helpers, opts):
        """If every value is None or "", the result is empty."""
        out = helpers.compact_kwargs(opts, list(opts.keys()))
        assert out == {}

    @given(
        keys=st.lists(st.text(min_size=1, max_size=8), max_size=10, unique=True),
    )
    @settings(max_examples=100, **_PROP_SETTINGS)
    def test_missing_keys_silently_skipped(self, helpers, keys):
        """Asking for a key that isn't in opts must not raise."""
        out = helpers.compact_kwargs({}, keys)
        assert out == {}


# ---------------------------------------------------------------------------
# @akeyless_filter properties
# ---------------------------------------------------------------------------


class TestAkeylessFilterProperties:

    @given(value=st.one_of(
        st.none(), st.integers(), st.binary(max_size=20),
        st.lists(st.text(max_size=5), max_size=3),
        st.dictionaries(st.text(max_size=5), st.text(max_size=5), max_size=3),
    ))
    @settings(max_examples=100, **_PROP_SETTINGS)
    def test_default_expects_str_rejects_any_non_string(self, helpers, value):
        """For any non-string input, the default (expects=str) filter
        raises AnsibleFilterError -- never returns junk, never raises
        the underlying TypeError."""
        from ansible.errors import AnsibleFilterError

        @helpers.akeyless_filter
        def echo(v): return v

        with pytest.raises(AnsibleFilterError):
            echo(value)

    @given(value=st.text(max_size=50))
    @settings(max_examples=100, **_PROP_SETTINGS)
    def test_strings_pass_through_when_inner_returns_value(self, helpers, value):
        """For any string input, the filter must invoke the inner fn
        and return its result."""

        @helpers.akeyless_filter
        def echo(v): return v.upper()

        assert echo(value) == value.upper()

    @given(value=st.text(max_size=50))
    @settings(max_examples=50, **_PROP_SETTINGS)
    def test_inner_exception_is_translated_with_chain(self, helpers, value):
        """Inner exceptions are always re-raised as AnsibleFilterError
        with the original exception preserved via __cause__."""
        from ansible.errors import AnsibleFilterError

        @helpers.akeyless_filter
        def explode(v):
            raise ValueError("inner-explosion")

        with pytest.raises(AnsibleFilterError) as excinfo:
            explode(value)
        assert isinstance(excinfo.value.__cause__, ValueError)


# ---------------------------------------------------------------------------
# @akeyless_test properties
# ---------------------------------------------------------------------------


class TestAkeylessTestProperties:

    @given(value=st.one_of(
        st.none(), st.integers(), st.binary(max_size=20),
        st.lists(st.text(max_size=5), max_size=3),
        st.dictionaries(st.text(max_size=5), st.text(max_size=5), max_size=3),
    ))
    @settings(max_examples=100, **_PROP_SETTINGS)
    def test_non_string_input_always_returns_false(self, helpers, value):
        """The non-string input contract holds for ALL non-string types."""

        @helpers.akeyless_test
        def always_true(v): return True  # the decorator should short-circuit

        assert always_true(value) is False

    @given(value=st.text(max_size=50))
    @settings(max_examples=100, **_PROP_SETTINGS)
    def test_string_input_invokes_predicate(self, helpers, value):
        """Strings reach the wrapped predicate."""
        calls = []

        @helpers.akeyless_test
        def captured(v):
            calls.append(v)
            return True

        captured(value)
        assert calls == [value]

    @given(value=st.text(max_size=50))
    @settings(max_examples=100, **_PROP_SETTINGS)
    def test_predicate_exception_always_returns_false(self, helpers, value):
        """An unexpected exception in the predicate must always coerce
        to False -- a test that raises during render breaks the whole
        template."""

        @helpers.akeyless_test
        def broken(v):
            raise RuntimeError("predicate crashed")

        assert broken(value) is False

    @given(value=st.text(max_size=50))
    @settings(max_examples=50, **_PROP_SETTINGS)
    def test_return_value_is_always_bool(self, helpers, value):
        """Returned value is always bool, never str/int/etc."""

        @helpers.akeyless_test
        def returns_string(v): return "non-empty-string"

        result = returns_string(value)
        assert isinstance(result, bool)
