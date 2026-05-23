# Copyright: (c) 2026, pleme-io
# MIT License
#
# Unit tests for plugins/callback/akeyless_redactor.py -- defensive
# secondary-pass secret redaction. no_log=true on the producing
# task is the primary defense; this callback is defense in depth.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import importlib.util
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
CALLBACK_PATH = REPO_ROOT / "plugins" / "callback" / "akeyless_redactor.py"


def _install_ansible_callback_stubs():
    """Stub ansible.plugins.callback.CallbackBase + .default so the
    callback imports without a real Ansible install. We replace
    CallbackBase with a minimal class that supports
    set_options/get_option."""
    if "ansible.plugins.callback" in sys.modules:
        return

    ansible_pkg = sys.modules.setdefault("ansible", types.ModuleType("ansible"))
    plugins_mod = types.ModuleType("ansible.plugins")
    cb_mod = types.ModuleType("ansible.plugins.callback")
    cb_default_mod = types.ModuleType("ansible.plugins.callback.default")

    class _StubCallbackBase:
        def __init__(self):
            self._opts: dict = {}

        def set_options(self, task_keys=None, var_options=None, direct=None):
            self._opts.update(direct or {})

        def get_option(self, name):
            return self._opts.get(name)

        # The default callback's hook methods -- our subclass calls
        # super() on these. Return None like the real ones.
        def v2_runner_on_ok(self, result):
            return None

        def v2_runner_on_failed(self, result, ignore_errors=False):
            return None

        def v2_runner_on_unreachable(self, result):
            return None

    cb_mod.CallbackBase = _StubCallbackBase
    cb_default_mod.CallbackModule = _StubCallbackBase
    sys.modules["ansible.plugins"] = plugins_mod
    sys.modules["ansible.plugins.callback"] = cb_mod
    sys.modules["ansible.plugins.callback.default"] = cb_default_mod
    ansible_pkg.plugins = plugins_mod


