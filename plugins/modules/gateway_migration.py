#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_migration
short_description: Manages a gateway migration in Akeyless
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage gateway_migration resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    ServiceAccountKeyDecoded:
      description: ""
      type: str
    ad_auto_rotate:
      description: "Enable/Disable automatic/recurrent rotation for migrated secrets. Default is false: only manual rotation is allowed for migrated secrets. If set to true, this command should be combined with --ad-rotation-interval and --ad-rotation-hour parameters (Relevant only for Active Directory migration)"
      type: str
    ad_cert_expiration_event_in:
      description: "How many days before the expiration of discovered certificates would you like to be notified (Relevant only for Active Directory migration with certificate discovery enabled)"
      type: list
      elements: str
    ad_certificates_path_template:
      description: "Path location template for migrating certificates e.g.: /Certificates/{{COMMON_NAME}} (Relevant only for Active Directory migration with certificate discovery enabled)"
      type: str
    ad_computer_base_dn:
      description: "Distinguished Name of Computer objects (servers) to search in Active Directory e.g.: CN=Computers,DC=example,DC=com (Relevant only for Active Directory migration)"
      type: str
    ad_discover_iis_app:
      description: "Enable/Disable discovery of IIS application from each domain server as part of the SSH/Windows Rotated Secrets. Default is false. (Relevant only for Active Directory migration)"
      type: str
    ad_discover_services:
      description: "Enable/Disable discovery of Windows services from each domain server as part of the SSH/Windows Rotated Secrets. Default is false. (Relevant only for Active Directory migration)"
      type: str
    ad_discovery_types:
      description: "Set migration discovery types (domain-users, computers, local-users). (Relevant only for Active Directory migration)"
      type: list
      elements: str
    ad_domain_name:
      description: "Active Directory Domain Name (Relevant only for Active Directory migration)"
      type: str
    ad_domain_users_path_template:
      description: "Path location template for migrating domain users as Rotated Secrets e.g.: .../DomainUsers/{{USERNAME}} (Relevant only for Active Directory migration)"
      type: str
    ad_local_users_ignore:
      description: "Comma-separated list of Local Users which should not be migrated (Relevant only for Active Directory migration)"
      type: str
    ad_local_users_path_template:
      description: "Path location template for migrating domain users as Rotated Secrets e.g.: .../LocalUsers/{{COMPUTER_NAME}}/{{USERNAME}} (Relevant only for Active Directory migration)"
      type: str
    ad_os_filter:
      description: "Filter by Operating System to run the migration, can be used with wildcards, e.g. SRV20* (Relevant only for Active Directory migration)"
      type: str
    ad_rotation_hour:
      description: "The hour of the scheduled rotation in UTC (Relevant only for Active Directory migration)"
      type: int
    ad_rotation_interval:
      description: "The number of days to wait between every automatic rotation [1-365] (Relevant only for Active Directory migration)"
      type: int
    ad_sra_enable_rdp:
      description: "Enable/Disable RDP Secure Remote Access for the migrated local users rotated secrets. Default is false: rotated secrets will not be created with SRA (Relevant only for Active Directory migration)"
      type: str
    ad_ssh_port:
      description: "Set the SSH Port for further connection to the domain servers. Default is port 22 (Relevant only for Active Directory migration)"
      type: str
    ad_target_format:
      description: "Relevant only for ad-discovery-types=computers. For linked, all computers will be migrated into a linked target(s). if set with regular, the migration will create a target for each computer."
      type: str
    ad_target_name:
      description: "Active Directory LDAP Target Name. Server type should be Active Directory (Relevant only for Active Directory migration)"
      type: str
    ad_targets_path_template:
      description: "Path location template for migrating domain servers as SSH/Windows Targets e.g.: .../Servers/{{COMPUTER_NAME}} (Relevant only for Active Directory migration)"
      type: str
    ad_targets_type:
      description: "Set the target type of the domain servers [ssh/windows](Relevant only for Active Directory migration)"
      type: str
    ad_user_base_dn:
      description: "Distinguished Name of User objects to search in Active Directory, e.g.: CN=Users,DC=example,DC=com (Relevant only for Active Directory migration)"
      type: str
    ad_user_groups:
      description: "Comma-separated list of domain groups from which privileged domain users will be migrated. If empty, migrate all users based on the --ad-user-base-dn (Relevant only for Active Directory migration)"
      type: str
    ad_winrm_over_http:
      description: "Use WinRM over HTTP, by default runs over HTTPS"
      type: str
    ad_winrm_port:
      description: "Set the WinRM Port for further connection to the domain servers. Default is 5986 (Relevant only for Active Directory migration)"
      type: str
    ad_discover_local_users:
      description: "Enable/Disable discovery of local users from each domain server and migrate them as SSH/Windows Rotated Secrets. Default is false: only domain users will be migrated. Discovery of local users might require further installation of SSH on the servers, based on the supplied computer base DN. This will be implemented automatically as part of the migration process (Relevant only for Active Directory migration)
