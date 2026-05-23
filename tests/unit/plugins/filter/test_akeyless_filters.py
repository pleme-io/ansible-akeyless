# Copyright: (c) 2026, pleme-io
# MIT License
#
# Unit tests for plugins/filter/akeyless.py -- pure-Python Jinja2
# filters that transform Akeyless secret payloads. No SDK needed.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import importlib.util
import sys
import types
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
FILTER_PATH = REPO_ROOT / "plugins" / "filter" / "akeyless.py"


def _install_ansible_errors_stub():
    """Ensure ansible.errors carries AnsibleFilterError. Idempotent
    merge with any pre-existing ansible.errors stub installed by
    sibling test files (e.g. action plugin tests bring in
    AnsibleActionFail)."""
    ansible_pkg = sys.modules.setdefault("ansible", types.ModuleType("ansible"))
    errors_mod = sys.modules.get("ansible.errors")
    if errors_mod is None:
        errors_mod = types.ModuleType("ansible.errors")
        sys.modules["ansible.errors"] = errors_mod
        ansible_pkg.errors = errors_mod
    if not hasattr(errors_mod, "AnsibleFilterError"):
        class _StubFilterError(Exception):
            pass
        errors_mod.AnsibleFilterError = _StubFilterError


@pytest.fixture(scope="module")
def filters():
    _install_ansible_errors_stub()
    spec = importlib.util.spec_from_file_location(
        "akeyless_filters_under_test", FILTER_PATH
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["akeyless_filters_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# FilterModule registration
# ---------------------------------------------------------------------------


def test_filter_module_registers_all_filters(filters):
    """The FilterModule class is what Ansible's filter loader probes
    for. It must expose every filter via the filters() method."""
    fm = filters.FilterModule()
    registered = fm.filters()
    expected = {
        "b64decode_secret",
        "parse_dotenv_secret",
        "secret_to_json",
        "split_pem_bundle",
        "secret_keys_to_env",
        "mask_secret",
        "secret_strength",
    }
    assert set(registered) == expected
    # Every registered name must resolve to a callable.
    for name, fn in registered.items():
        assert callable(fn), f"filter {name!r} is not callable: {fn!r}"


# ---------------------------------------------------------------------------
# b64decode_secret
# ---------------------------------------------------------------------------


class TestB64DecodeSecret:

    def test_decodes_valid_base64(self, filters):
        # base64 of "hello world"
        assert filters.b64decode_secret("aGVsbG8gd29ybGQ=") == "hello world"

    def test_rejects_non_string(self, filters):
        from ansible.errors import AnsibleFilterError
        with pytest.raises(AnsibleFilterError, match="expects a string"):
            filters.b64decode_secret(b"raw-bytes")
        with pytest.raises(AnsibleFilterError, match="expects a string"):
            filters.b64decode_secret(None)

    def test_rejects_invalid_base64(self, filters):
        from ansible.errors import AnsibleFilterError
        # "@@@" is not valid base64 (contains invalid chars + bad padding)
        with pytest.raises(AnsibleFilterError, match="b64decode_secret failed"):
            filters.b64decode_secret("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")


# ---------------------------------------------------------------------------
# parse_dotenv_secret
# ---------------------------------------------------------------------------


class TestParseDotenvSecret:

    def test_parses_simple_key_value(self, filters):
        out = filters.parse_dotenv_secret("FOO=bar\nBAZ=qux")
        assert out == {"FOO": "bar", "BAZ": "qux"}

    def test_skips_blank_lines_and_comments(self, filters):
        out = filters.parse_dotenv_secret(
            "# header comment\n"
            "FOO=bar\n"
            "\n"
            "# inline-style comment\n"
            "BAZ=qux\n"
        )
        assert out == {"FOO": "bar", "BAZ": "qux"}

    def test_strips_export_prefix(self, filters):
        out = filters.parse_dotenv_secret("export FOO=bar\nexport BAZ=qux")
        assert out == {"FOO": "bar", "BAZ": "qux"}

    def test_strips_matching_quotes(self, filters):
        out = filters.parse_dotenv_secret(
            'A="double quoted"\n'
            "B='single quoted'\n"
            'C=unquoted\n'
        )
        assert out == {
            "A": "double quoted",
            "B": "single quoted",
            "C": "unquoted",
        }

    def test_preserves_mismatched_quotes_as_value(self, filters):
        """Mismatched quotes are NOT stripped -- value preserved
        verbatim. Catches a foot-gun where one side has a typo."""
        out = filters.parse_dotenv_secret('FOO="left-only')
        assert out == {"FOO": '"left-only'}

    def test_raises_on_line_without_equals(self, filters):
        from ansible.errors import AnsibleFilterError
        with pytest.raises(AnsibleFilterError, match="no '=' separator"):
            filters.parse_dotenv_secret("FOO=bar\nBAZ_WITHOUT_EQUALS\nQUX=hello")

    def test_rejects_non_string(self, filters):
        from ansible.errors import AnsibleFilterError
        with pytest.raises(AnsibleFilterError, match="expects a string"):
            filters.parse_dotenv_secret({"already": "a dict"})


# ---------------------------------------------------------------------------
# secret_to_json
# ---------------------------------------------------------------------------


class TestSecretToJson:

    def test_parses_valid_json(self, filters):
        assert filters.secret_to_json('{"a": 1}') == {"a": 1}
        assert filters.secret_to_json("[1, 2, 3]") == [1, 2, 3]
        assert filters.secret_to_json('"plain-string"') == "plain-string"

    def test_raises_with_preview_on_invalid_json(self, filters):
        from ansible.errors import AnsibleFilterError
        bad = "not-json-at-all-this-is-just-text-with-a-very-long-tail-to-test-preview-truncation"
        with pytest.raises(AnsibleFilterError, match="value starts with"):
            filters.secret_to_json(bad)

    def test_rejects_non_string(self, filters):
        from ansible.errors import AnsibleFilterError
        with pytest.raises(AnsibleFilterError, match="expects a string"):
            filters.secret_to_json({"already": "a dict"})


# ---------------------------------------------------------------------------
# split_pem_bundle
# ---------------------------------------------------------------------------


class TestSplitPemBundle:

    def test_splits_single_cert(self, filters):
        pem = (
            "-----BEGIN CERTIFICATE-----\n"
            "AAAA\n"
            "-----END CERTIFICATE-----\n"
        )
        blocks = filters.split_pem_bundle(pem)
        assert len(blocks) == 1
        assert "-----BEGIN CERTIFICATE-----" in blocks[0]
        assert "-----END CERTIFICATE-----" in blocks[0]

    def test_splits_multi_cert_bundle(self, filters):
        pem = (
            "-----BEGIN CERTIFICATE-----\nAAAA\n-----END CERTIFICATE-----\n"
            "-----BEGIN CERTIFICATE-----\nBBBB\n-----END CERTIFICATE-----\n"
        )
        blocks = filters.split_pem_bundle(pem)
        assert len(blocks) == 2
        assert "AAAA" in blocks[0]
        assert "BBBB" in blocks[1]

    def test_handles_mixed_block_types(self, filters):
        """PEM bundles may contain CERTIFICATE + RSA PRIVATE KEY + etc.
        The split should respect block boundaries regardless of type."""
        pem = (
            "-----BEGIN CERTIFICATE-----\nAAAA\n-----END CERTIFICATE-----\n"
            "-----BEGIN RSA PRIVATE KEY-----\nKKKK\n-----END RSA PRIVATE KEY-----\n"
        )
        blocks = filters.split_pem_bundle(pem)
        assert len(blocks) == 2
        assert "CERTIFICATE" in blocks[0]
        assert "PRIVATE KEY" in blocks[1]

    def test_raises_on_orphan_end_marker(self, filters):
        from ansible.errors import AnsibleFilterError
        with pytest.raises(AnsibleFilterError, match="outside an open block"):
            filters.split_pem_bundle("-----END CERTIFICATE-----")

    def test_raises_on_unterminated_block(self, filters):
        from ansible.errors import AnsibleFilterError
        with pytest.raises(AnsibleFilterError, match="unterminated"):
            filters.split_pem_bundle("-----BEGIN CERTIFICATE-----\nincomplete")


# ---------------------------------------------------------------------------
# secret_keys_to_env
# ---------------------------------------------------------------------------


class TestSecretKeysToEnv:

    def test_uppercases_keys(self, filters):
        out = filters.secret_keys_to_env({"foo": "bar", "Baz": "qux"})
        assert out == {"FOO": "bar", "BAZ": "qux"}

    def test_replaces_dashes_and_dots_with_underscores(self, filters):
        """Env-var convention is UPPER_SNAKE; dashes + dots in source
        keys (common in Akeyless paths) become underscores."""
        out = filters.secret_keys_to_env({
            "api-key": "x",
            "db.host": "y",
            "feature-flag.enabled": "true",
        })
        assert out == {
            "API_KEY": "x",
            "DB_HOST": "y",
            "FEATURE_FLAG_ENABLED": "true",
        }

    def test_applies_prefix(self, filters):
        out = filters.secret_keys_to_env({"key": "v"}, prefix="APP_")
        assert out == {"APP_KEY": "v"}

    def test_coerces_non_string_values_to_str(self, filters):
        """env vars are always strings; ints/bools/floats must be coerced."""
        out = filters.secret_keys_to_env({"port": 8080, "debug": True})
        assert out == {"PORT": "8080", "DEBUG": "True"}

    def test_rejects_non_dict_input(self, filters):
        from ansible.errors import AnsibleFilterError
        with pytest.raises(AnsibleFilterError, match="expects a dict"):
            filters.secret_keys_to_env([("a", 1)])

    def test_rejects_non_string_prefix(self, filters):
        from ansible.errors import AnsibleFilterError
        with pytest.raises(AnsibleFilterError, match="prefix must be a string"):
            filters.secret_keys_to_env({"k": "v"}, prefix=123)
