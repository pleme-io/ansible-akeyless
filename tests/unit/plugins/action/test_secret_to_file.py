# Copyright: (c) 2026, pleme-io
# MIT License
#
# Unit tests for plugins/action/secret_to_file.py -- the action plugin
# that wraps "fetch secret + write to remote file" into one task.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import importlib.util
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
ACTION_PATH = REPO_ROOT / "plugins" / "action" / "secret_to_file.py"


def _install_ansible_action_stubs():
    """Idempotent + additive: ensures every symbol the action plugin
    + test code expects is present on the shared ansible.errors stub
    even when sibling test files have installed their own."""
    ansible_pkg = sys.modules.setdefault("ansible", types.ModuleType("ansible"))
    errors_mod = sys.modules.get("ansible.errors")
    if errors_mod is None:
        errors_mod = types.ModuleType("ansible.errors")
        sys.modules["ansible.errors"] = errors_mod
        ansible_pkg.errors = errors_mod

    if not hasattr(errors_mod, "AnsibleActionFail"):
        class _StubActionFail(Exception):
            pass
        errors_mod.AnsibleActionFail = _StubActionFail

    if "ansible.plugins.action" in sys.modules:
        return

    plugins_mod = types.ModuleType("ansible.plugins")
    action_mod = types.ModuleType("ansible.plugins.action")
    loader_mod = types.ModuleType("ansible.plugins.loader")

    class _StubActionBase:
        def __init__(self):
            self._task = None
            self._templar = None
            self._loader = None

        def run(self, tmp=None, task_vars=None):
            return {}

        def _execute_module(self, module_name=None, module_args=None, task_vars=None):
            # Pin call args on the instance for test assertions; return
            # a plausible-shape result dict.
            self._last_module_name = module_name
            self._last_module_args = module_args
            return {
                "changed": True,
                "dest": (module_args or {}).get("dest"),
                "invocation": {"module_args": dict(module_args or {})},
            }

    action_mod.ActionBase = _StubActionBase

    # lookup_loader.get stub; tests override per case.
    loader_mod.lookup_loader = MagicMock(name="lookup_loader")

    sys.modules["ansible.plugins"] = plugins_mod
    sys.modules["ansible.plugins.action"] = action_mod
    sys.modules["ansible.plugins.loader"] = loader_mod
    ansible_pkg.plugins = plugins_mod


