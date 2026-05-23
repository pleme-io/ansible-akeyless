# -*- coding: utf-8 -*-
# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = """
name: akeyless_token
short_description: Cache Akeyless auth tokens across tasks / plays
description:
  - File-backed cache for Akeyless access tokens. Avoids per-task /
    per-play re-auth when running large playbooks against the same
    Akeyless account.
  - Stores tokens in a JSON file with a per-key TTL. Default TTL is
    25 minutes -- Akeyless tokens are good for 60 by default, so we
    refresh well before expiry.
  - Read by the lookup / inventory plugins when their `token` option
    is unset AND a cached entry exists. Written by them when a fresh
    auth call returns a new token.
author:
  - "pleme-io (@pleme-io)"
version_added: "0.2.6"

options:
  _uri:
    description: Directory the cache file lives in.
    type: path
    default: ~/.cache/ansible/akeyless
    env:
      - name: ANSIBLE_CACHE_PLUGIN_CONNECTION
    ini:
      - section: defaults
        key: fact_caching_connection
  _prefix:
    description: Filename prefix for cache entries.
    type: str
    default: "akeyless_token_"
    env:
      - name: ANSIBLE_CACHE_PLUGIN_PREFIX
    ini:
      - section: defaults
        key: fact_caching_prefix
  _timeout:
    description: TTL in seconds for cached tokens. Default 1500 (25
                 minutes); leaves ~35 minutes of headroom on the
                 typical 60-minute Akeyless token lifetime.
    type: int
    default: 1500
    env:
      - name: ANSIBLE_CACHE_PLUGIN_TIMEOUT
    ini:
      - section: defaults
        key: fact_caching_timeout

requirements:
  - ansible-core >= 2.14
"""

EXAMPLES = """
# ansible.cfg:
#
# [defaults]
# fact_caching = drzln0.akeyless.akeyless_token
# fact_caching_connection = /var/cache/ansible/akeyless
# fact_caching_timeout = 1500
"""

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from ansible.plugins.cache import BaseCacheModule


class CacheModule(BaseCacheModule):
    """File-backed token cache. One JSON file per cache key, keyed by
    (gateway_url, access_id) hash so distinct Akeyless tenants /
    auth identities don't collide.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._cache_dir = Path(
            os.path.expanduser(self._get_option("_uri") or "~/.cache/ansible/akeyless")
        )
        self._prefix = self._get_option("_prefix") or "akeyless_token_"
        self._timeout = int(self._get_option("_timeout") or 1500)
        # NOTE: We intentionally don't mkdir here. Two reasons:
        #   1. Constructing the cache module shouldn't have file-system
        #      side effects (some CI sandboxes -- e.g. nix's
        #      build-time tests -- run without HOME set, so the
        #      default ~/.cache path fails PermissionError).
        #   2. Lazy mkdir is cheaper at module-load time when callers
        #      construct the cache just to introspect options.
        # `_ensure_dir()` is called from set() / get() / keys() etc.
        # before any actual file IO.

    def _ensure_dir(self) -> None:
        """Lazily create the cache directory. Called before every
        file-touching operation. Idempotent + tolerant of races."""
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_option(self, name: str) -> Any:
        try:
            return self.get_option(name)
        except Exception:
            return None

    def _path_for(self, key: str) -> Path:
        # Sanitize the key for filesystem safety -- replace any non-
        # alphanumeric character with underscore.
        safe = "".join(c if c.isalnum() else "_" for c in key)
        return self._cache_dir / f"{self._prefix}{safe}.json"

    def _entry_alive(self, path: Path) -> bool:
        """An entry is alive when the file exists AND its mtime is
        within _timeout seconds of now. Atomic atomic-rename writes
        ensure the mtime reflects the entry's true creation time."""
        if not path.exists():
            return False
        age = time.time() - path.stat().st_mtime
        return age < self._timeout

    def get(self, key: str) -> Any:
        """Return the cached value for `key` if alive; else raise
        KeyError (Ansible's cache contract)."""
        path = self._path_for(key)
        if not self._entry_alive(path):
            raise KeyError(key)
        try:
            return json.loads(path.read_text())
        except (OSError, ValueError):
            # Corrupt / unreadable cache entry: treat as a miss + cleanup.
            try:
                path.unlink()
            except OSError:
                pass
            raise KeyError(key)

    def set(self, key: str, value: Any) -> None:
        """Atomically write `value` (json-serialised) to the cache file.
        Uses tmpfile + rename so partial writes never leave a corrupt
        entry visible to a concurrent reader."""
        self._ensure_dir()
        path = self._path_for(key)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(value))
        os.replace(tmp, path)
        # Restrict perms: tokens are sensitive; world-readable would
        # defeat the whole point. 0600 = owner read+write only.
        os.chmod(path, 0o600)

    def keys(self) -> List[str]:
        if not self._cache_dir.exists():
            return []
        out = []
        for p in self._cache_dir.glob(f"{self._prefix}*.json"):
            stem = p.stem
            if stem.startswith(self._prefix):
                out.append(stem[len(self._prefix):])
        return out

    def contains(self, key: str) -> bool:
        return self._entry_alive(self._path_for(key))

    def delete(self, key: str) -> None:
        path = self._path_for(key)
        try:
            path.unlink()
        except FileNotFoundError:
            pass

    def flush(self) -> None:
        """Remove every cached entry. Useful for forced re-auth."""
        if not self._cache_dir.exists():
            return
        for p in self._cache_dir.glob(f"{self._prefix}*.json"):
            try:
                p.unlink()
            except OSError:
                pass

    def copy(self) -> Dict[str, Any]:
        """Return a {key: value} snapshot of the live cache."""
        out: Dict[str, Any] = {}
        for key in self.keys():
            try:
                out[key] = self.get(key)
            except KeyError:
                pass
        return out