Deprecated: use AdDiscoverTypes"
      type: str
    ai_certificate_discovery:
      description: "Enable AI-assisted certificate discovery (only when AI Insight is enabled on the Gateway)"
      type: str
    aws_key:
      description: "AWS Secret Access Key (relevant only for AWS migration)"
      type: str
    aws_key_id:
      description: "AWS Access Key ID with sufficient permissions to get all secrets, e.g. 'arn:aws:secretsmanager:[Region]:[AccountId]:secret:[/path/to/secrets/*]' (relevant only for AWS migration)"
      type: str
    aws_region:
      description: "AWS region of the required Secrets Manager (relevant only for AWS migration)"
      type: str
    azure_client_id:
      description: "Azure Key Vault Access client ID, should be Azure AD App with a service principal (relevant only for Azure Key Vault migration)"
      type: str
    azure_kv_name:
      description: "Azure Key Vault Name (relevant only for Azure Key Vault migration)"
      type: str
    azure_secret:
      description: "Azure Key Vault secret (relevant only for Azure Key Vault migration)"
      type: str
    azure_tenant_id:
      description: "Azure Key Vault Access tenant ID (relevant only for Azure Key Vault migration)"
      type: str
    conjur_account:
      description: "Conjur account name set on your Conjur server (relevant only for Conjur migration)."
      type: str
    conjur_api_key:
      description: "Conjur API Key for the specified user (relevant only for Conjur migration)."
      type: str
    conjur_url:
      description: "Conjur server base URL (relevant only for Conjur migration).
If conjur-url is HTTPS and Conjur uses a private CA/self-signed certificate,
make the CA bundle available on the Gateway and set CONJUR_SSL_CERT_PATH to its path."
      type: str
    conjur_username:
      description: "Conjur username used to authenticate (relevant only for Conjur migration)."
      type: str
    delete_remote:
      description: "Delete the secret from the remote target as well, relevant only when usc-name is not empty (relevant only for HasiCorp Vault migration)"
      type: bool
    expiration_event_in:
      description: "How many days before the expiration of the certificate would you like to be notified."
      type: list
      elements: str
    gcp_key:
      description: "Base64-encoded GCP Service Account private key text with sufficient permissions to Secrets Manager, Minimum required permission is Secret Manager Secret Accessor, e.g. 'roles/secretmanager.secretAccessor' (relevant only for GCP migration)"
      type: str
    gcp_project_id:
      description: "GCP Project ID (cross-project override)"
      type: str
    hashi_json:
      description: "Import secret key as json value or independent secrets (relevant only for HasiCorp Vault migration) [true/false]"
      type: str
    hashi_ns:
      description: "HashiCorp Vault Namespaces is a comma-separated list of namespaces which need to be imported into Akeyless Vault. For every provided namespace, all its child namespaces are imported as well, e.g. nmsp/subnmsp1/subnmsp2,nmsp/anothernmsp. By default, import all namespaces (relevant only for HasiCorp Vault migration)"
      type: list
      elements: str
    hashi_token:
      description: "HashiCorp Vault access token with sufficient permissions to preform list & read operations on secrets objects (relevant only for HasiCorp Vault migration)"
      type: str
    hashi_url:
      description: "HashiCorp Vault API URL, e.g. https://vault-mgr01:8200 (relevant only for HasiCorp Vault migration)"
      type: str
    hosts:
      description: "A comma separated list of IPs, CIDR ranges, or DNS names to scan"
      type: str
      required: true
    k8s_ca_certificate:
      description: "For Certificate Authentication method
