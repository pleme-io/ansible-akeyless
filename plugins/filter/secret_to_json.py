# -*- coding: utf-8 -*-
# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
name: secret_to_json
short_description: Parse a JSON-stored secret value into native data
version_added: "0.2.5"
description:
  - Akeyless commonly stores complex structures (auth configs, KV maps,
    embedded certs) as JSON strings; callers want them as native
    dicts/lists in Ansible.
  - Wraps C(json.loads) with a clearer error message than the default
    C(JSONDecodeError) stack, including a 60-character preview of the
    value to aid diagnosis (without dumping a potentially-large secret
    to the log).
author:
  - "pleme-io (@pleme-io)"
options:
  _input:
    description: JSON-formatted secret value.
    required: true
    type: str
'''

EXAMPLES = r'''
- name: Parse a JSON-stored config
  ansible.builtin.set_fact:
    config: "{{ lookup('drzln0.akeyless.secret', '/app/config')
                | drzln0.akeyless.secret_to_json }}"
'''

RETURN = r'''
_value:
  description: Parsed JSON value (dict / list / scalar).
  type: raw
'''

from ansible_collections.drzln0.akeyless.plugins.filter.akeyless import (
    secret_to_json,
)


class FilterModule:
    def filters(self):
        return {"secret_to_json": secret_to_json}
