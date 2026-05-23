# Copyright: (c) 2026, pleme-io
# MIT License
#
# Unit tests for plugins/inventory/akeyless.py -- the JSON-secret-
# backed inventory plugin.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import importlib.util
import json
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
INVENTORY_PATH = REPO_ROOT / "plugins" / "inventory" / "akeyless.py"


def _install_ansible_inventory_stubs():
    """Install minimal ansible.plugins.inventory stubs so the inventory
    plugin imports without a real Ansible install. The
    BaseInventoryPlugin + Constructable mixin we stub here cover
    the surface our InventoryModule actually uses (verify_file,
    _read_config_data, get_option, super().parse)."""
    if "ansible.plugins.inventory" in sys.modules:
        return

    ansible_pkg = sys.modules.setdefault("ansible", types.ModuleType("ansible"))
    errors_mod = types.ModuleType("ansible.errors")

    class _StubAnsibleError(Exception):
        pass

    errors_mod.AnsibleError = _StubAnsibleError
    sys.modules["ansible.errors"] = errors_mod
    ansible_pkg.errors = errors_mod

    plugins_mod = types.ModuleType("ansible.plugins")
    inv_mod = types.ModuleType("ansible.plugins.inventory")

    class _StubBaseInventoryPlugin:
        def __init__(self):
            self._opts: dict = {}

        def verify_file(self, path):
            return True  # always accept; subclasses filter further

        def _read_config_data(self, path):
            pass  # tests inject options via _opts directly

        def get_option(self, name):
            return self._opts.get(name)

        def parse(self, inventory, loader, path, *args, **kwargs):
            pass

    class _StubConstructable:
        pass

    inv_mod.BaseInventoryPlugin = _StubBaseInventoryPlugin
    inv_mod.Constructable = _StubConstructable
    sys.modules["ansible.plugins"] = plugins_mod
    sys.modules["ansible.plugins.inventory"] = inv_mod
    ansible_pkg.plugins = plugins_mod