K8s Cluster CA certificate (relevant only for K8s migration with Certificate Authentication method)"
      type: list
      elements: int
    k8s_client_certificate:
      description: "K8s Client certificate with sufficient permission to list and get secrets in the namespace(s) you selected (relevant only for K8s migration with Certificate Authentication method)"
      type: list
      elements: int
    k8s_client_key:
      description: "K8s Client key (relevant only for K8s migration with Certificate Authentication method)"
      type: list
      elements: int
    k8s_namespace:
      description: "K8s Namespace, Use this field to import secrets from a particular namespace only. By default, the secrets are imported from all namespaces (relevant only for K8s migration)"
      type: str
    k8s_password:
      description: "K8s Client password (relevant only for K8s migration with Password Authentication method)"
      type: str
    k8s_skip_system:
      description: "K8s Skip Control Plane Secrets, This option allows to avoid importing secrets from system namespaces (relevant only for K8s migration)"
      type: bool
    k8s_token:
      description: "For Token Authentication method
K8s Bearer Token with sufficient permission to list and get secrets in the namespace(s) you selected (relevant only for K8s migration with Token Authentication method)"
      type: str
    k8s_url:
      description: "K8s API Server URL, e.g. https://k8s-api.mycompany.com:6443 (relevant only for K8s migration)"
      type: str
    k8s_username:
      description: "For Password Authentication method
K8s Client username with sufficient permission to list and get secrets in the namespace(s) you selected (relevant only for K8s migration with Password Authentication method)"
      type: str
    name:
      description: "Migration name"
      type: str
      required: true
    port_ranges:
      description: "A comma separated list of port ranges
Examples: '80,443' or '80,443,8080-8090' or '443'"
      type: str
    protection_key:
      description: "The name of the key that protects the classic key value (if empty, the account default key will be used)"
      type: str
    si_auto_rotate:
      description: "Enable/Disable automatic/recurrent rotation for migrated secrets. Default is false: only manual rotation is allowed for migrated secrets. If set to true, this command should be combined with --si-rotation-interval and --si-rotation-hour parameters (Relevant only for Server Inventory migration)"
      type: str
    si_rotation_hour:
      description: "The hour of the scheduled rotation in UTC (Relevant only for Server Inventory migration)"
      type: int
    si_rotation_interval:
      description: "The number of days to wait between every automatic rotation [1-365] (Relevant only for Server Inventory migration)"
      type: int
    si_sra_enable_rdp:
      description: "Enable/Disable RDP Secure Remote Access for the migrated local users rotated secrets. Default is false: rotated secrets will not be created with SRA (Relevant only for Server Inventory migration)"
      type: str
    si_target_name:
      description: "SSH, Windows or Linked Target Name. (Relevant only for Server Inventory migration)"
      type: str
      required: true
    si_user_groups:
      description: "Comma-separated list of groups to migrate users from. If empty, all users from all groups will be migrated (Relevant only for Server Inventory migration)"
      type: str
    si_users_ignore:
      description: "Comma-separated list of Local Users which should not be migrated (Relevant only for Server Inventory migration)"
      type: str
    si_users_path_template:
      description: "Path location template for migrating users as Rotated Secrets e.g.: .../Users/{{COMPUTER_NAME}}/{{USERNAME}} (Relevant only for Server Inventory migration)"
      type: str
      required: true
    target_location:
      description: "Target location in Akeyless for imported secrets"
      type: str
      required: true
    type:
      description: "Migration type (hashi/aws/gcp/k8s/azure_kv/conjur/active_directory/server_inventory/certificate)"
      type: str
    usc_name:
      description: "Universal Secret Connector name"
      type: str
    use_gw_cloud_identity:
      description: "Use the GW's Cloud IAM"
      type: bool
'''

EXAMPLES = r'''
- name: Create gateway_migration
  gateway_migration:
    state: present

