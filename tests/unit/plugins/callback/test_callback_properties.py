# Copyright: (c) 2026, pleme-io
# MIT License
#
# Hypothesis property tests for plugins/callback/akeyless_redactor.py.
# Complements test_akeyless_redactor.py (fixed cases) with random
# task-result shapes. The redactor is defensive code -- "secrets must
# never reach stdout" is the invariant -- so property-based fuzzing
# is more important here than for most plugins.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import importlib.util
import sys
import types
from pathlib import Path

import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

REPO_ROOT = Path(__file__).resolve().parents[4]
CALLBACK_PATH = REPO_ROOT / "plugins" / "callback" / "akeyless_redactor.py"


def _install_ansible_callback_stubs():
    """Stub ansible.plugins.callback.* so the callback module imports
    without an ansible-core install."""
    ansible_pkg = sys.modules.setdefault("ansible", types.ModuleType("ansible"))
    plugins_pkg = sys.modules.setdefault(
        "ansible.plugins", types.ModuleType("ansible.plugins")
    )
    ansible_pkg.plugins = plugins_pkg
    callback_mod = sys.modules.get("ansible.plugins.callback")
    if callback_mod is None:
        callback_mod = types.ModuleType("ansible.plugins.callback")
        sys.modules["ansible.plugins.callback"] = callback_mod
        plugins_pkg.callback = callback_mod
    if not hasattr(callback_mod, "CallbackBase"):
        class _CallbackBase:
            def set_options(self, *_, **__): pass
            def get_option(self, _name): return None
        callback_mod.CallbackBase = _CallbackBase

    # default callback plugin (the redactor inherits from it)
    default_mod = sys.modules.get(
        "ansible_collections.ansible.builtin.plugins.callback.default"
    )
    if default_mod is None:
        default_mod = types.ModuleType(
            "ansible_collections.ansible.builtin.plugins.callback.default"
        )
        sys.modules[
            "ansible_collections.ansible.builtin.plugins.callback.default"
        ] = default_mod
    if not hasattr(default_mod, "CallbackModule"):
        class _DefaultCB:
            def __init__(self): pass
            def set_options(self, *_, **__): pass
            def get_option(self, _name): return None
            def v2_runner_on_ok(self, _r): pass
            def v2_runner_on_failed(self, _r, ignore_errors=False): pass
            def v2_runner_on_unreachable(self, _r): pass
        default_mod.CallbackModule = _DefaultCB


