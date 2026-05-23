#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: kmip_client_v2
short_description: Manages a KMIP client in Akeyless Vault (no update; changes force recreate)
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage kmip_client_v2 resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    activate_keys_on_creation:
      description: "If set to 'true', newly created keys on the client will be set to an 'active' state"
      type: str
    certificate_ttl:
      description: "Client certificate TTL in days"
      type: int
    name:
      description: "Client name"
      type: str
      required: true
'''

EXAMPLES = r'''
- name: Create kmip_client_v2
  kmip_client_v2:
    state: present

- name: Delete kmip_client_v2
  kmip_client_v2:
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
    'activate_keys_on_creation': {'type': 'str'},
    'certificate_ttl': {'type': 'int'},
    'name': {'type': 'str', 'required': True},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="kmip_client_v2",
        sdk_create=("KmipCreateClient", "kmip_create_client"),
        # WARNING: The following fields are immutable after creation.
        #   - activate_keys_on_creation
        #   - certificate_ttl
        #   - name
        # Changing them requires destroy + recreate.
        sdk_update=None,
        immutable=True,
        sdk_delete=("KmipDeleteClient", "kmip_delete_client"),
        sdk_read=("KmipDescribeClient", "kmip_describe_client"),
    )


if __name__ == '__main__':
    main()