- name: Delete gateway_migration
  gateway_migration:
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
    'ServiceAccountKeyDecoded': {'type': 'str'},
    'ad_auto_rotate': {'type': 'str'},
    'ad_cert_expiration_event_in': {'type': 'list', 'elements': 'str'},
    'ad_certificates_path_template': {'type': 'str'},
    'ad_computer_base_dn': {'type': 'str'},
    'ad_discover_iis_app': {'type': 'str'},
    'ad_discover_services': {'type': 'str'},
    'ad_discovery_types': {'type': 'list', 'elements': 'str'},
    'ad_domain_name': {'type': 'str'},
    'ad_domain_users_path_template': {'type': 'str'},
    'ad_local_users_ignore': {'type': 'str'},
    'ad_local_users_path_template': {'type': 'str'},
    'ad_os_filter': {'type': 'str'},
    'ad_rotation_hour': {'type': 'int'},
    'ad_rotation_interval': {'type': 'int'},
    'ad_sra_enable_rdp': {'type': 'str'},
    'ad_ssh_port': {'type': 'str'},
    'ad_target_format': {'type': 'str'},
    'ad_target_name': {'type': 'str'},
    'ad_targets_path_template': {'type': 'str'},
    'ad_targets_type': {'type': 'str'},
    'ad_user_base_dn': {'type': 'str'},
    'ad_user_groups': {'type': 'str'},
    'ad_winrm_over_http': {'type': 'str'},
    'ad_winrm_port': {'type': 'str'},
    'ad_discover_local_users': {'type': 'str'},
    'ai_certificate_discovery': {'type': 'str'},
    'aws_key': {'type': 'str'},
    'aws_key_id': {'type': 'str'},
    'aws_region': {'type': 'str'},
    'azure_client_id': {'type': 'str'},
    'azure_kv_name': {'type': 'str'},
    'azure_secret': {'type': 'str'},
    'azure_tenant_id': {'type': 'str'},
    'conjur_account': {'type': 'str'},
    'conjur_api_key': {'type': 'str'},
    'conjur_url': {'type': 'str'},
    'conjur_username': {'type': 'str'},
    'delete_remote': {'type': 'bool'},
    'expiration_event_in': {'type': 'list', 'elements': 'str'},
    'gcp_key': {'type': 'str'},
    'gcp_project_id': {'type': 'str'},
    'hashi_json': {'type': 'str'},
    'hashi_ns': {'type': 'list', 'elements': 'str'},
    'hashi_token': {'type': 'str'},
    'hashi_url': {'type': 'str'},
    'hosts': {'type': 'str', 'required': True},
    'k8s_ca_certificate': {'type': 'list', 'elements': 'int'},
    'k8s_client_certificate': {'type': 'list', 'elements': 'int'},
    'k8s_client_key': {'type': 'list', 'elements': 'int'},
    'k8s_namespace': {'type': 'str'},
    'k8s_password': {'type': 'str'},
    'k8s_skip_system': {'type': 'bool'},
    'k8s_token': {'type': 'str'},
    'k8s_url': {'type': 'str'},
    'k8s_username': {'type': 'str'},
    'name': {'type': 'str', 'required': True},
    'port_ranges': {'type': 'str'},
    'protection_key': {'type': 'str'},
    'si_auto_rotate': {'type': 'str'},
    'si_rotation_hour': {'type': 'int'},
    'si_rotation_interval': {'type': 'int'},
    'si_sra_enable_rdp': {'type': 'str'},
    'si_target_name': {'type': 'str', 'required': True},
    'si_user_groups': {'type': 'str'},
    'si_users_ignore': {'type': 'str'},
    'si_users_path_template': {'type': 'str', 'required': True},
    'target_location': {'type': 'str', 'required': True},
    'type': {'type': 'str'},
    'usc_name': {'type': 'str'},
    'use_gw_cloud_identity': {'type': 'bool'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="gateway_migration",
        sdk_create=("GatewayCreateMigration", "gateway_create_migration"),
        sdk_update=("GatewayUpdateMigration", "gateway_update_migration"),
        sdk_delete=("GatewayDeleteMigration", "gateway_delete_migration"),
        sdk_read=("GatewayGetMigration", "gateway_get_migration"),
    )


if __name__ == '__main__':
    main()
