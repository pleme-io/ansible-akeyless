#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: esm
short_description: Manages an external secrets manager (ESM) in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage esm resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    binary_value:
      description: "Use this option if the external secret value is a base64 encoded binary"
      type: bool
    description:
      description: "Description of the external secret"
      type: str
    esm_name:
      description: "Name of the External Secrets Manager item"
      type: str
      required: true
    secret_name:
      description: "Name for the new external secret"
      type: str
      required: true
    tags:
      description: "Tags for the external secret"
      type: dict
    value:
      description: "Value of the external secret item, either text or base64 encoded binary"
      type: str
      required: true
'''

EXAMPLES = r'''
- name: Create esm
  esm:
    state: present

- name: Delete esm
  esm:
    state: absent
'''

RETURN = r'''
# No computed fields
'''

from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    run_standard_crud,
)

argument_spec = {
    'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
    'binary_value': {'type': 'bool'},
    'description': {'type': 'str'},
    'esm_name': {'type': 'str', 'required': True},
    'secret_name': {'type': 'str', 'required': True},
    'tags': {'type': 'dict'},
    'value': {'type': 'str', 'required': True},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label='esm',
        sdk_create=('EsmCreate', 'esm_create'),
        sdk_update=('EsmUpdate', 'esm_update'),
        sdk_delete=('EsmDelete', 'esm_delete'),
        sdk_read=('EsmGet', 'esm_get'),
    )


if __name__ == '__main__':
    main()
