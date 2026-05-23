# -*- coding: utf-8 -*-
# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = """
name: is_akeyless_path
short_description: Test whether a value is a valid Akeyless secret path
version_added: "0.2.5"
description:
  - Returns C(True) when C(value) is a syntactically valid Akeyless
    secret path (leading slash, slash-delimited
    C([A-Za-z0-9_.-]+) segments, no trailing slash, no whitespace).
  - Defensively rejects C(.) and C(..) segments (no path-traversal).
  - Returns C(False) for any non-string input; never raises.
author:
  - "pleme-io (@pleme-io)"
options:
  _input:
    description: Value to test.
    required: true
    type: str
"""

EXAMPLES = """
- name: Validate a secret path before fetching
  ansible.builtin.assert:
    that: secret_path is drzln0.akeyless.is_akeyless_path

- name: Skip when path looks wrong
  ansible.builtin.fail:
    msg: "Bad secret path: {{ p }}"
  when: not (p is drzln0.akeyless.is_akeyless_path)
"""

RETURN = """
_value:
  description: True if value is a valid Akeyless path; False otherwise.
  type: bool
"""

import re
from typing import Any, Dict

from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_plugin_helpers import (
    akeyless_test,
)

_PATH_RE = re.compile(r"^/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*$")


@akeyless_test
def is_akeyless_path(value: str) -> bool:
    # @akeyless_test handles the non-string -> False guard + the
    # "any exception => False" safety net.
    if value != value.strip() or value.endswith("/"):
        return False
    if not _PATH_RE.match(value):
        return False
    segments = value.split("/")
    return "." not in segments and ".." not in segments


class TestModule:
    def tests(self) -> Dict[str, Any]:
        return {"is_akeyless_path": is_akeyless_path}