@pytest.fixture(scope="module")
def callback():
    _install_ansible_callback_stubs()
    spec = importlib.util.spec_from_file_location(
        "akeyless_redactor_under_test_props", CALLBACK_PATH
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


_PROP_SETTINGS = dict(
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)

# Strategies for building arbitrary task-result-like containers.
_scalar = st.one_of(
    st.none(),
    st.booleans(),
    st.integers(),
    st.floats(allow_nan=False, allow_infinity=False),
    st.text(min_size=1, max_size=30),
)

_payload = st.recursive(
    _scalar,
    lambda children: st.one_of(
        st.lists(children, max_size=5),
        st.dictionaries(st.text(min_size=1, max_size=10), children, max_size=5),
    ),
    max_leaves=15,
)


# ---------------------------------------------------------------------------
# _is_suspicious properties
# ---------------------------------------------------------------------------


class TestIsSuspiciousProperties:

    @given(text=st.text(max_size=10))
    @settings(max_examples=100, **_PROP_SETTINGS)
    def test_short_value_never_flagged(self, callback, text):
        """Invariant: a value shorter than min_secret_length is never
        flagged, regardless of content. Short strings show up
        everywhere (status, hostnames) and are not interesting
        secrets."""
        assert callback._is_suspicious(text, min_length=32) is False

    @given(
        text=st.text(min_size=32, max_size=80).filter(
            lambda s: "/" in s or "http" in s or " " in s or "\n" in s
        ),
    )
    @settings(max_examples=50, **_PROP_SETTINGS)
    def test_long_text_with_url_or_path_or_whitespace_not_flagged(
        self, callback, text
    ):
        """URLs, file paths, and whitespace-heavy text are not flagged
        even at length, since they're rarely secrets and breaking them
        in output is annoying."""
        # We're only testing the specific signal categories the
        # redactor handles -- urls/paths/whitespace shouldn't match
        # the access_id regex or pure-base64 heuristic.
        # Exclude pure base64-ish strings to avoid false positives.
        if all(c.isalnum() or c in "+/=\n" for c in text):
            return
        assert callback._is_suspicious(text, min_length=32) is False

    @given(hex_chars=st.from_regex(r"^[a-fA-F0-9]{32,64}$", fullmatch=True))
    @settings(max_examples=50, **_PROP_SETTINGS)
    def test_access_id_shape_always_flagged(self, callback, hex_chars):
        """`p-<32+ hex chars>` is the canonical Akeyless access_id
        shape -- always flag it."""
        assert callback._is_suspicious(f"p-{hex_chars}", min_length=10) is True


# ---------------------------------------------------------------------------
# _redact_in_place properties
# ---------------------------------------------------------------------------


class TestRedactInPlaceProperties:

    @given(payload=_payload)
    @settings(max_examples=200, **_PROP_SETTINGS)
    def test_does_not_raise_on_any_shape(self, callback, payload):
        """For any arbitrary nested dict/list/scalar shape, the
        redactor must complete without raising. Crashing during
        output rendering would mask the original task error and
        confuse the operator."""
        callback._redact_in_place(payload, token="<R>", min_length=32, seen=set())

    @given(payload=_payload)
    @settings(max_examples=100, **_PROP_SETTINGS)
    def test_redaction_is_idempotent(self, callback, payload):
        """Apply the redactor twice -- the second pass must produce
        the same shape as the first. Idempotence matters because
        in real pipelines multiple callbacks may wrap result objects."""
        import copy
        a = copy.deepcopy(payload)
        b = copy.deepcopy(payload)
        callback._redact_in_place(a, token="<R>", min_length=32, seen=set())
        callback._redact_in_place(b, token="<R>", min_length=32, seen=set())
        callback._redact_in_place(b, token="<R>", min_length=32, seen=set())
        assert a == b

    @given(payload=_payload)
    @settings(max_examples=100, **_PROP_SETTINGS)
    def test_non_strings_pass_through(self, callback, payload):
        """Numbers, booleans, None remain themselves after redaction.
        The redactor must never coerce or mask them."""
        import copy
        original = copy.deepcopy(payload)
        callback._redact_in_place(payload, token="<R>", min_length=32, seen=set())

        def _check_non_string_invariance(orig, after):
            if isinstance(orig, dict):
                for k in orig:
                    if k in after:
                        _check_non_string_invariance(orig[k], after[k])
            elif isinstance(orig, list):
                for o, a in zip(orig, after):
                    _check_non_string_invariance(o, a)
            elif not isinstance(orig, str):
                assert orig == after, (
                    f"non-string {orig!r} was modified to {after!r}"
                )

        _check_non_string_invariance(original, payload)

    def test_handles_arbitrary_nesting_without_recursion_error(self, callback):
        """Build a 100-deep nested dict and confirm the redactor doesn't
        blow the stack. (Python default recursion limit is 1000; we
        stay well under but pin the no-crash invariant.)"""
        node = {"end": "x"}
        for _ in range(80):
            node = {"nested": node}
        callback._redact_in_place(node, token="<R>", min_length=32, seen=set())

    @given(
        suspicious_payload=st.from_regex(r"^p-[a-fA-F0-9]{40}$", fullmatch=True),
    )
    @settings(max_examples=50, **_PROP_SETTINGS)
    def test_top_level_suspicious_string_in_dict_gets_redacted(
        self, callback, suspicious_payload
    ):
        """A dict containing a suspicious value must have that value
        replaced with the redaction token."""
        d = {"token": suspicious_payload}
        callback._redact_in_place(d, token="<REDACTED>", min_length=10, seen=set())
        assert d["token"] == "<REDACTED>"
