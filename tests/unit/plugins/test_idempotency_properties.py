# Copyright: (c) 2026, pleme-io
# MIT License
#
# Hypothesis property-based tests for the load-bearing idempotency
# helpers (compute_diff / drift_to_diff). The hand-written suite in
# test_idempotency.py covers known-good shapes; this file generates
# adversarial inputs (random nesting, type mixes, None scatters,
# Unicode keys, etc.) to catch the edge cases hand-written tests
# almost always miss in a function that gets called from 155 module
# code paths.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import importlib.util
import sys
import types
from pathlib import Path

import pytest
from hypothesis import given, settings, strategies as st


REPO_ROOT = Path(__file__).resolve().parents[3]
HELPER_PATH = REPO_ROOT / "plugins" / "module_utils" / "akeyless_client.py"


@pytest.fixture(scope="module")
def helper():
    """Load akeyless_client.py with a stub akeyless SDK so the helper
    imports cleanly without the real (heavy) SDK."""
    if "akeyless" not in sys.modules:
        akeyless_mod = types.ModuleType("akeyless")
        akeyless_exc = types.ModuleType("akeyless.exceptions")
        akeyless_exc.ApiException = type("ApiException", (Exception,), {})
        akeyless_mod.exceptions = akeyless_exc
        sys.modules["akeyless"] = akeyless_mod
        sys.modules["akeyless.exceptions"] = akeyless_exc

    spec = importlib.util.spec_from_file_location(
        "akeyless_client_under_test_props", HELPER_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------- strategies
#
# Reusable strategies. We deliberately keep keys ASCII + reasonably short
# so failing cases are readable in test output, but VALUES range widely
# (ints / strings / bools / lists / nested dicts / None) so we surface
# type-mismatch bugs.

# Field names: snake_case ASCII identifiers, the shape every argspec uses.
field_name = st.from_regex(r"^[a-z][a-z0-9_]{0,15}$", fullmatch=True)

# Scalar values that might land in an argspec param or an SDK response.
scalar_value = st.one_of(
    st.none(),
    st.booleans(),
    st.integers(min_value=-1_000_000, max_value=1_000_000),
    st.text(min_size=0, max_size=40),
)

# Lists / dicts shallow enough to be realistic but deep enough to hit
# the nested-lookup paths inside compute_diff.
list_value = st.lists(scalar_value, max_size=5)
dict_value = st.dictionaries(field_name, scalar_value, max_size=5)
any_value = st.one_of(scalar_value, list_value, dict_value)


# ---------------------------------------------------------------------- properties


class TestComputeDiffProperties:
    """Invariants compute_diff must hold across any input shape."""

    @given(
        current=st.dictionaries(field_name, any_value, max_size=10),
        params=st.dictionaries(field_name, any_value, max_size=10),
    )
    @settings(max_examples=200, deadline=None)
    def test_returns_list_of_3tuples(self, helper, current, params):
        """compute_diff is contracted to return [(key, before, after), ...].
        No matter the input, the shape must hold so callers can
        unpack reliably."""
        drift = helper.compute_diff(current, params)
        assert isinstance(drift, list)
        for entry in drift:
            assert isinstance(entry, tuple)
            assert len(entry) == 3
            key, before, after = entry
            assert isinstance(key, str)
            # before may be anything (incl. None when a nested-key
            # lookup happens to find None — though we explicitly skip
            # that case in the helper, but the invariant on the tuple
            # shape still holds)
            # after must NOT be None (we never report a drift for a
            # None desired value -- if `after` is None it'd mean the
            # user wants to clear a field, which we don't currently
            # support and the helper skips)
            assert after is not None, (
                f"compute_diff returned a drift entry with after=None; "
                f"violates the 'skip None desireds' contract: {entry}")

    @given(
        params=st.dictionaries(field_name, any_value, max_size=10),
    )
    @settings(max_examples=100, deadline=None)
    def test_empty_current_means_no_drift(self, helper, params):
        """If we can't read current state at all, we have nothing to
        diff against -- no drift, no false-positive update calls."""
        assert helper.compute_diff(None, params) == []
        assert helper.compute_diff({}, params) == []
        assert helper.compute_diff([], params) == []
        assert helper.compute_diff("not a dict", params) == []

    @given(
        current=st.dictionaries(field_name, any_value, max_size=10),
    )
    @settings(max_examples=100, deadline=None)
    def test_empty_params_means_no_drift(self, helper, current):
        """Nothing requested → nothing to converge."""
        assert helper.compute_diff(current, {}) == []
        assert helper.compute_diff(current, None) == []

    @given(
        current=st.dictionaries(field_name, any_value, max_size=10),
        params=st.dictionaries(field_name, scalar_value, max_size=10),
    )
    @settings(max_examples=200, deadline=None)
    def test_ignore_keys_never_appear_in_drift(self, helper, current, params):
        """IDEMPOTENCY_IGNORE_KEYS values are auth/transport noise --
        they must never cause an unnecessary update call regardless of
        what current/params say about them."""
        # Force ignored keys to appear with values in both sides
        for key in helper.IDEMPOTENCY_IGNORE_KEYS:
            current[key] = "current-value-for-ignored"
            params[key] = "different-value-for-ignored"
        drift = helper.compute_diff(current, params)
        drift_keys = {k for k, _, _ in drift}
        assert helper.IDEMPOTENCY_IGNORE_KEYS.isdisjoint(drift_keys), (
            f"ignored keys leaked into drift: "
            f"{helper.IDEMPOTENCY_IGNORE_KEYS & drift_keys}")

    @given(
        params=st.dictionaries(field_name, scalar_value, max_size=10),
    )
    @settings(max_examples=100, deadline=None)
    def test_no_drift_when_current_matches_params(self, helper, params):
        """The core idempotency property: when current state mirrors the
        desired params exactly (sans None entries), there is no drift,
        no update call, no changed=True surprise."""
        # Build `current` from `params`, skipping None values + the
        # ignore set (which compute_diff would skip anyway).
        current = {
            k: v for k, v in params.items()
            if v is not None and k not in helper.IDEMPOTENCY_IGNORE_KEYS
        }
        assert helper.compute_diff(current, params) == []

    @given(
        params=st.dictionaries(field_name, scalar_value, max_size=8),
    )
    @settings(max_examples=100, deadline=None)
    def test_nested_lookup_finds_target_details(self, helper, params):
        """A common Akeyless response shape nests resource fields under
        target_details / item_details / etc. The lookup must descend
        into these to find matching values."""
        # Skip the ignore set + Nones; we want the helper to match
        # everything in `params` against the nested dict.
        matchable = {
            k: v for k, v in params.items()
            if v is not None and k not in helper.IDEMPOTENCY_IGNORE_KEYS
        }
        current = {"target_details": matchable}
        assert helper.compute_diff(current, params) == []

    @given(
        key=field_name,
        before=scalar_value.filter(lambda v: v is not None),
        after=scalar_value.filter(
            lambda v: v is not None and v != "" and v != 0 and v is not False),
    )
    @settings(max_examples=50, deadline=None)
    def test_single_drift_round_trips_through_helper(
        self, helper, key, before, after):
        """For a single-field diff with distinct before/after values, the
        helper reports exactly that diff (modulo ignore-set keys)."""
        # Skip cases where the random key happens to be ignored, OR
        # where before/after are equal under Python ==.
        if key in helper.IDEMPOTENCY_IGNORE_KEYS:
            return
        if before == after:
            return
        drift = helper.compute_diff({key: before}, {key: after})
        assert drift == [(key, before, after)]


# ---------------------------------------------------------------------- drift_to_diff


class TestDriftToDiffProperties:

    @given(
        # Build drift tuples directly with non-None before/after so we
        # don't hammer hypothesis's filtering health-check.
        drift=st.lists(
            st.tuples(
                field_name,
                st.one_of(
                    st.booleans(),
                    st.integers(min_value=-1000, max_value=1000),
                    st.text(min_size=0, max_size=20)),
                st.one_of(
                    st.booleans(),
                    st.integers(min_value=-1000, max_value=1000),
                    st.text(min_size=0, max_size=20))),
            max_size=10, unique_by=lambda t: t[0]),
    )
    @settings(max_examples=100, deadline=None)
    def test_round_trip_into_before_after_shape(self, helper, drift):
        """drift_to_diff is just a reshape; every (key, before, after)
        tuple must surface in both the before and after dicts at the
        same key."""
        diff = helper.drift_to_diff(drift)
        assert set(diff.keys()) == {"before", "after"}
        assert isinstance(diff["before"], dict)
        assert isinstance(diff["after"], dict)
        for key, before, after in drift:
            assert diff["before"][key] == before
            assert diff["after"][key] == after
        assert len(diff["before"]) == len(drift)
        assert len(diff["after"]) == len(drift)
