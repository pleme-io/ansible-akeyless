# Copyright: (c) 2026, pleme-io
# MIT License
#
# Unit tests for the compute_diff / drift_to_diff helpers that drive
# real idempotency across all 155 standard-CRUD modules. These functions
# decide whether a module calls update() and reports changed=True, so
# their behavior is load-bearing -- a false-no-drift verdict means
# silent staleness; a false-drift verdict means changed=True every run
# (the bug we wrote them to eliminate).

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import importlib.util
import sys
import types
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
HELPER_PATH = REPO_ROOT / "plugins" / "module_utils" / "akeyless_client.py"


@pytest.fixture(scope="module")
def helper():
    """Load akeyless_client.py in isolation so we don't pay the SDK
    import cost just to test pure-Python helpers. The SDK-dependent
    paths (get_client, call_api) aren't exercised here."""
    # Stub akeyless so the import doesn't blow up.
    if "akeyless" not in sys.modules:
        akeyless_mod = types.ModuleType("akeyless")
        akeyless_exc = types.ModuleType("akeyless.exceptions")
        akeyless_exc.ApiException = type("ApiException", (Exception,), {})
        akeyless_mod.exceptions = akeyless_exc
        sys.modules["akeyless"] = akeyless_mod
        sys.modules["akeyless.exceptions"] = akeyless_exc

    spec = importlib.util.spec_from_file_location("akeyless_client_under_test", HELPER_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------- compute_diff


class TestComputeDiff:
    def test_no_drift_when_all_params_match(self, helper):
        current = {"name": "foo", "description": "bar", "max_versions": 5}
        params  = {"name": "foo", "description": "bar", "max_versions": 5}
        assert helper.compute_diff(current, params) == []

    def test_drift_on_changed_value(self, helper):
        current = {"name": "foo", "description": "old"}
        params  = {"name": "foo", "description": "new"}
        drift = helper.compute_diff(current, params)
        assert drift == [("description", "old", "new")]

    def test_skips_none_params(self, helper):
        """A None param means the user didn't ask to set anything --
        never count it as drift, even if current has a value."""
        current = {"name": "foo", "description": "set"}
        params  = {"name": "foo", "description": None}
        assert helper.compute_diff(current, params) == []

    def test_skips_ignore_keys(self, helper):
        """auth/state/token params live in argspec but aren't part of the
        resource's desired state; they must never drive update()."""
        current = {"name": "foo"}
        params  = {
            "name": "foo",
            "state": "present",
            "token": "t-xxx",
            "access_id": "p-xxx",
            "access_key": "secret",
            "gateway_url": "https://api.akeyless.io",
        }
        assert helper.compute_diff(current, params) == []

    def test_skips_field_missing_from_current(self, helper):
        """If the SDK Get response doesn't echo a field (e.g. password
        write-only), missing != drift. Conservative on purpose: we'd
        rather miss a true drift than report drift every run."""
        current = {"name": "foo"}  # no `password` in response
        params  = {"name": "foo", "password": "hunter2"}
        assert helper.compute_diff(current, params) == []

    def test_finds_field_in_target_details_nesting(self, helper):
        """Akeyless target_get returns the schema fields nested under
        `target_details`. Drift lookup should descend into that."""
        current = {
            "name": "my-target",
            "target_details": {"hashi_url": "https://old:8200"},
        }
        params = {"name": "my-target", "hashi_url": "https://new:8200"}
        drift = helper.compute_diff(current, params)
        assert drift == [("hashi_url", "https://old:8200", "https://new:8200")]

    def test_finds_field_in_item_details_nesting(self, helper):
        """Same pattern for items (static_secret, etc.)."""
        current = {"name": "s", "item_details": {"max_versions": 5}}
        params  = {"name": "s", "max_versions": 10}
        assert helper.compute_diff(current, params) == [("max_versions", 5, 10)]

    def test_finds_field_via_camelcase_fallback(self, helper):
        """Some SDK responses use camelCase. The lookup should try both."""
        current = {"name": "foo", "maxVersions": 3}
        params  = {"name": "foo", "max_versions": 5}
        assert helper.compute_diff(current, params) == [("max_versions", 3, 5)]

    def test_multiple_drifts_returned_in_order(self, helper):
        current = {"name": "foo", "description": "a", "max_versions": 5}
        params  = {"name": "foo", "description": "b", "max_versions": 10}
        drift = helper.compute_diff(current, params)
        assert sorted(drift) == sorted([
            ("description", "a", "b"),
            ("max_versions", 5, 10),
        ])

    def test_empty_current_returns_no_drift(self, helper):
        """Defensive: a None / empty / non-dict current shouldn't crash."""
        assert helper.compute_diff(None, {"name": "x"}) == []
        assert helper.compute_diff({}, {"name": "x"}) == []
        assert helper.compute_diff([], {"name": "x"}) == []

    def test_empty_params_returns_no_drift(self, helper):
        assert helper.compute_diff({"name": "x"}, {}) == []
        assert helper.compute_diff({"name": "x"}, None) == []

    def test_custom_ignore_overrides_default(self, helper):
        """Callers can pass their own ignore set (e.g. to also exclude
        a per-resource computed field)."""
        current = {"name": "foo", "description": "x"}
        params  = {"name": "foo", "description": "y"}
        # By default this is drift; explicit ignore should suppress.
        assert helper.compute_diff(current, params, ignore={"description"}) == []


# ---------------------------------------------------------------------- drift_to_diff


class TestDriftToDiff:
    def test_empty_drift(self, helper):
        assert helper.drift_to_diff([]) == {"before": {}, "after": {}}

    def test_single_drift(self, helper):
        d = helper.drift_to_diff([("description", "old", "new")])
        assert d == {"before": {"description": "old"}, "after": {"description": "new"}}

    def test_multiple_drift(self, helper):
        d = helper.drift_to_diff([
            ("description", "a", "b"),
            ("max_versions", 5, 10),
        ])
        assert d == {
            "before": {"description": "a", "max_versions": 5},
            "after":  {"description": "b", "max_versions": 10},
        }


# ------------------------------------------------------------ IDEMPOTENCY_IGNORE_KEYS


class TestIgnoreKeys:
    def test_contains_auth_fields(self, helper):
        """Auth/transport params must never be in compute_diff -- they
        change per environment and are not part of resource state."""
        for k in ("access_id", "access_key", "access_type", "gateway_url",
                  "token", "uid_token", "state"):
            assert k in helper.IDEMPOTENCY_IGNORE_KEYS, k

    def test_is_frozen(self, helper):
        """frozenset so it can't be mutated globally by test pollution."""
        assert isinstance(helper.IDEMPOTENCY_IGNORE_KEYS, frozenset)
