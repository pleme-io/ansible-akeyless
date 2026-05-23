# Copyright: (c) 2026, pleme-io
# MIT License
#
# Pin the public-API surface of akeyless_client.py so accidental
# removal or renaming of a load-bearing helper / primitive fails CI
# before it ships.

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
        "akeyless_client_public_api", HELPER_PATH
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["akeyless_client_public_api"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def helper(fake_akeyless):
    return _load_helper(fake_akeyless[0])


# Pinned: every name that downstream modules MAY import. Removing or
# renaming any of these is a breaking change for the 208 generated
# modules that depend on them.
EXPECTED_LIFECYCLE_HELPERS = frozenset({
    "run_standard_crud",
    "run_action_module",
    "run_info_module",
})

EXPECTED_PRIMITIVES = frozenset({
    "get_client",
    "call_api",
    "build_body",
})


def test_lifecycle_helpers_registry_matches_pinned_set(helper):
    """The @lifecycle_helper decorator populates LIFECYCLE_HELPERS on
    each function import. Pin the exact set to catch:
      - a helper accidentally losing its @lifecycle_helper decorator
        (would fall out of the set silently)
      - a new helper added without an updated pin (intentional, but
        worth surfacing in code review)
    Adding a new helper here AND in the EXPECTED set is a one-line
    two-place edit that's hard to do by accident.
    """
    assert set(helper.LIFECYCLE_HELPERS) == EXPECTED_LIFECYCLE_HELPERS, (
        f"LIFECYCLE_HELPERS drifted: "
        f"removed={EXPECTED_LIFECYCLE_HELPERS - set(helper.LIFECYCLE_HELPERS)}, "
        f"added={set(helper.LIFECYCLE_HELPERS) - EXPECTED_LIFECYCLE_HELPERS}"
    )


def test_primitives_match_pinned_set(helper):
    """PRIMITIVES is the lower-level helper surface. Same change-
    surface pinning argument as for LIFECYCLE_HELPERS."""
    assert helper.PRIMITIVES == EXPECTED_PRIMITIVES


@pytest.mark.parametrize("name", sorted(EXPECTED_LIFECYCLE_HELPERS | EXPECTED_PRIMITIVES))
def test_pinned_public_symbol_is_importable_and_callable(helper, name):
    """Every name in the pinned sets must resolve to a callable on the
    helper module. Catches the case where a symbol is documented but
    not actually defined (e.g. typo, stale rename)."""
    sym = getattr(helper, name, None)
    assert sym is not None, f"{name!r} pinned in public API but missing from helper module"
    assert callable(sym), f"{name!r} pinned in public API but is not callable: {sym!r}"


def test_sdkcall_namedtuple_is_public(helper):
    """SdkCall is the typed (model, method) pair handed to lifecycle
    helpers. Verify it's accessible AND behaves like both a NamedTuple
    and a plain tuple (backward compat)."""
    SdkCall = getattr(helper, "SdkCall", None)
    assert SdkCall is not None, "SdkCall not exposed at module scope"
    instance = SdkCall(model="X", method="y")
    assert instance == ("X", "y"), "SdkCall must equal the plain tuple form"
    assert instance.model == "X"
    assert instance.method == "y"


def test_default_constants_are_set(helper):
    """The DEFAULT_GATEWAY_URL + DEFAULT_ACCESS_TYPE constants are read
    by get_client; downstream tooling (e.g. tests) may also rely on
    them. Pin the values to catch surprise changes."""
    assert helper.DEFAULT_GATEWAY_URL == "https://api.akeyless.io"
    assert helper.DEFAULT_ACCESS_TYPE == "access_key"


def test_idempotency_ignore_keys_includes_auth_and_state(helper):
    """compute_diff skips IDEMPOTENCY_IGNORE_KEYS so transient auth/
    state metadata never triggers spurious update calls. Pin the
    minimum required set; additions are OK."""
    required = {"gateway_url", "access_id", "access_key", "access_type",
                "token", "state"}
    missing = required - set(helper.IDEMPOTENCY_IGNORE_KEYS)
    assert not missing, (
        f"IDEMPOTENCY_IGNORE_KEYS missing required entries: {missing}"
    )
