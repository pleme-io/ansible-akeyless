# -*- coding: utf-8 -*-
# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = """
name: is_akeyless_access_id
short_description: Test whether a value matches the Akeyless access-ID format
version_added: "0.2.5"
description:
  - Returns C(True) when C(value) is a string matching C(p-<hex>{16,})
    -- the format used by Akeyless console + CLI for access keys.
  - Useful for pre-validating playbook variables before handing them
    to the auth call.
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
- name: Verify access_id env var format
  ansible.builtin.assert:
    that: lookup('env', 'AKEYLESS_ACCESS_ID') is drzln0.akeyless.is_akeyless_access_id
"""

RETURN = """
_value:
  description: True if value matches the access-ID format; False otherwise.
  type: bool
"""

import re
from typing import Any, Dict

from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_plugin_helpers import (
    akeyless_test,
)

_ACCESS_ID_RE = re.compile(r"^p-[a-fA-F0-9]{16,}$")


@akeyless_test
def is_akeyless_access_id(value: str) -> bool:
    return bool(_ACCESS_ID_RE.match(value))


class TestModule:
    def tests(self) -> Dict[str, Any]:
        return {"is_akeyless_access_id": is_akeyless_access_id}
