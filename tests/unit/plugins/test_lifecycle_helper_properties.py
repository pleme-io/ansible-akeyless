# Copyright: (c) 2026, pleme-io
# MIT License
#
# Hypothesis property tests for the three lifecycle helpers:
#   run_standard_crud / run_action_module / run_info_module.
#
# Existing test_lifecycle_helpers.py covers fixed inputs across every
# branch of the state machine; this file generates random argument_spec
# shapes + random sdk_call (tuple OR SdkCall) values and asserts the
# load-bearing invariants hold:
#
#   1. Helpers never return -- they always terminate via SystemExit
#      from exit_json or fail_json.
#   2. SdkCall NamedTuple and plain ("Model", "method") tuples produce
#      byte-equivalent SDK dispatch (NamedTuple IS a tuple).
#   3. run_info_module always reports changed=False regardless of input.
#   4. run_action_module always reports changed=True regardless of input.
#   5. run_standard_crud with state=absent + current=None reports
#      changed=False with "already absent".

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

# Helper-state setup runs once per fixture activation; each @given case
# reuses the same helper module + AnsibleModule stub but re-stubs the
# primitives (get_client/build_body/call_api) per case via _drive(). The
# helper itself is stateless, so the function-scoped-fixture health
# check is a false positive here. Suppress it once at module scope.
_PROP_SETTINGS = dict(deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])

REPO_ROOT = Path(__file__).resolve().parents[3]
HELPER_PATH = REPO_ROOT / "plugins" / "module_utils" / "akeyless_client.py"


