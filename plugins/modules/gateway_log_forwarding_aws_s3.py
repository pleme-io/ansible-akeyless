#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_log_forwarding_aws_s3
short_description: Manages the AWS S3 log forwarding configuration on the gateway (singleton)
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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client import (
    get_client, call_api, build_body, compute_diff, drift_to_diff,
    IDEMPOTENCY_IGNORE_KEYS,
)


def create_resource(module, client, token):
    """Create the resource."""
    body = build_body("GatewayUpdateLogForwardingAwsS3", dict(module.params, token=token))
    return call_api(module, client, "gateway_update_log_forwarding_aws_s3", body)


def update_resource(module, client, token):
    """Update the resource."""
    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("GatewayUpdateLogForwardingAwsS3", dict(module.params, token=token))
    return call_api(module, client, "gateway_update_log_forwarding_aws_s3", body)


def delete_resource(module, client, token):
    """Delete the resource."""
    body = build_body("GatewayUpdateLogForwardingAwsS3", dict(module.params, token=token))
    return call_api(module, client, "gateway_update_log_forwarding_aws_s3", body)


def read_resource(module, client, token):
    """Read the current state of the resource. Returns None if absent."""
    body = build_body("GatewayGetLogForwarding", {"name": module.params.get("name"), "token": token})
    return call_api(module, client, "gateway_get_log_forwarding", body, swallow_404=True)


def main():
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

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    client, token = get_client(module)
    state = module.params.get('state', 'present')
    current = read_resource(module, client, token)

    if state == 'absent':
        if current is None:
            module.exit_json(changed=False, msg="gateway_log_forwarding_aws_s3 already absent")
        if module.check_mode:
            module.exit_json(changed=True)
        result = delete_resource(module, client, token)
        module.exit_json(changed=True, result=result)

    # state == 'present'
    if current is None:
        if module.check_mode:
            module.exit_json(changed=True)
        result = create_resource(module, client, token)
        module.exit_json(changed=True, result=result)

    # Resource exists -- only update if any desired field differs
    # from what's in the SDK Get response. Honest convergence:
    # no drift => no API call => changed=False.
    drift = compute_diff(current, module.params, IDEMPOTENCY_IGNORE_KEYS)
    if not drift:
        module.exit_json(changed=False, msg="gateway_log_forwarding_aws_s3 already in desired state")
    diff = drift_to_diff(drift)
    if module.check_mode:
        module.exit_json(changed=True, diff=diff)
    result = update_resource(module, client, token)
    module.exit_json(changed=True, result=result, diff=diff)


if __name__ == '__main__':
    main()
