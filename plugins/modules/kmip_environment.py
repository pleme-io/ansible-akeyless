#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: kmip_environment
short_description: Manages a KMIP environment in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage kmip_environment resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    certificate_ttl:
      description: "Server certificate TTL in days"
      type: int
    hostname:
      description: "Hostname"
      type: str
      required: true
    root:
      description: "Root path of KMIP Resources"
      type: str
      required: true
'''

EXAMPLES = r'''
- name: Create kmip_environment
  kmip_environment:
    state: present

- name: Delete kmip_environment
  kmip_environment:
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
    'certificate_ttl': {'type': 'int'},
    'hostname': {'type': 'str', 'required': True},
    'root': {'type': 'str', 'required': True},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="kmip_environment",
        sdk_create=("KmipServerSetup", "kmip_server_setup"),
        sdk_update=None,
        immutable=True,
        sdk_delete=("KmipDeleteServer", "kmip_delete_server"),
        sdk_read=("KmipDescribeServer", "kmip_describe_server"),
    )


if __name__ == '__main__':
    main()
