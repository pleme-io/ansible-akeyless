# -*- coding: utf-8 -*-
# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
name: mask_secret
short_description: Partial-reveal mask for log-safe secret display
version_added: "0.2.5"
description:
  - Shows the first C(show_first) chars + last C(show_last) chars of
    the value, replacing the middle with a fixed-length block of
    C(mask_char).
  - Defaults (C(show_first=4), C(show_last=0)) mirror the common
    C("p-abcd***") shape that surfaces enough of the value to
    recognize it without leaking the whole thing.
  - When the reveal windows overlap the entire value, the filter
    falls back to a fully-masked output so the secret can never leak
    via aggressive C(show_*) values.
author:
  - "pleme-io (@pleme-io)"
options:
  _input:
    description: Secret string to mask.
    required: true
    type: str
  show_first:
    description: Number of leading characters to reveal.
    type: int
    default: 4
  show_last:
    description: Number of trailing characters to reveal.
    type: int
    default: 0
  mask_char:
    description: Single character used for the masked middle block.
    type: str
    default: "*"
'''

EXAMPLES = r'''
- name: Log a masked access ID
  ansible.builtin.debug:
    msg: "Auth ID: {{ access_id | drzln0.akeyless.mask_secret }}"

- name: Show first 6 + last 4 of a token
  ansible.builtin.debug:
    msg: "Token: {{ tok | drzln0.akeyless.mask_secret(show_first=6, show_last=4) }}"
'''

RETURN = r'''
_value:
  description: Partially-masked string.
  type: str
'''

from ansible_collections.drzln0.akeyless.plugins.filter.akeyless import (
    mask_secret,
)


class FilterModule:
    def filters(self):
        return {"mask_secret": mask_secret}
