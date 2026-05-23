#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
name: akeyless_redactor
type: stdout
short_description: Defensive secondary-pass redaction of Akeyless secret values
description:
  - Wraps the default stdout callback to defensively redact any
    string in the task result that matches a configurable set of
    suspicion patterns (PEM blocks, base64-encoded blobs, Akeyless
    access IDs).
  - C(no_log=true) on the producing task is the primary defense;
    this callback is a secondary pass that catches values which
    escape into result fields where the module author forgot to flag
    them sensitive. Defense in depth.
author:
  - "pleme-io (@pleme-io)"
version_added: "0.2.5"

options:
  redaction_token:
    description: The string substituted for any value detected as a secret.
    type: str
    default: '*** redacted by akeyless_redactor ***'
    env:
      - name: ANSIBLE_AKEYLESS_REDACTION_TOKEN
    ini:
      - section: callback_akeyless_redactor
        key: redaction_token
  min_secret_length:
    description: Strings shorter than this byte length are left
                 unredacted. Prevents redacting trivial short values
                 that happen to look base64-ish.
    type: int
    default: 32
    env:
      - name: ANSIBLE_AKEYLESS_MIN_SECRET_LENGTH

requirements:
  - ansible-core >= 2.14

extends_documentation_fragment:
  - ansible.builtin.default_callback
'''

EXAMPLES = r'''
# ansible.cfg:
#
# [defaults]
# stdout_callback = drzln0.akeyless.akeyless_redactor
# bin_ansible_callbacks = True
#
# [callback_akeyless_redactor]
# redaction_token = REDACTED
# min_secret_length = 24
'''

import base64
import re
from typing import Any, Dict, List, Set

from ansible.plugins.callback import CallbackBase

# Import the default callback we wrap. Doing it inside try/except lets
# unit tests load this file without ansible.plugins.callback.default
# being present (the test installs a stub).
try:
    from ansible.plugins.callback.default import CallbackModule as DefaultCallback
    _HAS_DEFAULT_CALLBACK = True
except ImportError:
    DefaultCallback = CallbackBase  # type: ignore[assignment,misc]
    _HAS_DEFAULT_CALLBACK = False


# Suspicion patterns. A value matching ANY of these and exceeding
# `min_secret_length` bytes gets redacted.
_PEM_RE = re.compile(r"-----BEGIN [A-Z ]+-----")
_AKEYLESS_ACCESS_ID_RE = re.compile(r"\bp-[a-fA-F0-9]{16,}\b")
_AKEYLESS_PATH_RE = re.compile(r"\bakeyless[a-z_]*\b", re.IGNORECASE)


def _looks_like_base64(value: str) -> bool:
    """Heuristic base64 detection: only base64 alphabet chars and
    correct padding. Cheap to compute via base64.b64decode(validate=True).
    """
    if not value or len(value) % 4 != 0:
        return False
    try:
        base64.b64decode(value, validate=True)
        return True
    except (ValueError, base64.binascii.Error):
        return False


def _is_suspicious(value: str, min_length: int) -> bool:
    """Return True when the value should be redacted. False otherwise.
    Short values + obviously-non-secret content (URLs, file paths)
    pass through unredacted to keep the output useful."""
    if len(value) < min_length:
        return False
    if _PEM_RE.search(value):
        return True
    if _AKEYLESS_ACCESS_ID_RE.search(value):
        return True
    # Substantial-length pure base64 -> very likely a key/cert blob.
    if _looks_like_base64(value):
        return True
    return False


def _redact_in_place(node: Any, token: str, min_length: int,
                      seen: Set[int]) -> Any:
    """Walk a result tree (dict/list/scalar) and replace any suspicious
    string with `token`. Mutates dicts/lists in place, returns scalars
    (callers re-bind the parent ref). `seen` tracks already-visited
    container ids to defend against cycles."""
    if id(node) in seen:
        return node
    if isinstance(node, dict):
        seen.add(id(node))
        for k, v in list(node.items()):
            node[k] = _redact_in_place(v, token, min_length, seen)
        return node
    if isinstance(node, list):
        seen.add(id(node))
        for i, v in enumerate(node):
            node[i] = _redact_in_place(v, token, min_length, seen)
        return node
    if isinstance(node, str) and _is_suspicious(node, min_length):
        return token
    return node


class CallbackModule(DefaultCallback):
    """Defensive stdout-callback that redacts Akeyless-shaped secrets
    from task results before they're rendered."""

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "stdout"
    CALLBACK_NAME = "drzln0.akeyless.akeyless_redactor"

    def __init__(self) -> None:
        super().__init__()
        self._redaction_token = "*** redacted by akeyless_redactor ***"
        self._min_secret_length = 32

    def set_options(self, task_keys=None, var_options=None, direct=None) -> None:
        super().set_options(task_keys=task_keys, var_options=var_options, direct=direct)
        try:
            self._redaction_token = self.get_option("redaction_token") or self._redaction_token
            self._min_secret_length = int(self.get_option("min_secret_length") or self._min_secret_length)
        except Exception:
            # Defensive: keep operating with defaults if get_option
            # is unavailable (older ansible-core compat).
            pass

    def _redact(self, result_obj: Any) -> None:
        """Apply redaction to a TaskResult-like object's _result dict
        in place. The default callback reads result._result.<field> when
        rendering, so mutating _result before super() forwards the
        sanitized view."""
        result_dict = getattr(result_obj, "_result", None)
        if isinstance(result_dict, dict):
            _redact_in_place(
                result_dict,
                self._redaction_token,
                self._min_secret_length,
                seen=set(),
            )

    # Override the OK / FAILED / UNREACHABLE callbacks to redact
    # before delegating to the default-callback renderer. The other
    # CallbackBase entrypoints (playbook start/end, host stats) don't
    # carry secret-laden payloads so we leave them untouched.

    def v2_runner_on_ok(self, result):
        self._redact(result)
        return super().v2_runner_on_ok(result)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self._redact(result)
        return super().v2_runner_on_failed(result, ignore_errors=ignore_errors)

    def v2_runner_on_unreachable(self, result):
        self._redact(result)
        return super().v2_runner_on_unreachable(result)
