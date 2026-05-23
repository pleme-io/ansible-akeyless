#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: target_gke
short_description: Manages a Google GKE target in Akeyless Vault
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage target_gke resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    description:
      description: "Target description"
      type: str
    gke_account_key:
      description: "GCP service account key JSON (base64)"
      type: str
    gke_cluster_cert:
      description: "GKE cluster CA certificate (PEM)"
      type: str
    gke_cluster_endpoint:
      description: "GKE cluster API server URL"
      type: str
    gke_cluster_name:
      description: "GKE cluster name"
      type: str
    gke_service_account_email:
      description: "GCP service account email"
      type: str
    key:
      description: "The name of a key that used to encrypt the target secret value (if empty, the account default protectionKey key will be used)"
      type: str
    max_versions:
      description: "Set the maximum number of versions, limited by the account settings defaults."
      type: str
    name:
      description: "Target name"
      type: str
      required: true
    use_gw_cloud_identity:
      description: "Use gateway cloud identity for authentication"
      type: bool
'''

EXAMPLES = r'''
- name: Create target_gke
  target_gke:
    state: present

- name: Delete target_gke
  target_gke:
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
    'description': {'type': 'str'},
    'gke_account_key': {'type': 'str', 'no_log': True},
    'gke_cluster_cert': {'type': 'str', 'no_log': True},
    'gke_cluster_endpoint': {'type': 'str'},
    'gke_cluster_name': {'type': 'str'},
    'gke_service_account_email': {'type': 'str'},
    'key': {'type': 'str'},
    'max_versions': {'type': 'str'},
    'name': {'type': 'str', 'required': True},
    'use_gw_cloud_identity': {'type': 'bool'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="target_gke",
        sdk_create=("TargetCreateGke", "target_create_gke"),
        sdk_update=("TargetUpdateGke", "target_update_gke"),
        sdk_delete=("TargetDelete", "target_delete"),
        sdk_read=("TargetGet", "target_get"),
    )


if __name__ == '__main__':
    main()
