#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: target_db
short_description: Manages a database target in Akeyless Vault
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
      no_log: true
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
      no_log: true
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
      no_log: true
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
      no_log: true
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


def create_resource(module):
    """Create the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="target_db created")
    except Exception as e:
        module.fail_json(msg="Failed to create target_db: %s" % str(e))


def update_resource(module):
    """Update the resource."""
    # WARNING: The following fields are immutable after creation.
    #   - name
    # Changing them requires destroy + recreate.

    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="target_db updated")
    except Exception as e:
        module.fail_json(msg="Failed to update target_db: %s" % str(e))


def delete_resource(module):
    """Delete the resource."""
    try:
        # TODO: implement API call
        module.exit_json(changed=True, msg="target_db deleted")
    except Exception as e:
        module.fail_json(msg="Failed to delete target_db: %s" % str(e))


def read_resource(module):
    """Read the current state of the resource."""
    try:
        # TODO: implement API call
        return None
    except Exception as e:
        module.fail_json(msg="Failed to read target_db: %s" % str(e))


def main():
    argument_spec = {
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'azure_client_id': {'type': 'str'},
        'azure_client_secret': {'type': 'str'},
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
        'key': {'type': 'str'},
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
        'snowflake_api_private_key': {'type': 'str'},
        'snowflake_api_private_key_password': {'type': 'str'},
        'ssl': {'type': 'bool'},
        'ssl_certificate': {'type': 'str', 'no_log': True},
        'user_name': {'type': 'str'},
    }

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    state = module.params.get('state', 'present')
    current = read_resource(module)

    if module.check_mode:
        module.exit_json(changed=(current is None and state == 'present')
                         or (current is not None and state == 'absent'))

    if state == 'absent':
        if current is not None:
            delete_resource(module)
        else:
            module.exit_json(changed=False, msg="target_db already absent")
    else:
        if current is None:
            create_resource(module)
        else:
            update_resource(module)


if __name__ == '__main__':
    main()
