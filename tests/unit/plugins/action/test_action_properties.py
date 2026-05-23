# Copyright: (c) 2026, pleme-io
# MIT License
#
# Hypothesis property tests for plugins/action/secret_to_file.py.
# Complements test_secret_to_file.py (fixed cases) with random arg
# shapes. The action plugin is the canonical "fetch + materialise"
# pattern; verifying it rejects unknown args + always passes auth
# opts through reliably is the load-bearing contract.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import importlib.util
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

REPO_ROOT = Path(__file__).resolve().parents[4]
ACTION_PATH = REPO_ROOT / "plugins" / "action" / "secret_to_file.py"


def _install_action_stubs():
    """Stubs for ansible.errors / plugins.action / plugins.loader +
    the plugin_helpers helper. Idempotent."""
    ansible_pkg = sys.modules.setdefault("ansible", types.ModuleType("ansible"))
    errors_mod = sys.modules.get("ansible.errors")
    if errors_mod is None:
        errors_mod = types.ModuleType("ansible.errors")
        sys.modules["ansible.errors"] = errors_mod
        ansible_pkg.errors = errors_mod
    if not hasattr(errors_mod, "AnsibleActionFail"):
        class _StubFail(Exception):
            pass
        errors_mod.AnsibleActionFail = _StubFail

    if "ansible.plugins.action" not in sys.modules:
        plugins_mod = types.ModuleType("ansible.plugins")
        action_mod = types.ModuleType("ansible.plugins.action")
        loader_mod = types.ModuleType("ansible.plugins.loader")

        class _StubActionBase:
            """Same shape as test_secret_to_file.py's stub --
            sibling test files install whichever installer fires
            first, so the contract must match (in particular both
            _last_module_name and _last_module_args attributes).
            Without this match, running the two test files
            sequentially fails on AttributeError."""

            def __init__(self):
                self._task = None
                self._templar = None
                self._loader = None

            def run(self, tmp=None, task_vars=None):
                return {}

            def _execute_module(self, module_name=None, module_args=None, task_vars=None):
                self._last_module_name = module_name
                self._last_module_args = module_args
                return {
                    "changed": True,
                    "dest": (module_args or {}).get("dest"),
                    "invocation": {"module_args": dict(module_args or {})},
                }

        action_mod.ActionBase = _StubActionBase
        loader_mod.lookup_loader = MagicMock(name="lookup_loader")
        sys.modules["ansible.plugins"] = plugins_mod
        sys.modules["ansible.plugins.action"] = action_mod
        sys.modules["ansible.plugins.loader"] = loader_mod
        ansible_pkg.plugins = plugins_mod

    # Register plugin_helpers under its canonical FQ name.
    for name in (
        "ansible_collections",
        "ansible_collections.drzln0",
        "ansible_collections.drzln0.akeyless",
        "ansible_collections.drzln0.akeyless.plugins",
        "ansible_collections.drzln0.akeyless.plugins.module_utils",
    ):
        sys.modules.setdefault(name, types.ModuleType(name))
    full = (
        "ansible_collections.drzln0.akeyless.plugins.module_utils"
        ".akeyless_plugin_helpers"
    )
    sys.modules.pop(full, None)
    helper_path = REPO_ROOT / "plugins" / "module_utils" / "akeyless_plugin_helpers.py"
    spec = importlib.util.spec_from_file_location(full, helper_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[full] = mod
    spec.loader.exec_module(mod)


@pytest.fixture
def action_mod():
    _install_action_stubs()
    spec = importlib.util.spec_from_file_location(
        "secret_to_file_props_under_test", ACTION_PATH
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _make_action_instance(action_mod, args, templar_value="secret-value"):
    """Build an ActionModule instance with controlled task args + a
    fake templar that returns the supplied value (skipping the
    lookup_loader fallback in production code)."""
    instance = action_mod.ActionModule()
    instance._task = type("Task", (), {"args": dict(args)})()
    instance._templar = MagicMock()
    instance._templar.template.return_value = templar_value
    instance._loader = MagicMock()
    return instance


_PROP_SETTINGS = dict(
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)

# Strategies
_arg_name = st.text(
    alphabet=st.characters(whitelist_categories=("Ll",)),
    min_size=1, max_size=20,
)
_arg_value = st.one_of(st.text(max_size=30), st.integers(), st.booleans())


# ---------------------------------------------------------------------------
# Argument validation properties
# ---------------------------------------------------------------------------


class TestValidArgsProperties:

    def test_valid_args_contains_required_pair(self, action_mod):
        """`secret` + `dest` are always required, regardless of any
        per-version refactor."""
        valid = action_mod.ActionModule._VALID_ARGS
        assert "secret" in valid
        assert "dest" in valid

    def test_valid_args_contains_all_auth_opt_keys(self, action_mod):
        """Every AUTH_OPT_KEYS field must be passable through to the
        downstream lookup. If the auth-opts list grows, _VALID_ARGS
        must absorb it (we tested this via the AUTH_OPT_KEYS import)."""
        from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_plugin_helpers import (
            AUTH_OPT_KEYS,
        )
        valid = action_mod.ActionModule._VALID_ARGS
        for key in AUTH_OPT_KEYS:
            assert key in valid, f"_VALID_ARGS missing auth key {key!r}"

    def test_valid_args_contains_copy_passthrough_keys(self, action_mod):
        """Standard ansible.builtin.copy options that flow through to
        the target side -- pinned because users rely on them."""
        valid = action_mod.ActionModule._VALID_ARGS
        for key in ("owner", "group", "mode", "backup", "force"):
            assert key in valid, f"_VALID_ARGS missing copy key {key!r}"

    @given(unknown_arg=_arg_name.filter(
        lambda s: s not in {
            "secret", "dest", "owner", "group", "mode", "backup", "force",
            "gateway_url", "access_id", "access_key", "access_type", "token",
        }
    ))
    @settings(max_examples=100, **_PROP_SETTINGS)
    def test_any_unknown_arg_rejected(self, action_mod, unknown_arg):
        """Property: ANY arg name not in _VALID_ARGS must raise
        AnsibleActionFail. Catches typos that would otherwise silently
        do nothing (`owener` instead of `owner`, `accesss_key` etc.)."""
        from ansible.errors import AnsibleActionFail
        args = {
            "secret": "/x", "dest": "/tmp/x",
            unknown_arg: "anything",
        }
        instance = _make_action_instance(action_mod, args)
        with pytest.raises(AnsibleActionFail, match=r"Unknown args"):
            instance.run(task_vars={})


# ---------------------------------------------------------------------------
# Required-args properties
# ---------------------------------------------------------------------------


class TestRequiredArgsProperties:

    @given(args=st.dictionaries(
        st.sampled_from(
            ("owner", "group", "mode", "backup", "force",
             "gateway_url", "access_id", "access_key",
             "access_type", "token"),
        ),
        _arg_value,
        max_size=5,
    ))
    @settings(max_examples=50, **_PROP_SETTINGS)
    def test_missing_secret_always_fails(self, action_mod, args):
        """Property: any combination of optional args, without
        `secret`, must raise."""
        from ansible.errors import AnsibleActionFail
        # Ensure secret isn't accidentally present.
        args.pop("secret", None)
        args["dest"] = "/tmp/x"  # supply dest so the check reaches secret first
        instance = _make_action_instance(action_mod, args)
        with pytest.raises(AnsibleActionFail, match=r"'secret' is required"):
            instance.run(task_vars={})

    @given(args=st.dictionaries(
        st.sampled_from(
            ("owner", "group", "mode", "backup", "force",
             "gateway_url", "access_id", "access_key",
             "access_type", "token"),
        ),
        _arg_value,
        max_size=5,
    ))
    @settings(max_examples=50, **_PROP_SETTINGS)
    def test_missing_dest_always_fails(self, action_mod, args):
        from ansible.errors import AnsibleActionFail
        args.pop("dest", None)
        args["secret"] = "/x"
        instance = _make_action_instance(action_mod, args)
        with pytest.raises(AnsibleActionFail, match=r"'dest' is required"):
            instance.run(task_vars={})


# ---------------------------------------------------------------------------
# Copy-args forwarding properties
# ---------------------------------------------------------------------------


class TestCopyArgsForwardingProperties:

    @given(extra=st.dictionaries(
        st.sampled_from(("owner", "group", "mode", "backup", "force")),
        st.one_of(st.text(max_size=10), st.integers(min_value=0, max_value=0o777),
                   st.booleans()),
        max_size=5,
    ))
    @settings(max_examples=100, **_PROP_SETTINGS)
    def test_copy_passthrough_args_forwarded(self, action_mod, extra):
        """Every owner/group/mode/backup/force that the user provides
        must show up in the args passed to ansible.builtin.copy."""
        args = {"secret": "/x", "dest": "/tmp/x"}
        args.update(extra)
        instance = _make_action_instance(action_mod, args)
        instance.run(task_vars={})

        forwarded = instance._last_module_args
        assert forwarded["dest"] == "/tmp/x"
        for key, value in extra.items():
            assert forwarded[key] == value, (
                f"copy arg {key!r} not forwarded: expected {value!r}, got {forwarded.get(key)!r}"
            )

    def test_content_arg_is_redacted_in_invocation(self, action_mod):
        """The `content` arg holds the secret value; the invocation's
        module_args must never expose it (defensive redaction)."""
        instance = _make_action_instance(action_mod, {
            "secret": "/x", "dest": "/tmp/x",
        }, templar_value="SUPER_SECRET_VALUE")
        result = instance.run(task_vars={})
        ma = result.get("invocation", {}).get("module_args", {})
        if "content" in ma:
            assert "SUPER_SECRET_VALUE" not in ma["content"], (
                "secret value leaked into invocation.module_args.content"
            )
            assert "redacted" in ma["content"], (
                f"expected `redacted` marker; got {ma['content']!r}"
            )