@pytest.fixture(scope="module")
def callback_mod():
    _install_ansible_callback_stubs()
    spec = importlib.util.spec_from_file_location(
        "akeyless_redactor_under_test", CALLBACK_PATH
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["akeyless_redactor_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# _is_suspicious -- the heuristic gate
# ---------------------------------------------------------------------------


class TestIsSuspicious:

    def test_pem_block_is_suspicious(self, callback_mod):
        pem = (
            "-----BEGIN CERTIFICATE-----\nAAAAAAAA\n-----END CERTIFICATE-----"
        )
        assert callback_mod._is_suspicious(pem, min_length=32)

    def test_access_id_is_suspicious(self, callback_mod):
        text = "access_id is p-abcdef0123456789 supplied via env"
        # The whole string is 50+ chars, contains the access-id pattern.
        assert callback_mod._is_suspicious(text, min_length=32)

    def test_long_base64_is_suspicious(self, callback_mod):
        # 64-char base64 = a likely secret blob
        b64 = "QUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUE="
        assert callback_mod._is_suspicious(b64, min_length=32)

    def test_short_value_not_suspicious(self, callback_mod):
        """Trivial short strings (passwords-shaped) pass through to
        keep playbook output usable; the producing task should use
        no_log=true for those."""
        assert not callback_mod._is_suspicious("abc", min_length=32)
        assert not callback_mod._is_suspicious("p-abcdef0123456789", min_length=200)

    def test_url_not_suspicious(self, callback_mod):
        """URLs / file paths are common in task output and shouldn't
        be redacted as secrets. They lack PEM markers, lack access-ID
        format, and contain non-base64 characters (/, :)."""
        url = "https://api.akeyless.io/get-secret-value/foo/bar?x=1"
        assert not callback_mod._is_suspicious(url, min_length=32)


# ---------------------------------------------------------------------------
# _looks_like_base64
# ---------------------------------------------------------------------------


class TestLooksLikeBase64:

    def test_valid_base64_returns_true(self, callback_mod):
        assert callback_mod._looks_like_base64("aGVsbG8gd29ybGQ=")

    def test_empty_returns_false(self, callback_mod):
        assert not callback_mod._looks_like_base64("")

    def test_wrong_padding_returns_false(self, callback_mod):
        assert not callback_mod._looks_like_base64("aGVsbG8")  # 7 chars

    def test_invalid_chars_returns_false(self, callback_mod):
        assert not callback_mod._looks_like_base64("@@@@@@@@")


# ---------------------------------------------------------------------------
# _redact_in_place -- tree-walking redaction
# ---------------------------------------------------------------------------


class TestRedactInPlace:

    def test_redacts_top_level_suspicious_string_in_dict(self, callback_mod):
        d = {
            "cert": "-----BEGIN CERTIFICATE-----\nAAAAAAAA\n-----END CERTIFICATE-----",
            "msg": "ok",
        }
        callback_mod._redact_in_place(d, "REDACTED", min_length=32, seen=set())
        assert d["cert"] == "REDACTED"
        assert d["msg"] == "ok"  # short, not suspicious

    def test_redacts_nested_dict(self, callback_mod):
        d = {
            "result": {
                "value": "-----BEGIN RSA PRIVATE KEY-----\nKKKK\n-----END RSA PRIVATE KEY-----",
                "name": "myrole",
            },
        }
        callback_mod._redact_in_place(d, "REDACTED", min_length=32, seen=set())
        assert d["result"]["value"] == "REDACTED"
        assert d["result"]["name"] == "myrole"

    def test_redacts_in_list_items(self, callback_mod):
        d = {
            "results": [
                {"value": "QUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUE="},
                {"value": "short"},
            ],
        }
        callback_mod._redact_in_place(d, "REDACTED", min_length=32, seen=set())
        assert d["results"][0]["value"] == "REDACTED"
        assert d["results"][1]["value"] == "short"

    def test_handles_cyclic_references(self, callback_mod):
        """Defensive: a result dict containing a cycle shouldn't
        infinite-loop the redactor. The `seen` set tracks visited
        container ids."""
        d: dict = {"x": "ok"}
        d["self"] = d  # cycle
        # Should not stack-overflow.
        callback_mod._redact_in_place(d, "REDACTED", min_length=32, seen=set())
        assert d["x"] == "ok"

    def test_passes_through_non_string_non_container_scalars(self, callback_mod):
        d = {"int": 42, "bool": True, "none": None, "float": 3.14}
        callback_mod._redact_in_place(d, "REDACTED", min_length=32, seen=set())
        assert d == {"int": 42, "bool": True, "none": None, "float": 3.14}


# ---------------------------------------------------------------------------
# CallbackModule integration
# ---------------------------------------------------------------------------


class TestCallbackModule:

    def test_init_carries_defaults(self, callback_mod):
        cb = callback_mod.CallbackModule()
        assert cb._redaction_token == "*** redacted by akeyless_redactor ***"
        assert cb._min_secret_length == 32

    def test_set_options_reads_redaction_token(self, callback_mod):
        cb = callback_mod.CallbackModule()
        cb.set_options(direct={
            "redaction_token": "<<REDACTED>>",
            "min_secret_length": 16,
        })
        assert cb._redaction_token == "<<REDACTED>>"
        assert cb._min_secret_length == 16

    def test_v2_runner_on_ok_redacts_result(self, callback_mod):
        cb = callback_mod.CallbackModule()
        result = MagicMock()
        result._result = {
            "value": "-----BEGIN CERTIFICATE-----\nAAAAAAAA\n-----END CERTIFICATE-----",
            "ok_msg": "deployed",
        }
        cb.v2_runner_on_ok(result)
        assert result._result["value"] == "*** redacted by akeyless_redactor ***"
        assert result._result["ok_msg"] == "deployed"

    def test_v2_runner_on_failed_redacts_result(self, callback_mod):
        cb = callback_mod.CallbackModule()
        result = MagicMock()
        result._result = {
            "value": "p-abcdef0123456789 leaked here in a long-enough message"
                     " to clear the suspicion length threshold",
        }
        cb.v2_runner_on_failed(result, ignore_errors=False)
        assert "p-abcdef0123456789" not in result._result["value"]

    def test_callback_name_and_type(self, callback_mod):
        """Ansible discovers callbacks by CALLBACK_NAME and dispatches
        by CALLBACK_TYPE. Pin both."""
        assert callback_mod.CallbackModule.CALLBACK_NAME == "drzln0.akeyless.akeyless_redactor"
        assert callback_mod.CallbackModule.CALLBACK_TYPE == "stdout"
