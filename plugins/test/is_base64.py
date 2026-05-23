# -*- coding: utf-8 -*-
# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = """
name: is_base64
short_description: Test whether a value is a valid base64 string
version_added: "0.2.5"
description:
  - Returns C(True) when C(value) is a string that decodes cleanly
    via Python's C(base64.b64decode(validate=True)) (strict alphabet
    + correct padding).
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
- name: Choose decoding strategy based on secret shape
  ansible.builtin.set_fact:
    decoded: >-
      {{ secret | drzln0.akeyless.b64decode_secret
         if secret is drzln0.akeyless.is_base64
         else secret }}
"""

RETURN = """
_value:
  description: True if value is valid base64; False otherwise.
  type: bool
"""

import base64
from typing import Any, Dict


def is_base64(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        base64.b64decode(value, validate=True)
        return True
    except (ValueError, base64.binascii.Error):
        return False


class TestModule:
    def tests(self) -> Dict[str, Any]:
        return {"is_base64": is_base64}
