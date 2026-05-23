#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Jinja2 test plugins for Akeyless secret content + path shapes.

Tests are addressed as `{{ value is drzln0.akeyless.<test_name> }}` in
playbook conditionals.
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import base64
import re
from typing import Any, Dict


# Akeyless path shape: leading slash, slash-delimited segments, each
# segment is [A-Za-z0-9_.-]. Permissive enough for the common cases
# without allowing path traversal (./..) or whitespace.
_PATH_RE = re.compile(r"^/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*$")

# Akeyless access ID shape: `p-` followed by 16 hex chars (the format
# used by the Akeyless console + CLI for access keys). Defensive
# pre-validation lets playbook authors fail-fast on typos.
_ACCESS_ID_RE = re.compile(r"^p-[a-fA-F0-9]{16,}$")


def is_akeyless_path(value: Any) -> bool:
    """True when value is a valid Akeyless secret path (e.g.
    "/app/db/password"). Rejects relative paths, traversal segments
    ('..'), and trailing slashes.

    Usage:
        - name: Skip when path looks wrong
          ansible.builtin.fail:
            msg: "Bad secret path: {{ p }}"
          when: not p is drzln0.akeyless.is_akeyless_path
    """
    if not isinstance(value, str):
        return False
    if value != value.strip() or value.endswith("/"):
        return False
    if not _PATH_RE.match(value):
        return False
    # Defensive: reject `.` / `..` segments even though they pass the
    # regex via the dot character class. Neither is a meaningful
    # Akeyless name and they could enable path-manipulation injection
    # through poorly-normalized callers.
    segments = value.split("/")
    return "." not in segments and ".." not in segments


def is_akeyless_access_id(value: Any) -> bool:
    """True when value matches the Akeyless access-ID format
    (`p-<hex>`). Useful for pre-validating playbook variables before
    handing them to the auth call.

    Usage:
        - name: Verify access_id env var format
          ansible.builtin.assert:
            that: lookup('env', 'AKEYLESS_ACCESS_ID') is drzln0.akeyless.is_akeyless_access_id
    """
    if not isinstance(value, str):
        return False
    return bool(_ACCESS_ID_RE.match(value))


def is_pem_block(value: Any) -> bool:
    """True when value is a single PEM-formatted block (begins with
    -----BEGIN ... ----- and ends with -----END ... -----). Doesn't
    validate the base64 body -- structural check only.

    Usage:
        - name: Branch on whether the secret is a cert
          ansible.builtin.set_fact:
            cert_format: "{{ 'pem' if secret is drzln0.akeyless.is_pem_block else 'raw' }}"
    """
    if not isinstance(value, str):
        return False
    lines = value.strip().splitlines()
    if not lines:
        return False
    first, last = lines[0].strip(), lines[-1].strip()
    return (
        first.startswith("-----BEGIN ") and first.endswith("-----")
        and last.startswith("-----END ") and last.endswith("-----")
    )


def is_base64(value: Any) -> bool:
    """True when value is a string that decodes as valid base64
    (strict mode -- only the base64 alphabet, correct padding).

    Usage:
        - name: Choose decoding strategy
          ansible.builtin.set_fact:
            decoded: "{{ secret | drzln0.akeyless.b64decode_secret
                          if secret is drzln0.akeyless.is_base64
                          else secret }}"
    """
    if not isinstance(value, str):
        return False
    try:
        base64.b64decode(value, validate=True)
        return True
    except (ValueError, base64.binascii.Error):
        return False


class TestModule:
    """Register the akeyless tests with Ansible's test plugin registry."""

    def tests(self) -> Dict[str, Any]:
        return {
            "is_akeyless_path": is_akeyless_path,
            "is_akeyless_access_id": is_akeyless_access_id,
            "is_pem_block": is_pem_block,
            "is_base64": is_base64,
        }
