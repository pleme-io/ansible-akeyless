# Copyright: (c) 2026, pleme-io
# MIT License
#
# Unit tests for the mask_secret + secret_strength filters added to
# plugins/filter/akeyless.py.

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
    ansible_pkg = sys.modules.setdefault("ansible", types.ModuleType("ansible"))
    errors_mod = sys.modules.get("ansible.errors")
    if errors_mod is None:
        errors_mod = types.ModuleType("ansible.errors")
        sys.modules["ansible.errors"] = errors_mod
        ansible_pkg.errors = errors_mod
    if not hasattr(errors_mod, "AnsibleFilterError"):
        class _StubE(Exception):
            pass
        errors_mod.AnsibleFilterError = _StubE


@pytest.fixture(scope="module")
def filters():
    _install_ansible_errors_stub()
    spec = importlib.util.spec_from_file_location(
        "akeyless_filters_mask_strength", FILTER_PATH
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["akeyless_filters_mask_strength"] = mod
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# mask_secret
# ---------------------------------------------------------------------------


class TestMaskSecret:

    def test_default_reveals_first_four(self, filters):
        assert filters.mask_secret("p-abcdef0123456789") == "p-ab********"

    def test_show_first_and_last(self, filters):
        # 24-char input, show_first=4 + show_last=4 -> head + ******** + tail
        out = filters.mask_secret("ABCDEFGHIJKLMNOPQRSTUVWX",
                                  show_first=4, show_last=4)
        assert out == "ABCD********UVWX"

    def test_custom_mask_char(self, filters):
        out = filters.mask_secret("hello-world", show_first=2,
                                  show_last=0, mask_char="#")
        assert out == "he########"

    def test_full_overlap_returns_full_mask(self, filters):
        """When show_first + show_last would reveal the entire value
        (or more), the filter must NOT echo the original -- it returns
        a fixed-length fully-masked block."""
        assert filters.mask_secret("ab", show_first=2, show_last=0) == "********"
        assert filters.mask_secret("ab", show_first=4, show_last=4) == "********"
        assert filters.mask_secret("hi", show_first=1, show_last=1) == "********"

    def test_empty_string_returns_full_mask(self, filters):
        """Edge case: empty input still returns the mask sentinel so
        callers can't distinguish 'empty secret' from 'unmasked'
        in the output."""
        assert filters.mask_secret("") == "********"

    def test_rejects_non_string_input(self, filters):
        from ansible.errors import AnsibleFilterError
        with pytest.raises(AnsibleFilterError, match="expects a string"):
            filters.mask_secret(b"raw-bytes")
        with pytest.raises(AnsibleFilterError, match="expects a string"):
            filters.mask_secret(None)

    def test_rejects_negative_window(self, filters):
        from ansible.errors import AnsibleFilterError
        with pytest.raises(AnsibleFilterError, match=">= 0"):
            filters.mask_secret("hello", show_first=-1)
        with pytest.raises(AnsibleFilterError, match=">= 0"):
            filters.mask_secret("hello", show_last=-2)

    def test_rejects_non_int_window(self, filters):
        from ansible.errors import AnsibleFilterError
        with pytest.raises(AnsibleFilterError, match="must be ints"):
            filters.mask_secret("hello", show_first="4")

    def test_rejects_multi_char_mask(self, filters):
        from ansible.errors import AnsibleFilterError
        with pytest.raises(AnsibleFilterError, match="single character"):
            filters.mask_secret("hello", mask_char="**")
        with pytest.raises(AnsibleFilterError, match="single character"):
            filters.mask_secret("hello", mask_char="")


# ---------------------------------------------------------------------------
# secret_strength
# ---------------------------------------------------------------------------


class TestSecretStrength:

    def test_returns_dict_with_required_keys(self, filters):
        out = filters.secret_strength("hello")
        assert set(out) == {"length", "entropy_bits", "classification"}

    def test_empty_string_is_weak(self, filters):
        out = filters.secret_strength("")
        assert out["length"] == 0
        assert out["entropy_bits"] == 0.0
        assert out["classification"] == "weak"

    def test_short_dictionary_word_is_weak(self, filters):
        out = filters.secret_strength("password")
        assert out["classification"] == "weak"

    def test_random_short_string_is_moderate_or_strong(self, filters):
        """A 16-char mix of letters + digits has > 60 bits of entropy
        by Shannon estimation -> moderate or strong."""
        out = filters.secret_strength("Ab3xK9pQrLm2Vt8w")
        assert out["classification"] in ("moderate", "strong")
        assert out["entropy_bits"] > 40

    def test_long_random_string_is_vault(self, filters):
        """A 64-char string with high char diversity hits the
        vault threshold (>= 128 bits)."""
        # 64 chars, 32 unique -> char_entropy = log2(32) = 5 bits/char
        # total = 5 * 64 = 320 bits -- well into vault.
        sample = "abcdefghijklmnopqrstuvwxyz0123456" * 2  # 66 chars, plenty of diversity
        out = filters.secret_strength(sample[:64])
        assert out["classification"] == "vault"

    def test_single_repeated_char_is_weak(self, filters):
        """A long string of the same char has near-zero entropy --
        all the bits cancel because char-prob is 1.0."""
        out = filters.secret_strength("a" * 100)
        assert out["entropy_bits"] == 0.0
        assert out["classification"] == "weak"

    def test_length_matches_input(self, filters):
        out = filters.secret_strength("abcdef")
        assert out["length"] == 6

    def test_entropy_bits_is_rounded(self, filters):
        """Returned entropy is rounded to 2 decimals for readability
        in playbook output (otherwise long IEEE floats clutter logs)."""
        out = filters.secret_strength("abc")
        # 3 unique chars, length 3 -> char_entropy = log2(3) ~= 1.58
        # total ~ 4.75; rounded to 2 dp
        s = str(out["entropy_bits"])
        # max 2 chars after the decimal point
        assert "." in s and len(s.split(".")[1]) <= 2

    def test_rejects_non_string(self, filters):
        from ansible.errors import AnsibleFilterError
        with pytest.raises(AnsibleFilterError, match="expects a string"):
            filters.secret_strength(b"bytes")
        with pytest.raises(AnsibleFilterError, match="expects a string"):
            filters.secret_strength(None)


# ---------------------------------------------------------------------------
# FilterModule registration includes the new filters
# ---------------------------------------------------------------------------


def test_filter_module_registers_mask_and_strength(filters):
    fm = filters.FilterModule()
    registered = fm.filters()
    assert "mask_secret" in registered
    assert "secret_strength" in registered
    # Total filter count should be 7 (existing 5 + 2 new)
    assert len(registered) == 7
