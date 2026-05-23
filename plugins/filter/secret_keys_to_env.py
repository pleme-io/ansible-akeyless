# -*- coding: utf-8 -*-
# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
name: secret_keys_to_env
short_description: Convert a dict into UPPER_SNAKE_CASE env-var shape
version_added: "0.2.5"
description:
  - "Converts a C({key: value}) dict (e.g. from C(secret_to_json)) into
    the UPPER_SNAKE_CASE env-var shape Ansible's C(environment:) block
    expects. Optionally prefixes every key."
  - "Hyphens and dots in keys are replaced with underscores so values
    survive shell-environment rules."
author:
  - "pleme-io (@pleme-io)"
options:
  _input:
    description: Source dict.
    required: true
    type: dict
  prefix:
    description: Optional string prefixed to every output key (before uppercasing).
    type: str
    default: ""
'''

EXAMPLES = r'''
- name: Run app with prefixed env vars
  ansible.builtin.command: ./app
  environment: "{{ config_dict | drzln0.akeyless.secret_keys_to_env(prefix='APP_') }}"
'''

RETURN = r'''
_value:
  description: A dict of UPPER_SNAKE_CASE env-var-shaped keys to string values.
  type: dict
'''

from ansible_collections.drzln0.akeyless.plugins.filter.akeyless import (
    secret_keys_to_env,
)


class FilterModule:
    def filters(self):
        return {"secret_keys_to_env": secret_keys_to_env}