@pytest.fixture
def action_mod():
    _install_ansible_action_stubs()
    spec = importlib.util.spec_from_file_location(
        "secret_to_file_under_test", ACTION_PATH
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["secret_to_file_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


def _make_action(action_mod, args):
    """Build an ActionModule instance with a task whose args is `args`."""
    am = action_mod.ActionModule()
    am._task = MagicMock()
    am._task.args = args
    am._templar = MagicMock()
    am._templar.template = MagicMock(side_effect=Exception("force fallback"))
    am._loader = MagicMock()
    return am


# ---------------------------------------------------------------------------
# Required-arg validation
# ---------------------------------------------------------------------------


class TestRequiredArgs:

    def test_secret_required(self, action_mod):
        from ansible.errors import AnsibleActionFail
        am = _make_action(action_mod, {"dest": "/tmp/x"})
        with pytest.raises(AnsibleActionFail, match="'secret' is required"):
            am.run(task_vars={})

    def test_dest_required(self, action_mod):
        from ansible.errors import AnsibleActionFail
        am = _make_action(action_mod, {"secret": "/x"})
        with pytest.raises(AnsibleActionFail, match="'dest' is required"):
            am.run(task_vars={})

    def test_rejects_unknown_arg(self, action_mod):
        from ansible.errors import AnsibleActionFail
        am = _make_action(action_mod, {
            "secret": "/x", "dest": "/tmp/x", "totally_made_up": True,
        })
        with pytest.raises(AnsibleActionFail, match="Unknown args"):
            am.run(task_vars={})


# ---------------------------------------------------------------------------
# Successful fetch + copy delegation
# ---------------------------------------------------------------------------


class TestRunSuccess:

    def test_fetches_secret_and_delegates_to_copy(self, action_mod):
        """Happy path: secret is fetched via the lookup, then handed
        to ansible.builtin.copy with content=<secret>."""
        from ansible.plugins.loader import lookup_loader
        fake_lookup = MagicMock()
        fake_lookup.run.return_value = ["the-secret-value"]
        lookup_loader.get.return_value = fake_lookup

        am = _make_action(action_mod, {
            "secret": "/app/key",
            "dest": "/etc/app/key",
            "owner": "app",
            "mode": "0600",
        })
        result = am.run(task_vars={})

        # Lookup was called with our secret path.
        fake_lookup.run.assert_called_once()
        args, kwargs = fake_lookup.run.call_args
        assert args[0] == ["/app/key"]

        # _execute_module was invoked with ansible.builtin.copy + the secret value.
        assert am._last_module_name == "ansible.builtin.copy"
        assert am._last_module_args["content"] == "the-secret-value"
        assert am._last_module_args["dest"] == "/etc/app/key"
        assert am._last_module_args["owner"] == "app"
        assert am._last_module_args["mode"] == "0600"

        # Result inherits copy's shape.
        assert result["changed"] is True
        assert result["dest"] == "/etc/app/key"

    def test_copy_module_args_invocation_is_redacted(self, action_mod):
        """The action sets invocation.module_args.content to the
        redaction sentinel so the value doesn't leak even in
        -vvv stack output."""
        from ansible.plugins.loader import lookup_loader
        fake_lookup = MagicMock()
        fake_lookup.run.return_value = ["sensitive-value"]
        lookup_loader.get.return_value = fake_lookup

        am = _make_action(action_mod, {"secret": "/x", "dest": "/tmp/x"})
        result = am.run(task_vars={})

        redacted = result["invocation"]["module_args"]["content"]
        assert "sensitive-value" not in redacted
        assert "redacted" in redacted.lower()

    def test_none_lookup_result_fails_loud(self, action_mod):
        """If the lookup returns no value, fail rather than write
        an empty file silently."""
        from ansible.errors import AnsibleActionFail
        from ansible.plugins.loader import lookup_loader
        fake_lookup = MagicMock()
        fake_lookup.run.return_value = []
        lookup_loader.get.return_value = fake_lookup

        am = _make_action(action_mod, {"secret": "/missing", "dest": "/tmp/x"})
        with pytest.raises(AnsibleActionFail, match="returned no value"):
            am.run(task_vars={})

    def test_optional_copy_args_pass_through(self, action_mod):
        """owner/group/mode/backup/force all forward verbatim to copy."""
        from ansible.plugins.loader import lookup_loader
        fake_lookup = MagicMock()
        fake_lookup.run.return_value = ["v"]
        lookup_loader.get.return_value = fake_lookup

        am = _make_action(action_mod, {
            "secret": "/x", "dest": "/y",
            "owner": "root", "group": "wheel",
            "mode": "0640", "backup": True, "force": False,
        })
        am.run(task_vars={})
        ma = am._last_module_args
        assert ma["owner"] == "root"
        assert ma["group"] == "wheel"
        assert ma["mode"] == "0640"
        assert ma["backup"] is True
        assert ma["force"] is False


# ---------------------------------------------------------------------------
# Auth option forwarding to the lookup
# ---------------------------------------------------------------------------


class TestAuthForwarding:

    def test_auth_options_pass_to_lookup_run(self, action_mod):
        """Auth args supplied on the action task should reach the
        lookup as kwargs so the user's per-task override wins."""
        from ansible.plugins.loader import lookup_loader
        fake_lookup = MagicMock()
        fake_lookup.run.return_value = ["v"]
        lookup_loader.get.return_value = fake_lookup

        am = _make_action(action_mod, {
            "secret": "/x", "dest": "/y",
            "access_id": "p-xxx",
            "access_key": "secret",
            "gateway_url": "https://custom-gw/",
        })
        am.run(task_vars={})
        _, kwargs = fake_lookup.run.call_args
        assert kwargs["access_id"] == "p-xxx"
        assert kwargs["access_key"] == "secret"
        assert kwargs["gateway_url"] == "https://custom-gw/"
