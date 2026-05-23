# Copyright: (c) 2026, pleme-io
# MIT License
#
# Unit tests for plugins/test/akeyless.py -- the Jinja2 test plugins
# for Akeyless content shapes. Pure functions, no SDK needed.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
TEST_PLUGIN_DIR = REPO_ROOT / "plugins" / "test"

# Per-test files (one TestModule per file -- ansible-doc requires
# this layout for per-test docs to resolve).
TEST_FILES = {
    "is_akeyless_path": TEST_PLUGIN_DIR / "is_akeyless_path.py",
    "is_akeyless_access_id": TEST_PLUGIN_DIR / "is_akeyless_access_id.py",
    "is_pem_block": TEST_PLUGIN_DIR / "is_pem_block.py",
    "is_base64": TEST_PLUGIN_DIR / "is_base64.py",
}


def _install_plugin_helpers_stub():
    """Each per-test file imports @akeyless_test from
    plugins/module_utils/akeyless_plugin_helpers.py at module scope."""
    import types
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


@pytest.fixture(scope="module")
def tests():
    """Merge each per-test file's exports into a single namespace
    that the existing test cases can reach via `tests.<symbol>`."""
    _install_plugin_helpers_stub()
    merged = type("MergedTestPlugins", (), {})()
    for name, path in TEST_FILES.items():
        spec = importlib.util.spec_from_file_location(
            f"akeyless_test_under_test_{name}", path
        )
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        # Expose the test function under its name on the merged namespace.
        setattr(merged, name, getattr(mod, name))
    # Synthesise a TestModule that registers ALL test functions for
    # backward compat with the previous merged file.
    class _MergedTestModule:
        def tests(self_):
            out = {}
            for n, p in TEST_FILES.items():
                spec = importlib.util.spec_from_file_location(
                    f"_merged_tm_{n}", p
                )
                m = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(m)
                out.update(m.TestModule().tests())
            return out
    merged.TestModule = _MergedTestModule
    return merged


# ---------------------------------------------------------------------------
# TestModule registration (across all per-test files)
# ---------------------------------------------------------------------------


def test_test_modules_collectively_register_all_tests(tests):
    """Each per-test file's TestModule registers exactly one test;
    the merged registration must equal the 4-test set."""
    tm = tests.TestModule()
    registered = tm.tests()
    expected = {
        "is_akeyless_path",
        "is_akeyless_access_id",
        "is_pem_block",
        "is_base64",
    }
    assert set(registered) == expected
    for name, fn in registered.items():
        assert callable(fn), f"test {name!r} is not callable"


# ---------------------------------------------------------------------------
# is_akeyless_path
# ---------------------------------------------------------------------------


class TestIsAkeylessPath:

    @pytest.mark.parametrize("path", [
        "/app/db/password",
        "/single",
        "/with-dashes/and_underscores",
        "/numeric/123/path",
        "/dotted/file.ext",
        "/a/b/c/d/e/f/g",
    ])
    def test_valid_paths(self, tests, path):
        assert tests.is_akeyless_path(path)

    @pytest.mark.parametrize("path", [
        "no/leading/slash",
        "/trailing/slash/",
        "/with whitespace",
        "  /padded ",
        "/with/../traversal",
        "/with/./dot",
        "",
        "/",  # bare root has no segment
        "//empty/segment",
    ])
    def test_invalid_paths(self, tests, path):
        assert not tests.is_akeyless_path(path)

    @pytest.mark.parametrize("value", [None, 123, [], {}, b"/bytes/path"])
    def test_non_strings_rejected(self, tests, value):
        assert not tests.is_akeyless_path(value)


# ---------------------------------------------------------------------------
# is_akeyless_access_id
# ---------------------------------------------------------------------------


class TestIsAkeylessAccessId:

    @pytest.mark.parametrize("value", [
        "p-abcdef0123456789",
        "p-ABCDEF0123456789",
        "p-1234567890abcdef",
        "p-1234567890abcdef00",  # longer is fine
    ])
    def test_valid_access_ids(self, tests, value):
        assert tests.is_akeyless_access_id(value)

    @pytest.mark.parametrize("value", [
        "abcdef0123456789",   # missing p- prefix
        "p-short",            # too short
        "p-not-hex-1234567",  # not hex
        "P-abcdef0123456789", # uppercase prefix
        "",
    ])
    def test_invalid_access_ids(self, tests, value):
        assert not tests.is_akeyless_access_id(value)

    def test_non_string_rejected(self, tests):
        assert not tests.is_akeyless_access_id(None)
        assert not tests.is_akeyless_access_id(12345)


# ---------------------------------------------------------------------------
# is_pem_block
# ---------------------------------------------------------------------------


class TestIsPemBlock:

    def test_valid_single_cert_block(self, tests):
        pem = (
            "-----BEGIN CERTIFICATE-----\n"
            "AAAA\n"
            "-----END CERTIFICATE-----"
        )
        assert tests.is_pem_block(pem)

    def test_valid_rsa_private_key_block(self, tests):
        pem = (
            "-----BEGIN RSA PRIVATE KEY-----\n"
            "KKKK\n"
            "-----END RSA PRIVATE KEY-----"
        )
        assert tests.is_pem_block(pem)

    def test_tolerates_surrounding_whitespace(self, tests):
        pem = (
            "\n\n  "
            "-----BEGIN CERTIFICATE-----\n"
            "AAAA\n"
            "-----END CERTIFICATE-----"
            "\n\n"
        )
        assert tests.is_pem_block(pem)

    def test_rejects_unwrapped_string(self, tests):
        assert not tests.is_pem_block("just plain text")

    def test_rejects_missing_end_marker(self, tests):
        pem = "-----BEGIN CERTIFICATE-----\nAAAA"
        assert not tests.is_pem_block(pem)

    def test_rejects_empty(self, tests):
        assert not tests.is_pem_block("")
        assert not tests.is_pem_block("\n\n")

    def test_rejects_non_string(self, tests):
        assert not tests.is_pem_block(None)
        assert not tests.is_pem_block(b"-----BEGIN CERTIFICATE-----")


# ---------------------------------------------------------------------------
# is_base64
# ---------------------------------------------------------------------------


class TestIsBase64:

    def test_valid_base64_strings(self, tests):
        assert tests.is_base64("aGVsbG8gd29ybGQ=")   # "hello world"
        assert tests.is_base64("YWJjZA==")            # "abcd"
        assert tests.is_base64("")                    # empty is valid base64

    def test_rejects_non_alphabet_chars(self, tests):
        """validate=True rejects @ # $ etc that fall outside the
        base64 alphabet."""
        assert not tests.is_base64("@@@@invalid")
        assert not tests.is_base64("hello, world")

    def test_rejects_bad_padding(self, tests):
        """Padding must be present and the right length."""
        assert not tests.is_base64("aGVsbG8")  # missing padding

    def test_rejects_non_string(self, tests):
        assert not tests.is_base64(None)
        assert not tests.is_base64(b"YWJjZA==")
        assert not tests.is_base64(12345)
