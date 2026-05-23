# Copyright: (c) 2026, pleme-io
# MIT License
#
# Hypothesis property tests for plugins/cache/akeyless_token.py.
# Existing test_akeyless_token.py covers fixed cases; this file
# generates random inputs to exercise the cache's invariants.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import importlib.util
import sys
import types
from pathlib import Path

import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

REPO_ROOT = Path(__file__).resolve().parents[4]
CACHE_PATH = REPO_ROOT / "plugins" / "cache" / "akeyless_token.py"

_PROP_SETTINGS = dict(
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)


def _install_ansible_cache_stubs():
    ansible_pkg = sys.modules.setdefault("ansible", types.ModuleType("ansible"))
    plugins_mod = sys.modules.setdefault(
        "ansible.plugins", types.ModuleType("ansible.plugins")
    )
    ansible_pkg.plugins = plugins_mod
    if "ansible.plugins.cache" not in sys.modules:
        m = types.ModuleType("ansible.plugins.cache")

        class _BCM:
            def __init__(self, *args, **kwargs):
                self._opts = {}
            def get_option(self, name):
                return self._opts.get(name)
            def set_options(self, **kwargs):
                self._opts.update(kwargs)

        m.BaseCacheModule = _BCM
        sys.modules["ansible.plugins.cache"] = m


def _load_cache(tmp_path):
    _install_ansible_cache_stubs()
    spec = importlib.util.spec_from_file_location(
        f"akeyless_cache_props_{tmp_path.name}", CACHE_PATH
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    cm = mod.CacheModule()
    cm._cache_dir = Path(str(tmp_path))
    cm._prefix = "prop_"
    cm._timeout = 300
    cm._cache_dir.mkdir(parents=True, exist_ok=True)
    return cm


@pytest.fixture
def cache(tmp_path):
    return _load_cache(tmp_path)


# Strategies. Cache keys exercise the path-sanitization logic;
# values exercise the JSON serialization path.
cache_key = st.text(min_size=1, max_size=80)
json_safe_value = st.recursive(
    st.one_of(
        st.none(), st.booleans(),
        st.integers(min_value=-10**9, max_value=10**9),
        st.text(max_size=80),
    ),
    lambda children: st.one_of(
        st.lists(children, max_size=5),
        st.dictionaries(st.text(max_size=20), children, max_size=5),
    ),
    max_leaves=15,
)


# ---------------------------------------------------------------------------
# set → get round-trip across random key/value shapes
# ---------------------------------------------------------------------------


class TestSetGetProperties:

    @given(key=cache_key, value=json_safe_value)
    @settings(max_examples=200, **_PROP_SETTINGS)
    def test_set_then_get_round_trips(self, cache, key, value):
        """For any key + any json-serializable value, set+get must
        round-trip. Verifies the cache doesn't mangle / mis-serialize
        unusual key shapes or nested values."""
        cache.set(key, value)
        assert cache.get(key) == value

    @given(key=cache_key)
    @settings(max_examples=100, **_PROP_SETTINGS)
    def test_contains_consistent_with_get(self, cache, key):
        """contains(key) returns True iff get(key) doesn't raise.
        Pin this invariant since callers branch on contains()."""
        # Hypothesis reuses the function-scoped fixture across
        # examples; flush to isolate this case from siblings.
        cache.flush()
        assert not cache.contains(key)
        with pytest.raises(KeyError):
            cache.get(key)
        cache.set(key, "anything")
        assert cache.contains(key)
        assert cache.get(key) == "anything"

    @given(key=cache_key)
    @settings(max_examples=50, **_PROP_SETTINGS)
    def test_delete_makes_key_absent(self, cache, key):
        """delete() ALWAYS leaves contains(key) == False (whether the
        key existed before or not)."""
        cache.flush()  # isolate from siblings
        cache.set(key, "v")
        cache.delete(key)
        assert not cache.contains(key)
        cache.delete(key)
        assert not cache.contains(key)


# ---------------------------------------------------------------------------
# Path-sanitization invariants
# ---------------------------------------------------------------------------


class TestPathSafetyProperties:

    @given(key=st.text(
        # Generate adversarial keys: include /, .., \\, null bytes
        # (the key sanitizer must defend against all of them).
        alphabet=st.characters(
            blacklist_characters="\x00",  # null breaks Path; skip
            min_codepoint=0x20,
        ),
        min_size=1, max_size=100,
    ))
    @settings(max_examples=200, **_PROP_SETTINGS)
    def test_no_key_escapes_cache_dir(self, cache, key):
        """For ANY key, the resulting cache file MUST live directly
        under the cache dir -- no subdirectory creation, no
        ../escape, no absolute paths. Sanitization defends the
        cache dir's filesystem boundary."""
        path = cache._path_for(key)
        # The file must be a direct child of the cache dir.
        assert path.parent == cache._cache_dir, (
            f"key {key!r} produced path {path} escaping cache dir "
            f"{cache._cache_dir}"
        )

    @given(key=cache_key)
    @settings(max_examples=100, **_PROP_SETTINGS)
    def test_path_filename_contains_prefix(self, cache, key):
        """Every cache file name starts with the configured prefix,
        so keys() can find it via glob."""
        path = cache._path_for(key)
        assert path.name.startswith(cache._prefix)


# ---------------------------------------------------------------------------
# Security: secret values get 0600 perms regardless of input shape
# ---------------------------------------------------------------------------


class TestPermsInvariants:

    @given(key=cache_key, value=json_safe_value)
    @settings(max_examples=100, **_PROP_SETTINGS)
    def test_set_always_writes_0600(self, cache, key, value):
        """No matter the input, set() lands a file with mode 0600.
        Token data is sensitive; world-readable would defeat the
        cache's whole purpose."""
        cache.set(key, value)
        path = cache._path_for(key)
        mode = path.stat().st_mode & 0o777
        assert mode == 0o600


# ---------------------------------------------------------------------------
# keys() ↔ set() consistency
# ---------------------------------------------------------------------------


class TestKeysInvariants:

    @given(
        keys=st.lists(
            st.text(min_size=1, max_size=20,
                    alphabet=st.characters(whitelist_categories=("L", "N"))),
            min_size=1, max_size=10, unique=True,
        )
    )
    @settings(max_examples=50, **_PROP_SETTINGS)
    def test_keys_reflects_every_set_entry(self, cache, keys):
        """After setting N distinct keys, keys() returns exactly
        those N keys (modulo sanitization that might collide -- so
        we use alphanumeric-only inputs that survive sanitization)."""
        cache.flush()  # isolate from siblings
        for k in keys:
            cache.set(k, "v")
        listed = set(cache.keys())
        for k in keys:
            assert k in listed, (
                f"key {k!r} was set but missing from keys() listing"
            )

    @given(
        keys=st.lists(
            st.text(min_size=1, max_size=20,
                    alphabet=st.characters(whitelist_categories=("L", "N"))),
            min_size=1, max_size=10, unique=True,
        )
    )
    @settings(max_examples=30, **_PROP_SETTINGS)
    def test_flush_clears_every_key(self, cache, keys):
        """flush() returns the cache to empty regardless of what was set."""
        for k in keys:
            cache.set(k, "v")
        cache.flush()
        assert cache.keys() == []
