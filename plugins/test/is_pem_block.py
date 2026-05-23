# -*- coding: utf-8 -*-
# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = """
name: is_pem_block
short_description: Test whether a value is a single PEM block
version_added: "0.2.5"
description:
  - Returns C(True) when C(value) is a string wrapped in PEM
    C(-----BEGIN ...-----) / C(-----END ...-----) markers.
  - Structural check only -- does not validate the base64 body.
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
- name: Branch on whether the secret is a cert
  ansible.builtin.set_fact:
    cert_format: "{{ 'pem' if secret is drzln0.akeyless.is_pem_block else 'raw' }}"
"""

RETURN = """
_value:
  description: True if value is a PEM block; False otherwise.
  type: bool
"""

from typing import Any, Dict


def is_pem_block(value: Any) -> bool:
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


class TestModule:
    def tests(self) -> Dict[str, Any]:
        return {"is_pem_block": is_pem_block}
