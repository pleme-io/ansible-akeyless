#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gateway_log_forwarding_elasticsearch
short_description: Manages the Elasticsearch log forwarding configuration on the gateway (singleton)
author:
  - "pleme-io (@pleme-io)"
extends_documentation_fragment:
  - drzln0.akeyless.auth
description:
  - Manage gateway_log_forwarding_elasticsearch resources.
options:
    state:
      description: Whether the resource should be present or absent.
      type: str
      choices: ["present", "absent"]
      default: present
    api_key:
      description: "Elasticsearch api key relevant only for api_key auth-type"
      type: str
    auth_type:
      description: "Elasticsearch auth type [api_key/password]"
      type: str
    cloud_id:
      description: "Elasticsearch cloud id relevant only for cloud server-type"
      type: str
    enable:
      description: "Enable Log Forwarding [true/false]"
      type: str
    enable_tls:
      description: "Enable tls"
      type: bool
    index:
      description: "Elasticsearch index"
      type: str
    nodes:
      description: "Elasticsearch nodes relevant only for nodes server-type"
      type: str
    output_format:
      description: "Logs format [text/json]"
      type: str
    pull_interval:
      description: "Pull interval in seconds"
      type: str
    server_type:
      description: "Elasticsearch server type [cloud/nodes]"
      type: str
    tls_certificate:
      description: "Elasticsearch tls certificate"
      type: str
    user_name:
      description: "Elasticsearch user name relevant only for password auth-type"
      type: str
'''

EXAMPLES = r'''
- name: Create gateway_log_forwarding_elasticsearch
  gateway_log_forwarding_elasticsearch:
    state: present

- name: Delete gateway_log_forwarding_elasticsearch
  gateway_log_forwarding_elasticsearch:
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
    'api_key': {'type': 'str'},
    'auth_type': {'type': 'str'},
    'cloud_id': {'type': 'str'},
    'enable': {'type': 'str'},
    'enable_tls': {'type': 'bool'},
    'index': {'type': 'str'},
    'nodes': {'type': 'str'},
    'output_format': {'type': 'str'},
    'pull_interval': {'type': 'str'},
    'server_type': {'type': 'str'},
    'tls_certificate': {'type': 'str'},
    'user_name': {'type': 'str'},
    'gateway_url': {'type': 'str'},
    'access_id': {'type': 'str'},
    'access_key': {'type': 'str', 'no_log': True},
    'access_type': {'type': 'str', 'default': 'access_key'},
}


def main():
    run_standard_crud(
        argument_spec=argument_spec,
        resource_label="gateway_log_forwarding_elasticsearch",
        sdk_create=("GatewayUpdateLogForwardingElasticsearch", "gateway_update_log_forwarding_elasticsearch"),
        sdk_update=("GatewayUpdateLogForwardingElasticsearch", "gateway_update_log_forwarding_elasticsearch"),
        sdk_delete=("GatewayUpdateLogForwardingElasticsearch", "gateway_update_log_forwarding_elasticsearch"),
        sdk_read=("GatewayGetLogForwarding", "gateway_get_log_forwarding"),
    )


if __name__ == '__main__':
    main()