def _load_inventory(fake_akeyless):
    _install_ansible_inventory_stubs()
    fake_mod, _ = fake_akeyless
    # Add GetSecretValue + Auth attributes that our code calls.
    fake_mod.GetSecretValue = MagicMock(name="akeyless.GetSecretValue")
    spec = importlib.util.spec_from_file_location(
        "akeyless_inventory_under_test", INVENTORY_PATH
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["akeyless_inventory_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def inventory(fake_akeyless):
    return _load_inventory(fake_akeyless)


def _stub_inventory_recorder():
    """A MagicMock-backed stand-in for an Ansible Inventory object
    that records add_host / add_group / set_variable calls so tests
    can assert on the resulting tree shape."""
    inv = MagicMock(name="Inventory")
    inv.hosts: dict = {}
    inv.groups: dict = {}
    inv.host_vars: dict = {}

    def add_host(name, group=None):
        inv.hosts.setdefault(name, set())
        if group:
            inv.hosts[name].add(group)
            inv.groups.setdefault(group, set()).add(name)

    def add_group(name):
        inv.groups.setdefault(name, set())

    def set_variable(entity, key, value):
        inv.host_vars.setdefault(entity, {})[key] = value

    inv.add_host.side_effect = add_host
    inv.add_group.side_effect = add_group
    inv.set_variable.side_effect = set_variable
    return inv


# ---------------------------------------------------------------------------
# verify_file
# ---------------------------------------------------------------------------


class TestVerifyFile:

    def test_accepts_inventory_akeyless_yml(self, inventory):
        """The plugin only fires on inventory files ending in
        akeyless.{yml,yaml} -- prevents accidental hijacking of
        other YAML inventories in the same directory."""
        plugin = inventory.InventoryModule()
        assert plugin.verify_file("/tmp/inventory.akeyless.yml")
        assert plugin.verify_file("/tmp/inventory.akeyless.yaml")
        assert plugin.verify_file("/tmp/akeyless.yml")
        assert plugin.verify_file("/tmp/akeyless.yaml")

    def test_rejects_unrelated_extension(self, inventory):
        plugin = inventory.InventoryModule()
        assert not plugin.verify_file("/tmp/inventory.yml")
        assert not plugin.verify_file("/tmp/something.json")


# ---------------------------------------------------------------------------
# _authenticate
# ---------------------------------------------------------------------------


class TestAuthenticate:

    def test_pre_issued_token_skips_auth(self, inventory):
        client, token = inventory._authenticate({"token": "pre-issued"})
        assert token == "pre-issued"
        assert not client.auth.called

    def test_requires_access_id_without_token(self, inventory):
        from ansible.errors import AnsibleError
        with pytest.raises(AnsibleError, match="access_id is required"):
            inventory._authenticate({"token": None, "access_id": None})

    def test_resolves_token_via_auth_path(self, inventory):
        fake_client = MagicMock(name="V2Api()")
        fake_client.auth.return_value = MagicMock(token="resolved-token")
        inventory.akeyless.V2Api = MagicMock(return_value=fake_client)
        _, token = inventory._authenticate({
            "access_id": "p-xxx", "access_key": "secret",
        })
        assert token == "resolved-token"


# ---------------------------------------------------------------------------
# _merge_inventory_tree
# ---------------------------------------------------------------------------


class TestMergeInventoryTree:

    def test_adds_hosts_with_vars(self, inventory):
        inv = _stub_inventory_recorder()
        payload = {
            "hosts": {
                "web1": {"ansible_host": "10.0.0.1", "role": "web"},
                "web2": {"ansible_host": "10.0.0.2"},
            },
        }
        inventory._merge_inventory_tree(inv, payload, source_label="test")
        assert "web1" in inv.hosts
        assert "web2" in inv.hosts
        assert inv.host_vars["web1"] == {"ansible_host": "10.0.0.1", "role": "web"}
        assert inv.host_vars["web2"] == {"ansible_host": "10.0.0.2"}

    def test_adds_groups_with_membership_and_vars(self, inventory):
        inv = _stub_inventory_recorder()
        payload = {
            "groups": {
                "web": {"hosts": ["web1", "web2"], "vars": {"role": "web"}},
                "prod": {"hosts": ["web1"]},
            },
        }
        inventory._merge_inventory_tree(inv, payload, source_label="test")
        assert "web" in inv.groups
        assert inv.groups["web"] == {"web1", "web2"}
        assert inv.groups["prod"] == {"web1"}
        assert inv.host_vars["web"] == {"role": "web"}

    def test_unknown_top_level_keys_ignored(self, inventory):
        """Forward-compat: payload may add new top-level keys (children,
        meta, etc.) that this version doesn't know about. They must
        not crash the parse."""
        inv = _stub_inventory_recorder()
        payload = {
            "hosts": {"x": {}},
            "future_field": {"opaque": True},
        }
        inventory._merge_inventory_tree(inv, payload, source_label="test")
        assert "x" in inv.hosts

    def test_empty_payload_is_a_no_op(self, inventory):
        inv = _stub_inventory_recorder()
        inventory._merge_inventory_tree(inv, {}, source_label="test")
        assert inv.hosts == {}
        assert inv.groups == {}


# ---------------------------------------------------------------------------
# _fetch_secret
# ---------------------------------------------------------------------------


class TestFetchSecret:

    def test_parses_json_value(self, inventory):
        fake_client = MagicMock(name="V2Api()")
        response = MagicMock()
        response.to_dict.return_value = {"/sec": json.dumps({"hosts": {"a": {}}})}
        fake_client.get_secret_value.return_value = response

        out = inventory._fetch_secret(fake_client, "tok", "/sec")
        assert out == {"hosts": {"a": {}}}

    def test_raises_on_non_json_value(self, inventory):
        from ansible.errors import AnsibleError
        fake_client = MagicMock()
        response = MagicMock()
        response.to_dict.return_value = {"/sec": "not-json"}
        fake_client.get_secret_value.return_value = response

        with pytest.raises(AnsibleError, match="not valid JSON"):
            inventory._fetch_secret(fake_client, "tok", "/sec")

    def test_raises_when_secret_missing_from_response(self, inventory):
        from ansible.errors import AnsibleError
        fake_client = MagicMock()
        response = MagicMock()
        response.to_dict.return_value = {"/other": "v"}
        fake_client.get_secret_value.return_value = response

        with pytest.raises(AnsibleError, match="missing secret"):
            inventory._fetch_secret(fake_client, "tok", "/sec")


# ---------------------------------------------------------------------------
# InventoryModule.parse end-to-end
# ---------------------------------------------------------------------------


class TestParseEndToEnd:

    def test_parse_requires_secrets_option(self, inventory):
        from ansible.errors import AnsibleError
        plugin = inventory.InventoryModule()
        plugin._opts = {"secrets": []}  # empty list
        with pytest.raises(AnsibleError, match="`secrets` is required"):
            plugin.parse(_stub_inventory_recorder(), MagicMock(), "/tmp/x.akeyless.yml")

    def test_parse_merges_resolved_secret_into_inventory(self, inventory):
        """End-to-end: configure the plugin with one secret path,
        stub the SDK auth + get_secret_value to return inventory JSON,
        and assert the plugin populated the inventory recorder."""
        # Wire the SDK stubs.
        fake_client = MagicMock(name="V2Api()")
        fake_client.auth.return_value = MagicMock(token="tok")
        response = MagicMock()
        response.to_dict.return_value = {
            "/inv": json.dumps({
                "hosts": {"db1": {"role": "db"}},
                "groups": {"data": {"hosts": ["db1"]}},
            })
        }
        fake_client.get_secret_value.return_value = response
        inventory.akeyless.V2Api = MagicMock(return_value=fake_client)

        plugin = inventory.InventoryModule()
        plugin._opts = {
            "secrets": ["/inv"],
            "access_id": "p-xxx",
            "access_key": "secret",
            "access_type": "access_key",
            "gateway_url": "https://example/",
            "token": None,
        }
        inv = _stub_inventory_recorder()
        plugin.parse(inv, MagicMock(), "/tmp/x.akeyless.yml")
        assert "db1" in inv.hosts
        assert inv.host_vars["db1"] == {"role": "db"}
        assert inv.groups["data"] == {"db1"}
