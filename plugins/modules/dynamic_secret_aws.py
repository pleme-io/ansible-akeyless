#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: dynamic_secret_aws
short_description: Manages an AWS dynamic secret producer
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage dynamic_secret_aws resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    access_mode:
      description: "AWS access mode: iam_user or assume_role"
      type: str
    admin_rotation_interval_days:
      description: "Admin credentials rotation interval in days"
      type: int
    aws_access_key_id:
      description: "AWS access key ID for the producer"
      type: str
    aws_access_secret_key:
      description: "AWS secret access key for the producer"
      type: str
    aws_external_id:
      description: "The AWS External ID associated with the AWS role (relevant only for assume_role mode)"
      type: str
    aws_role_arns:
      description: "AWS role ARNs to assume (comma-separated)"
      type: str
    aws_user_console_access:
      description: "Enable AWS console access for dynamic users"
      type: bool
    aws_user_groups:
      description: "AWS IAM groups for dynamic users"
      type: str
    aws_user_policies:
      description: "AWS IAM policies for dynamic users"
      type: str
    aws_user_programmatic_access:
      description: "Enable programmatic access for dynamic users"
      type: bool
    custom_username_template:
      description: "Customize how temporary usernames are generated using go template"
      type: str
    delete_protection:
      description: "Enable delete protection"
      type: bool
    description:
      description: "Description of the object"
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
      description: "AWS region"
      type: str
    secure_access_delay:
      description: "The delay duration, in seconds, to wait after generating just-in-time credentials. Accepted range: 0-120 seconds"
      type: int
    session_tags:
      description: "String of Key value session tags comma separated, relevant only for Assumed Role"
      type: str
    tags:
      description: "Tags for the producer"
      type: list
      elements: str
    target_name:
      description: "Target name associated with this producer"
      type: str
    transitive_tag_keys:
      description: "String of transitive tag keys space separated, relevant only for Assumed Role"
      type: str
    user_ttl:
      description: "User TTL (e.g., 60m, 12h)"
      type: str
'''

EXAMPLES = r'''
- name: Create dynamic_secret_aws
  dynamic_secret_aws:
    state: present

- name: Delete dynamic_secret_aws
  dynamic_secret_aws:
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
    'aws_access_key_id': {'type': 'str', 'no_log': True},
    'aws_access_secret_key': {'type': 'str', 'no_log': True},
    'aws_external_id': {'type': 'str'},
    'aws_role_arns': {'type': 'str'},
    'aws_user_console_access': {'type': 'bool'},
    'aws_user_groups': {'type': 'str'},
    'aws_user_policies': {'type': 'str'},
    'aws_user_programmatic_access': {'type': 'bool'},
    'custom_username_template': {'type': 'str'},
    'delete_protection': {'type': 'bool'},
    'description': {'type': 'str'},
    'enable_admin_rotation': {'type': 'bool'},
    'item_custom_fields': {'type': 'dict'},
    'name': {'type': 'str', 'required': True},
    'password_length': {'type': 'str'},
    'producer_encryption_key_name': {'type': 'str'},
    'region': {'type': 'str'},
    'secure_access_delay': {'type': 'int'},
    'session_tags': {'type': 'str'},
    'tags': {'type': 'list', 'elements': 'str'},
    'target_name': {'type': 'str'},
    'transitive_tag_keys': {'type': 'str'},
    'user_ttl': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="dynamic_secret_aws",
        sdk_create=("DynamicSecretCreateAws", "dynamic_secret_create_aws"),
        sdk_update=("DynamicSecretUpdateAws", "dynamic_secret_update_aws"),
        sdk_delete=("DynamicSecretDelete", "dynamic_secret_delete"),
        sdk_read=("DynamicSecretGet", "dynamic_secret_get"),
    )


if __name__ == '__main__':
    main()
