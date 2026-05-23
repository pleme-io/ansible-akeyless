#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_producer_aws
short_description: Manages an AWS gateway producer (deprecated; prefer akeyless_dynamic_secret_aws)
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage gateway_producer_aws resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    access_mode:
      description: ""
      type: str
    admin_rotation_interval_days:
      description: "Admin credentials rotation interval (days)"
      type: int

    aws_access_key_id:
      description: "Access Key ID"
      type: str
      required: true

    aws_access_secret_key:
      description: "Secret Access Key"
      type: str
      required: true
    aws_external_id:
      description: "The AWS External ID associated with the AWS role (relevant only for assume_role mode)"
      type: str
    aws_role_arns:
      description: "AWS Role ARNs to be used in the Assume Role operation (relevant only for assume_role mode)"
      type: str
    aws_user_console_access:
      description: "AWS User console access"
      type: bool
    aws_user_groups:
      description: "AWS User groups"
      type: str

    aws_user_policies:
      description: "AWS User policies"
      type: str
      required: true
    aws_user_programmatic_access:
      description: "Enable AWS User programmatic access"
      type: bool
    custom_username_template:
      description: "Customize how temporary usernames are generated using go template"
      type: str
    delete_protection:
      description: "Protection from accidental deletion of this object [true/false]"
      type: str
    enable_admin_rotation:
      description: "Automatic admin credentials rotation"
      type: bool
    item_custom_fields:
      description: "Additional custom fields to associate with the item"
      type: dict
    name:
      description: "Dynamic secret name"
      type: str
      required: true
    password_length:
      description: "The length of the password to be generated"
      type: str
    producer_encryption_key_name:
      description: "Dynamic producer encryption key"
      type: str

    region:
      description: "Region"
      type: str
      required: true
    secure_access_delay:
      description: "The delay duration, in seconds, to wait after generating just-in-time credentials. Accepted range: 0-120 seconds"
      type: int
    session_tags:
      description: "String of Key value session tags comma separated, relevant only for Assumed Role"
      type: str
    tags:
      description: "Add tags attached to this object"
      type: list
      elements: str
    target_name:
      description: "Target name"
      type: str
    transitive_tag_keys:
      description: "String of transitive tag keys space separated, relevant only for Assumed Role"
      type: str
    user_ttl:
      description: "User TTL"
      type: str
'''

EXAMPLES = r'''
- name: Create gateway_producer_aws
  gateway_producer_aws:
    state: present

- name: Delete gateway_producer_aws
  gateway_producer_aws:
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
    'access_mode': {'type': 'str'},
    'admin_rotation_interval_days': {'type': 'int'},
    'aws_access_key_id': {'type': 'str', 'required': True},
    'aws_access_secret_key': {'type': 'str', 'required': True, 'no_log': True},
    'aws_external_id': {'type': 'str'},
    'aws_role_arns': {'type': 'str'},
    'aws_user_console_access': {'type': 'bool'},
    'aws_user_groups': {'type': 'str'},
    'aws_user_policies': {'type': 'str', 'required': True},
    'aws_user_programmatic_access': {'type': 'bool'},
    'custom_username_template': {'type': 'str'},
    'delete_protection': {'type': 'str'},
    'enable_admin_rotation': {'type': 'bool'},
    'item_custom_fields': {'type': 'dict'},
    'name': {'type': 'str', 'required': True},
    'password_length': {'type': 'str', 'no_log': False},
    'producer_encryption_key_name': {'type': 'str'},
    'region': {'type': 'str', 'required': True},
    'secure_access_delay': {'type': 'int'},
    'session_tags': {'type': 'str'},
    'tags': {'type': 'list', 'elements': 'str'},
    'target_name': {'type': 'str'},
    'transitive_tag_keys': {'type': 'str', 'no_log': False},
    'user_ttl': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label='gateway_producer_aws',
        sdk_create=('GatewayCreateProducerAws', 'gateway_create_producer_aws'),
        sdk_update=('GatewayUpdateProducerAws', 'gateway_update_producer_aws'),
        sdk_delete=('GatewayDeleteProducer', 'gateway_delete_producer'),
        sdk_read=('GatewayGetProducer', 'gateway_get_producer'),
    )


if __name__ == '__main__':
    main()