def _load_helper(fake_akeyless):
    spec = importlib.util.spec_from_file_location(
        "akeyless_client_lifecycle_props", HELPER_PATH
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["akeyless_client_lifecycle_props"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def helper(fake_akeyless):
    return _load_helper(fake_akeyless[0])


def _drive(helper, params, *, fake_ansible_module, check_mode=False,
           call_responses=None):
    """Wire AnsibleModule stub + primitive recorders; return the recorder."""
    fake_ansible_module(params=params, check_mode=check_mode)
    invocations = []

    def call_api_recorder(module, client, method, body, swallow_404=False):
        invocations.append((method, body, swallow_404))
        return (call_responses or {}).get(method)

    helper.get_client = MagicMock(return_value=(MagicMock(name="client"), "TOK"))
    helper.build_body = MagicMock(side_effect=lambda model, params: {
        "_model": model, **{k: v for k, v in params.items() if v is not None}
    })
    helper.call_api = call_api_recorder
    return invocations


def _capture(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except SystemExit as e:
        return getattr(e, "code", 0), getattr(e, "kwargs", {})
    pytest.fail(f"{fn.__name__} returned without exit_json/fail_json")


# Strategies. Model class names are PascalCase; methods are snake_case.
pascal_name = st.from_regex(r"^[A-Z][A-Za-z]{1,20}$", fullmatch=True)
snake_name = st.from_regex(r"^[a-z][a-z_]{1,20}$", fullmatch=True)


# ---------------------------------------------------------------------------
# SdkCall <-> plain-tuple equivalence
# ---------------------------------------------------------------------------


class TestSdkCallEquivalence:
    """SdkCall is a NamedTuple subclass of tuple; the helpers iterate-unpack
    sdk_call as `model, method = sdk_call`. Both forms must produce
    identical SDK dispatch."""

    @given(model=pascal_name, method=snake_name)
    @settings(max_examples=50, **_PROP_SETTINGS)
    def test_sdkcall_equals_plain_tuple(self, helper, model, method):
        sdk = helper.SdkCall(model=model, method=method)
        assert sdk == (model, method), (
            "SdkCall must equal the plain tuple form for backward compat")
        # Indexing into SdkCall by position works like a tuple.
        assert sdk[0] == model and sdk[1] == method
        # Iter-unpack works.
        m, n = sdk
        assert m == model and n == method
        # Named attribute access works.
        assert sdk.model == model and sdk.method == method


# ---------------------------------------------------------------------------
# run_info_module: changed=False is an invariant
# ---------------------------------------------------------------------------


class TestRunInfoModuleProperties:

    @given(model=pascal_name, method=snake_name)
    @settings(max_examples=30, **_PROP_SETTINGS)
    def test_always_unchanged(self, helper, fake_ansible_module, model, method):
        """No matter the sdk_call shape, info modules must report
        changed=False. Data sources never mutate."""
        invocations = _drive(
            helper, params={}, fake_ansible_module=fake_ansible_module,
            call_responses={method: {"some": "data"}},
        )
        code, kwargs = _capture(
            helper.run_info_module,
            argument_spec={},
            sdk_call=(model, method),
        )
        assert code == 0  # exit_json
        assert kwargs["changed"] is False
        assert [inv[0] for inv in invocations] == [method]

    @given(model=pascal_name, method=snake_name)
    @settings(max_examples=15, **_PROP_SETTINGS)
    def test_sdkcall_form_works_too(self, helper, fake_ansible_module, model, method):
        """The NamedTuple form must work everywhere the tuple form does."""
        _drive(
            helper, params={}, fake_ansible_module=fake_ansible_module,
            call_responses={method: {"x": 1}},
        )
        code, kwargs = _capture(
            helper.run_info_module,
            argument_spec={},
            sdk_call=helper.SdkCall(model=model, method=method),
        )
        assert code == 0
        assert kwargs["changed"] is False


# ---------------------------------------------------------------------------
# run_action_module: changed=True is an invariant
# ---------------------------------------------------------------------------


class TestRunActionModuleProperties:

    @given(model=pascal_name, method=snake_name)
    @settings(max_examples=30, **_PROP_SETTINGS)
    def test_always_changed(self, helper, fake_ansible_module, model, method):
        """One-shot actions always report changed=True. The helper
        hard-codes this rather than per-action wiring."""
        invocations = _drive(
            helper, params={}, fake_ansible_module=fake_ansible_module,
            call_responses={method: {"result": "done"}},
        )
        code, kwargs = _capture(
            helper.run_action_module,
            argument_spec={},
            sdk_call=(model, method),
        )
        assert code == 0
        assert kwargs["changed"] is True
        assert [inv[0] for inv in invocations] == [method]


# ---------------------------------------------------------------------------
# run_standard_crud: state=absent + missing => no-op
# ---------------------------------------------------------------------------


class TestRunStandardCrudProperties:

    @given(
        create_model=pascal_name, create_method=snake_name,
        delete_model=pascal_name, delete_method=snake_name,
        read_model=pascal_name, read_method=snake_name,
        label=snake_name,
    )
    @settings(max_examples=30, **_PROP_SETTINGS)
    def test_absent_when_missing_is_noop(
        self, helper, fake_ansible_module,
        create_model, create_method, delete_model, delete_method,
        read_model, read_method, label,
    ):
        """If we wanted absent and the read returns None, no write
        SDK call ever fires. Property holds for any (random) model/
        method names."""
        invocations = _drive(
            helper,
            params={"state": "absent", "name": "anything"},
            fake_ansible_module=fake_ansible_module,
            call_responses={read_method: None},
        )
        code, kwargs = _capture(
            helper.run_standard_crud,
            argument_spec={
                "state": {"type": "str", "choices": ["present", "absent"],
                          "default": "present"},
                "name": {"type": "str"},
            },
            resource_label=label,
            sdk_create=(create_model, create_method),
            sdk_update=None, immutable=True,
            sdk_delete=(delete_model, delete_method),
            sdk_read=(read_model, read_method),
        )
        assert code == 0
        assert kwargs["changed"] is False
        # The only SDK invocation should be the read; specifically, neither
        # the create nor the delete endpoint may fire. (We can't simply
        # check "no write" -- when the random strategies happen to pick
        # the same method name for read+delete, the no-write invariant
        # collides with the read. So check the exact methods that were
        # called and assert delete_method is absent regardless of name
        # overlap by checking against the invocation count for the read.)
        invoked = [inv[0] for inv in invocations]
        # Read must have been called exactly once.
        assert invoked.count(read_method) == 1, (
            f"expected exactly 1 read call to {read_method!r}, got {invoked}")
        # If delete_method != read_method, delete must not appear at all.
        if delete_method != read_method:
            assert delete_method not in invoked, (
                f"absent-of-absent must not call delete; invocations: {invoked}")
        # Create never fires on an absent-of-absent path regardless of overlap.
        if create_method not in {read_method, delete_method}:
            assert create_method not in invoked
        assert "already absent" in (kwargs.get("msg") or "")

    @given(
        create_model=pascal_name, create_method=snake_name,
        delete_model=pascal_name, delete_method=snake_name,
        read_model=pascal_name, read_method=snake_name,
        label=snake_name,
    )
    @settings(max_examples=30, **_PROP_SETTINGS)
    def test_check_mode_never_calls_write_endpoints(
        self, helper, fake_ansible_module,
        create_model, create_method, delete_model, delete_method,
        read_model, read_method, label,
    ):
        """In check_mode, no write endpoint may ever be invoked
        regardless of input shape -- this is the user-facing safety
        guarantee that --check is non-destructive."""
        invocations = _drive(
            helper,
            params={"state": "present", "name": "x"},
            fake_ansible_module=fake_ansible_module,
            check_mode=True,
            call_responses={read_method: None},  # would normally trigger create
        )
        code, kwargs = _capture(
            helper.run_standard_crud,
            argument_spec={
                "state": {"type": "str", "choices": ["present", "absent"],
                          "default": "present"},
                "name": {"type": "str"},
            },
            resource_label=label,
            sdk_create=(create_model, create_method),
            sdk_update=None, immutable=True,
            sdk_delete=(delete_model, delete_method),
            sdk_read=(read_model, read_method),
        )
        assert code == 0
        # Same naming-overlap caveat as test_absent_when_missing_is_noop:
        # we can't blindly say "no write method called" because the random
        # strategies may collide names with the read. Only assert against
        # names distinct from the read.
        invoked = [inv[0] for inv in invocations]
        if create_method != read_method:
            assert create_method not in invoked, (
                f"check_mode invariant violated; create_method {create_method!r} "
                f"called: {invoked}")
        if delete_method != read_method:
            assert delete_method not in invoked, (
                f"check_mode invariant violated; delete_method {delete_method!r} "
                f"called: {invoked}")
