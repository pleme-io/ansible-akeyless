#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: target_db
short_description: Manages a database target in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage target_db resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    azure_client_id:
      description: "(Optional) Client id (relevant for 'cloud-service-provider' only)"
      type: str
    azure_client_secret:
      description: "(Optional) Client secret (relevant for 'cloud-service-provider' only)"
      type: str
    azure_tenant_id:
      description: "(Optional) Tenant id (relevant for 'cloud-service-provider' only)"
      type: str
    cloud_service_provider:
      description: "(Optional) Cloud service provider (currently only supports Azure)"
      type: str
    cluster_mode:
      description: "Cluster Mode"
      type: bool
    comment:
      description: "Deprecated - use description"
      type: str
    connection_type:
      description: "Type of connection to mssql database [credentials/cloud-identity/wallet/parent-target]"
      type: str
      required: true
    db_name:
      description: "Database name"
      type: str
    db_server_certificates:
      description: "Database server TLS certificates (PEM)"
      type: str
    db_server_name:
      description: "Database server name for TLS verification"
      type: str
    db_type:
      description: "Database type: mysql, mssql, postgresql, mongodb, snowflake, oracle, cassandra, redshift, hanadb"
      type: str
      required: true
    description:
      description: "Target description"
      type: str
    host:
      description: "Database hostname"
      type: str
    key:
      description: "The name of a key that used to encrypt the target secret value (if empty, the account default protectionKey key will be used)"
      type: str
    max_versions:
      description: "Set the maximum number of versions, limited by the account settings defaults."
      type: str
    mongodb_atlas:
      description: "Use MongoDB Atlas connection"
      type: bool
    mongodb_atlas_api_private_key:
      description: "MongoDB Atlas API private key"
      type: str
    mongodb_atlas_api_public_key:
      description: "MongoDB Atlas API public key"
      type: str
    mongodb_atlas_project_id:
      description: "MongoDB Atlas project ID"
      type: str
    mongodb_default_auth_db:
      description: "MongoDB default authentication database"
      type: str
    mongodb_uri_options:
      description: "MongoDB additional URI options"
      type: str
    name:
      description: "Target name"
      type: str
      required: true
    oracle_service_name:
      description: "Oracle service name"
      type: str
    oracle_wallet_login_type:
      description: "Oracle Wallet login type (password/mtls)"
      type: str
    oracle_wallet_p12_file_data:
      description: "Oracle wallet p12 file data in base64"
      type: str
    oracle_wallet_sso_file_data:
      description: "Oracle wallet sso file data in base64"
      type: str
    parent_target_name:
      description: "Name of the parent target, relevant only when connection-type is parent-target"
      type: str
    port:
      description: "Database port"
      type: str
    pwd:
      description: "Database password"
      type: str
    snowflake_account:
      description: "Snowflake account identifier"
      type: str
    snowflake_api_private_key:
      description: "RSA Private key (base64 encoded)"
      type: str
    snowflake_api_private_key_password:
      description: "The Private key passphrase"
      type: str
    ssl:
      description: "Enable SSL connection"
      type: bool
    ssl_certificate:
      description: "Client SSL certificate (PEM)"
      type: str
    user_name:
      description: "Database username"
      type: str
'''

EXAMPLES = r'''
- name: Create target_db
  target_db:
    state: present

- name: Delete target_db
  target_db:
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
    body = build_body("TargetCreateDB", dict(module.params, token=token))
    return call_api(module, client, "target_create_db", body)


def update_resource(module, client, token):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    # TODO(phase-1b): use read_mapping for honest diff
    body = build_body("TargetUpdateDB", dict(module.params, token=token))
    return call_api(module, client, "target_update_db", body)


def delete_resource(module, client, token):
    """Delete the resource."""
    body = build_body("TargetDelete", dict(module.params, token=token))
    return call_api(module, client, "target_delete", body)


def read_resource(module, client, token):
    """Read the current state of the resource. Returns None if absent."""
    body = build_body("TargetGet", {"name": module.params.get("name"), "token": token})
    return call_api(module, client, "target_get", body, swallow_404=True)


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'azure_client_id': {'type': 'str'},
        'azure_client_secret': {'type': 'str', 'no_log': True},
        'azure_tenant_id': {'type': 'str'},
        'cloud_service_provider': {'type': 'str'},
        'cluster_mode': {'type': 'bool'},
        'comment': {'type': 'str'},
        'connection_type': {'type': 'str', 'required': True},
        'db_name': {'type': 'str'},
        'db_server_certificates': {'type': 'str', 'no_log': True},
        'db_server_name': {'type': 'str'},
        'db_type': {'type': 'str', 'required': True},
        'description': {'type': 'str'},
        'host': {'type': 'str'},
        'key': {'type': 'str', 'no_log': False},
        'max_versions': {'type': 'str'},
        'mongodb_atlas': {'type': 'bool'},
        'mongodb_atlas_api_private_key': {'type': 'str', 'no_log': True},
        'mongodb_atlas_api_public_key': {'type': 'str'},
        'mongodb_atlas_project_id': {'type': 'str'},
        'mongodb_default_auth_db': {'type': 'str'},
        'mongodb_uri_options': {'type': 'str'},
        'name': {'type': 'str', 'required': True},
        'oracle_service_name': {'type': 'str'},
        'oracle_wallet_login_type': {'type': 'str'},
        'oracle_wallet_p12_file_data': {'type': 'str'},
        'oracle_wallet_sso_file_data': {'type': 'str'},
        'parent_target_name': {'type': 'str'},
        'port': {'type': 'str'},
        'pwd': {'type': 'str', 'no_log': True},
        'snowflake_account': {'type': 'str'},
        'snowflake_api_private_key': {'type': 'str', 'no_log': True},
        'snowflake_api_private_key_password': {'type': 'str', 'no_log': True},
        'ssl': {'type': 'bool'},
        'ssl_certificate': {'type': 'str', 'no_log': True},
        'user_name': {'type': 'str'},
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
            module.exit_json(changed=False, msg="target_db already absent")
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
        module.exit_json(changed=False, msg="target_db already in desired state")
    diff = drift_to_diff(drift)
    if module.check_mode:
        module.exit_json(changed=True, diff=diff)
    result = update_resource(module, client, token)
    module.exit_json(changed=True, result=result, diff=diff)


if __name__ == '__main__':
    main()
