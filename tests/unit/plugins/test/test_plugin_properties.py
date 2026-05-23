# Copyright: (c) 2026, pleme-io
# MIT License
#
# Hypothesis property tests for plugins/test/akeyless.py. Existing
# test_akeyless_tests.py covers fixed cases; this file generates
# random inputs to catch the edge cases hand-written tests miss.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import base64
import importlib.util
import sys
from pathlib import Path

import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

REPO_ROOT = Path(__file__).resolve().parents[4]
TEST_PLUGIN_DIR = REPO_ROOT / "plugins" / "test"
PER_TEST_FILES = {
    "is_akeyless_path": TEST_PLUGIN_DIR / "is_akeyless_path.py",
    "is_akeyless_access_id": TEST_PLUGIN_DIR / "is_akeyless_access_id.py",
    "is_pem_block": TEST_PLUGIN_DIR / "is_pem_block.py",
    "is_base64": TEST_PLUGIN_DIR / "is_base64.py",
}

_PROP_SETTINGS = dict(deadline=None,
                       suppress_health_check=[HealthCheck.function_scoped_fixture])


@pytest.fixture(scope="module")
def tests():
    """Merge per-test-file exports onto one object so existing test
    methods reach them as `tests.<test_name>`."""
    merged = type("MergedTestPlugins", (), {})()
    for name, path in PER_TEST_FILES.items():
        spec = importlib.util.spec_from_file_location(
            f"_prop_test_under_test_{name}", path
        )
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        setattr(merged, name, getattr(mod, name))
    return merged


# Strategies for generating "looks-real" akeyless paths and identifiers.
valid_path_segment = st.from_regex(r"^[A-Za-z0-9_-]{1,20}$", fullmatch=True)
valid_path = st.builds(
    lambda segs: "/" + "/".join(segs),
    st.lists(valid_path_segment, min_size=1, max_size=5),
)


# ---------------------------------------------------------------------------
# is_akeyless_path properties
# ---------------------------------------------------------------------------


class TestIsAkeylessPathProperties:

    @given(path=valid_path)
    @settings(max_examples=200, **_PROP_SETTINGS)
    def test_random_valid_paths_accepted(self, tests, path):
        """Any path built from [/<segment>]+ where each segment is
        [A-Za-z0-9_-] must validate."""
        assert tests.is_akeyless_path(path), f"valid path rejected: {path!r}"

    @given(path=st.text(min_size=1, max_size=50))
    @settings(max_examples=200, **_PROP_SETTINGS)
    def test_paths_with_whitespace_always_rejected(self, tests, path):
        """Whitespace anywhere -> reject (invariant: clean paths only)."""
        if any(c.isspace() for c in path):
            assert not tests.is_akeyless_path(path), (
                f"path with whitespace was accepted: {path!r}"
            )

    @given(prefix=valid_path)
    @settings(max_examples=50, **_PROP_SETTINGS)
    def test_traversal_segments_always_rejected(self, tests, prefix):
        """Adding /../ or /./ to a valid path always invalidates it."""
        assert not tests.is_akeyless_path(prefix + "/../escape")
        assert not tests.is_akeyless_path(prefix + "/./relative")

    @given(path=valid_path)
    @settings(max_examples=50, **_PROP_SETTINGS)
    def test_trailing_slash_always_rejected(self, tests, path):
        assert not tests.is_akeyless_path(path + "/")

    @given(value=st.one_of(
        st.none(), st.integers(), st.booleans(), st.lists(st.text()),
        st.dictionaries(st.text(max_size=5), st.text(max_size=5), max_size=3),
        st.binary(max_size=20),
    ))
    @settings(max_examples=50, **_PROP_SETTINGS)
    def test_non_strings_always_return_false(self, tests, value):
        """Non-string inputs (including bytes) return False, never raise."""
        assert tests.is_akeyless_path(value) is False


# ---------------------------------------------------------------------------
# is_akeyless_access_id properties
# ---------------------------------------------------------------------------


class TestIsAkeylessAccessIdProperties:

    @given(hex_chars=st.from_regex(r"^[a-fA-F0-9]{16,32}$", fullmatch=True))
    @settings(max_examples=100, **_PROP_SETTINGS)
    def test_p_prefix_plus_hex_accepted(self, tests, hex_chars):
        assert tests.is_akeyless_access_id(f"p-{hex_chars}")

    @given(non_hex=st.text(
        alphabet=st.characters(blacklist_characters="abcdefABCDEF0123456789-"),
        min_size=16, max_size=16,
    ))
    @settings(max_examples=50, **_PROP_SETTINGS)
    def test_non_hex_after_prefix_rejected(self, tests, non_hex):
        assert not tests.is_akeyless_access_id(f"p-{non_hex}")

    @given(value=st.one_of(
        st.none(), st.integers(), st.binary(max_size=20),
        st.lists(st.text(max_size=5), max_size=3),
    ))
    @settings(max_examples=50, **_PROP_SETTINGS)
    def test_non_string_always_false(self, tests, value):
        assert tests.is_akeyless_access_id(value) is False


# ---------------------------------------------------------------------------
# is_pem_block properties
# ---------------------------------------------------------------------------


class TestIsPemBlockProperties:

    @given(
        kind=st.from_regex(r"^(CERTIFICATE|RSA PRIVATE KEY|PUBLIC KEY|EC PRIVATE KEY)$",
                            fullmatch=True),
        body=st.text(max_size=200),
    )
    @settings(max_examples=100, **_PROP_SETTINGS)
    def test_well_formed_pem_blocks_accepted(self, tests, kind, body):
        pem = f"-----BEGIN {kind}-----\n{body}\n-----END {kind}-----"
        assert tests.is_pem_block(pem)

    @given(text_no_markers=st.text(max_size=200).filter(
        lambda s: "BEGIN" not in s and "END" not in s
    ))
    @settings(max_examples=100, **_PROP_SETTINGS)
    def test_arbitrary_text_without_markers_rejected(self, tests, text_no_markers):
        assert not tests.is_pem_block(text_no_markers)

    @given(value=st.one_of(
        st.none(), st.integers(), st.binary(max_size=20),
    ))
    @settings(max_examples=30, **_PROP_SETTINGS)
    def test_non_string_always_false(self, tests, value):
        assert tests.is_pem_block(value) is False


# ---------------------------------------------------------------------------
# is_base64 properties
# ---------------------------------------------------------------------------


class TestIsBase64Properties:

    @given(payload=st.binary(min_size=1, max_size=100))
    @settings(max_examples=200, **_PROP_SETTINGS)
    def test_b64encode_output_is_always_valid(self, tests, payload):
        """For any binary payload, base64-encoding it produces a string
        that is_base64 must accept (round-trip property)."""
        encoded = base64.b64encode(payload).decode("ascii")
        assert tests.is_base64(encoded), (
            f"is_base64 rejected b64encode output: {encoded!r}"
        )

    @given(text=st.text(min_size=1, max_size=100).filter(
        lambda s: any(c not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
                       for c in s)
    ))
    @settings(max_examples=50, **_PROP_SETTINGS)
    def test_text_with_non_alphabet_rejected(self, tests, text):
        """Any string containing chars outside the base64 alphabet
        must be rejected (validate=True semantics)."""
        assert not tests.is_base64(text)

    @given(value=st.one_of(
        st.none(), st.integers(), st.binary(max_size=20),
    ))
    @settings(max_examples=30, **_PROP_SETTINGS)
    def test_non_string_always_false(self, tests, value):
        assert tests.is_base64(value) is False
