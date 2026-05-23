# Copyright: (c) 2026, pleme-io
# MIT License
#
# Unit tests for plugins/cache/akeyless_token.py -- file-backed
# token cache that lets the lookup/inventory plugins skip per-play
# re-auth.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import importlib.util
import os
import sys
import time
import types
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
CACHE_PATH = REPO_ROOT / "plugins" / "cache" / "akeyless_token.py"


def _install_ansible_cache_stubs():
    """Stub ansible.plugins.cache.BaseCacheModule with a minimum
    surface our CacheModule subclass needs (set_options-style
    get_option). Idempotent."""
    ansible_pkg = sys.modules.setdefault("ansible", types.ModuleType("ansible"))
    plugins_mod = sys.modules.setdefault(
        "ansible.plugins", types.ModuleType("ansible.plugins")
    )
    ansible_pkg.plugins = plugins_mod

    if "ansible.plugins.cache" not in sys.modules:
        cache_mod = types.ModuleType("ansible.plugins.cache")

        class _BCM:
            def __init__(self, *args, **kwargs):
                self._opts = {}

            def get_option(self, name):
                return self._opts.get(name)

            def set_options(self, **kwargs):
                self._opts.update(kwargs)

        cache_mod.BaseCacheModule = _BCM
        sys.modules["ansible.plugins.cache"] = cache_mod


def _load_cache(tmp_path):
    """Load the cache module + configure it to use tmp_path as the
    cache dir so tests don't touch ~/.cache."""
    _install_ansible_cache_stubs()
    spec = importlib.util.spec_from_file_location(
        f"akeyless_token_cache_{tmp_path.name}", CACHE_PATH
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    cm = mod.CacheModule()
    cm._opts = {
        "_uri": str(tmp_path),
        "_prefix": "test_",
        "_timeout": 300,
    }
    # Re-trigger __init__ logic that reads options.
    cm._cache_dir = Path(str(tmp_path))
    cm._prefix = "test_"
    cm._timeout = 300
    cm._cache_dir.mkdir(parents=True, exist_ok=True)
    return cm


@pytest.fixture
def cache(tmp_path):
    return _load_cache(tmp_path)


# ---------------------------------------------------------------------------
# set + get round-trip
# ---------------------------------------------------------------------------


def test_set_then_get_round_trips(cache):
    cache.set("k1", {"token": "tok-abc", "expires_at": 9999999})
    out = cache.get("k1")
    assert out == {"token": "tok-abc", "expires_at": 9999999}


def test_get_missing_key_raises_keyerror(cache):
    with pytest.raises(KeyError):
        cache.get("never-set")


def test_contains_returns_true_for_live_entry(cache):
    cache.set("k1", "v")
    assert cache.contains("k1")


def test_contains_returns_false_for_missing_entry(cache):
    assert not cache.contains("never-set")


# ---------------------------------------------------------------------------
# TTL
# ---------------------------------------------------------------------------


def test_expired_entry_raises_keyerror(cache):
    """An entry whose mtime is older than _timeout is considered
    dead -- get() must raise KeyError."""
    cache.set("k1", "v")
    # Backdate the file mtime to TTL+10s in the past.
    path = cache._path_for("k1")
    backdated = time.time() - (cache._timeout + 10)
    os.utime(path, (backdated, backdated))
    with pytest.raises(KeyError):
        cache.get("k1")


def test_expired_entry_contains_returns_false(cache):
    cache.set("k1", "v")
    path = cache._path_for("k1")
    backdated = time.time() - (cache._timeout + 10)
    os.utime(path, (backdated, backdated))
    assert not cache.contains("k1")


# ---------------------------------------------------------------------------
# delete + flush
# ---------------------------------------------------------------------------


def test_delete_removes_entry(cache):
    cache.set("k1", "v")
    cache.delete("k1")
    with pytest.raises(KeyError):
        cache.get("k1")


def test_delete_missing_key_is_no_op(cache):
    """delete() on a missing key must silently succeed -- callers
    treat the cache as best-effort."""
    cache.delete("never-set")  # should not raise


def test_flush_removes_every_entry(cache):
    cache.set("a", 1)
    cache.set("b", 2)
    cache.set("c", 3)
    cache.flush()
    for k in ("a", "b", "c"):
        assert not cache.contains(k)


# ---------------------------------------------------------------------------
# keys + copy
# ---------------------------------------------------------------------------


def test_keys_lists_set_entries(cache):
    cache.set("alpha", 1)
    cache.set("beta", 2)
    assert set(cache.keys()) == {"alpha", "beta"}


def test_copy_returns_snapshot(cache):
    cache.set("a", 1)
    cache.set("b", 2)
    snapshot = cache.copy()
    assert snapshot == {"a": 1, "b": 2}


# ---------------------------------------------------------------------------
# Security: token files must be 0600
# ---------------------------------------------------------------------------


def test_set_writes_0600_perms(cache):
    """Tokens are sensitive. Cache files must be world-unreadable."""
    cache.set("k1", "secret-token")
    path = cache._path_for("k1")
    mode = path.stat().st_mode & 0o777
    assert mode == 0o600, (
        f"cache file {path} has perms 0o{mode:o}, expected 0o600 "
        f"(tokens are sensitive; world-readable defeats the cache)"
    )


# ---------------------------------------------------------------------------
# Path safety
# ---------------------------------------------------------------------------


def test_key_with_unsafe_chars_is_sanitized(cache):
    """A key like 'https://gw/foo' must not create a directory
    structure in the cache dir. Non-alphanumeric chars become _."""
    cache.set("https://gw/foo", "v")
    # The file should exist; the slashes shouldn't have created
    # subdirectories.
    files = list(cache._cache_dir.glob("test_*.json"))
    assert len(files) == 1
    assert "https" in files[0].name
    # And the original key still round-trips.
    assert cache.get("https://gw/foo") == "v"


# ---------------------------------------------------------------------------
# Atomic write semantics
# ---------------------------------------------------------------------------


def test_corrupt_entry_treated_as_miss(cache):
    """A cache file with corrupt JSON should be treated as a miss
    (KeyError) AND the corrupt file should be cleaned up so the next
    write starts fresh."""
    path = cache._path_for("k1")
    path.write_text("{not valid json")
    with pytest.raises(KeyError):
        cache.get("k1")
    # The corrupt file should be gone after the failed get.
    assert not path.exists()
