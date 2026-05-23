# -*- coding: utf-8 -*-
# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
name: secret_strength
short_description: Shannon-entropy + heuristic strength score for a secret
version_added: "0.2.5"
description:
  - "Computes the Shannon entropy of the input string times its length
    to approximate total entropy bits, then classifies by cutoff."
  - "C(< 40 bits) -> C(weak) (passwords, dictionary words)"
  - "C(40-80 bits) -> C(moderate) (short random strings)"
  - "C(80-128 bits) -> C(strong) (medium random strings, tokens)"
  - "C(>= 128 bits) -> C(vault) (full-entropy keys)"
  - "Returns C({length, entropy_bits, classification})."
author:
  - "pleme-io (@pleme-io)"
options:
  _input:
    description: Secret string to score.
    required: true
    type: str
'''

EXAMPLES = r'''
- name: Reject weak rotated passwords
  ansible.builtin.assert:
    that:
      - (rotated_password | drzln0.akeyless.secret_strength).classification != 'weak'
'''

RETURN = r'''
_value:
  description: "Strength report dict: length (int), entropy_bits (float), classification (str)."
  type: dict
'''

from ansible_collections.drzln0.akeyless.plugins.filter.akeyless import (
    secret_strength,
)


class FilterModule:
    def filters(self):
        return {"secret_strength": secret_strength}
