#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_log_forwarding_aws_s3
short_description: Manages the AWS S3 log forwarding configuration on the gateway (singleton)
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage gateway_log_forwarding_aws_s3 resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    access_id:
      description: "AWS access id relevant for access_key auth-type"
      type: str
    access_key:
      description: "AWS access key relevant for access_key auth-type"
      type: str
    auth_type:
      description: "AWS auth type [access_key/cloud_id/assume_role]"
      type: str
    bucket_name:
      description: "AWS S3 bucket name"
      type: str
    enable:
      description: "Enable Log Forwarding [true/false]"
      type: str
    log_folder:
      description: "AWS S3 destination folder for logs"
      type: str
    output_format:
      description: "Logs format [text/json]"
      type: str
    pull_interval:
      description: "Pull interval in seconds"
      type: str
    region:
      description: "AWS region"
      type: str
    role_arn:
      description: "AWS role arn relevant for assume_role auth-type"
      type: str
'''

EXAMPLES = r'''
- name: Create gateway_log_forwarding_aws_s3
  gateway_log_forwarding_aws_s3:
    state: present

- name: Delete gateway_log_forwarding_aws_s3
  gateway_log_forwarding_aws_s3:
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
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str'},
    'auth_type': {'type': 'str'},
    'bucket_name': {'type': 'str'},
    'enable': {'type': 'str'},
    'log_folder': {'type': 'str'},
    'output_format': {'type': 'str'},
    'pull_interval': {'type': 'str'},
    'region': {'type': 'str'},
    'role_arn': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label='gateway_log_forwarding_aws_s3',
        sdk_create=('GatewayUpdateLogForwardingAwsS3', 'gateway_update_log_forwarding_aws_s3'),
        sdk_update=('GatewayUpdateLogForwardingAwsS3', 'gateway_update_log_forwarding_aws_s3'),
        sdk_delete=('GatewayUpdateLogForwardingAwsS3', 'gateway_update_log_forwarding_aws_s3'),
        sdk_read=('GatewayGetLogForwarding', 'gateway_get_log_forwarding'),
    )


if __name__ == '__main__':
    main()
