# Copyright: (c) 2026, pleme-io
# MIT License
#
# Hypothesis property tests for plugins/inventory/akeyless.py.
# Complements test_akeyless_inventory.py (fixed cases) with random
# JSON-secret payload shapes. The inventory plugin merges arbitrary
# user-provided JSON into Ansible's inventory tree, so robustness
# against malformed shapes matters.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import importlib.util
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

REPO_ROOT = Path(__file__).resolve().parents[4]
INVENTORY_PATH = REPO_ROOT / "plugins" / "inventory" / "akeyless.py"


def _install_inventory_stubs():
    """Idempotent stubs for ansible.errors + ansible.plugins.inventory
    + the lookup_auth + plugin_helpers helpers."""
    ansible_pkg = sys.modules.setdefault("ansible", types.ModuleType("ansible"))
    errors_mod = sys.modules.get("ansible.errors")
    if errors_mod is None:
        errors_mod = types.ModuleType("ansible.errors")
        sys.modules["ansible.errors"] = errors_mod
        ansible_pkg.errors = errors_mod
    if not hasattr(errors_mod, "AnsibleError"):
        class _StubAnsibleError(Exception):
            pass
        errors_mod.AnsibleError = _StubAnsibleError

    if "ansible.plugins.inventory" not in sys.modules:
        plugins_mod = types.ModuleType("ansible.plugins")
        inv_mod = types.ModuleType("ansible.plugins.inventory")

        class _BaseInventoryPlugin:
            def __init__(self): self._opts = {}
            def verify_file(self, path): return True
            def _read_config_data(self, path): pass
            def get_option(self, name): return self._opts.get(name)
            def parse(self, *args, **kwargs): pass

        class _Constructable: pass

        inv_mod.BaseInventoryPlugin = _BaseInventoryPlugin
        inv_mod.Constructable = _Constructable
        sys.modules["ansible.plugins"] = plugins_mod
        sys.modules["ansible.plugins.inventory"] = inv_mod
        ansible_pkg.plugins = plugins_mod

    # Helpers (lookup_auth + plugin_helpers) under their canonical FQ names.
    for name in (
        "ansible_collections",
        "ansible_collections.drzln0",
        "ansible_collections.drzln0.akeyless",
        "ansible_collections.drzln0.akeyless.plugins",
        "ansible_collections.drzln0.akeyless.plugins.module_utils",
    ):
        sys.modules.setdefault(name, types.ModuleType(name))
    for stem in ("akeyless_lookup_auth", "akeyless_plugin_helpers"):
        full = (
            f"ansible_collections.drzln0.akeyless.plugins.module_utils.{stem}"
        )
        sys.modules.pop(full, None)
        helper_path = REPO_ROOT / "plugins" / "module_utils" / f"{stem}.py"
        spec = importlib.util.spec_from_file_location(full, helper_path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[full] = mod
        spec.loader.exec_module(mod)


@pytest.fixture
def inventory_mod(fake_akeyless):
    """Function-scoped so it picks up the (function-scoped)
    fake_akeyless fixture cleanly. The setup overhead is small."""
    _install_inventory_stubs()
    fake_akeyless[0].GetSecretValue = MagicMock(name="akeyless.GetSecretValue")
    spec = importlib.util.spec_from_file_location(
        "akeyless_inventory_props_under_test", INVENTORY_PATH
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


class _FakeInventory:
    """Minimal inventory recorder that mimics the BaseInventoryPlugin
    interface used by _merge_inventory_tree. Captures the sequence of
    calls so tests can assert on the merged result.

    Important: Ansible's real Inventory namespaces hosts and groups
    separately -- a host named "demo" and a group named "demo" can
    coexist. To mirror that here we track WHICH namespace a target
    was most-recently added to (`_last_added_as`) and route
    set_variable() to that namespace. Without this distinction, a
    payload like {hosts: {0: {}}, groups: {0: {vars: {0: None}}}}
    silently routes group-var writes to the host's var dict and the
    idempotency property test catches the discrepancy on the second
    merge pass."""

    def __init__(self):
        self.hosts = {}        # host_name -> {var: value}
        self.groups = {}       # group_name -> {hosts: [...], vars: {}}
        self._last_added_as = {}  # name -> "host" | "group"
        self._all_calls = []

    def add_host(self, name, group=None):
        self._all_calls.append(("add_host", name, group))
        self.hosts.setdefault(name, {})
        self._last_added_as[name] = "host"
        if group is not None:
            self.groups.setdefault(group, {"hosts": [], "vars": {}})
            self._last_added_as[group] = "group"
            if name not in self.groups[group]["hosts"]:
                self.groups[group]["hosts"].append(name)

    def add_group(self, name):
        self._all_calls.append(("add_group", name))
        self.groups.setdefault(name, {"hosts": [], "vars": {}})
        self._last_added_as[name] = "group"

    def set_variable(self, target, key, value):
        self._all_calls.append(("set_variable", target, key, value))
        ns = self._last_added_as.get(target)
        if ns == "group" and target in self.groups:
            self.groups[target]["vars"][key] = value
        elif ns == "host" and target in self.hosts:
            self.hosts[target][key] = value
        elif target in self.hosts:
            self.hosts[target][key] = value
        elif target in self.groups:
            self.groups[target]["vars"][key] = value


_PROP_SETTINGS = dict(
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)


# Strategies for inventory-shaped payloads.
_host_name = st.text(
    alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"),
                            whitelist_characters="-_."),
    min_size=1, max_size=20,
)
_group_name = st.text(
    alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"),
                            whitelist_characters="_"),
    min_size=1, max_size=15,
)
_var_value = st.one_of(
    st.text(max_size=30), st.integers(), st.booleans(), st.none(),
)
_host_vars = st.dictionaries(
    st.text(min_size=1, max_size=15, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"))),
    _var_value, max_size=5,
)
_payload_hosts = st.dictionaries(_host_name, _host_vars, max_size=5)
_payload_groups = st.dictionaries(
    _group_name,
    st.fixed_dictionaries({
        "hosts": st.lists(_host_name, max_size=5),
        "vars": _host_vars,
    }),
    max_size=4,
)
_payload = st.fixed_dictionaries({
    "hosts": _payload_hosts,
    "groups": _payload_groups,
})


# ---------------------------------------------------------------------------
# _merge_inventory_tree properties
# ---------------------------------------------------------------------------


class TestMergeInventoryTreeProperties:

    @given(payload=_payload)
    @settings(max_examples=200, **_PROP_SETTINGS)
    def test_every_payload_host_added_to_inventory(self, inventory_mod, payload):
        """For any valid payload, every host in payload['hosts'] must
        end up in inventory.hosts after merge."""
        inv = _FakeInventory()
        inventory_mod._merge_inventory_tree(inv, payload, source_label="t")
        for name in payload["hosts"]:
            assert name in inv.hosts, f"host {name!r} missing from merged inventory"

    @given(payload=_payload)
    @settings(max_examples=200, **_PROP_SETTINGS)
    def test_every_payload_group_added(self, inventory_mod, payload):
        """Same for groups: every group in payload['groups'] must appear."""
        inv = _FakeInventory()
        inventory_mod._merge_inventory_tree(inv, payload, source_label="t")
        for name in payload["groups"]:
            assert name in inv.groups, f"group {name!r} missing"

    @given(payload=_payload)
    @settings(max_examples=100, **_PROP_SETTINGS)
    def test_host_vars_preserved_after_merge(self, inventory_mod, payload):
        """Each host's vars dict must be set verbatim on the inventory."""
        inv = _FakeInventory()
        inventory_mod._merge_inventory_tree(inv, payload, source_label="t")
        for name, vars_dict in payload["hosts"].items():
            for k, v in vars_dict.items():
                assert inv.hosts[name].get(k) == v, (
                    f"host {name!r} var {k!r}: expected {v!r}, got {inv.hosts[name].get(k)!r}"
                )

    @given(payload=_payload)
    @settings(max_examples=100, **_PROP_SETTINGS)
    def test_group_membership_recorded(self, inventory_mod, payload):
        """Hosts listed in a group's `hosts:` list must appear in
        inventory.groups[group]['hosts']."""
        inv = _FakeInventory()
        inventory_mod._merge_inventory_tree(inv, payload, source_label="t")
        for group, body in payload["groups"].items():
            for host in body.get("hosts") or []:
                assert host in inv.groups[group]["hosts"], (
                    f"host {host!r} should be in group {group!r}"
                )

    @given(payload=_payload)
    @settings(max_examples=100, **_PROP_SETTINGS)
    def test_merge_is_idempotent(self, inventory_mod, payload):
        """Applying _merge_inventory_tree twice produces the same
        inventory state as applying it once. (Important: if an
        inventory source is somehow processed twice, no duplicates
        or corruption.)"""
        a = _FakeInventory()
        b = _FakeInventory()
        inventory_mod._merge_inventory_tree(a, payload, source_label="t")
        inventory_mod._merge_inventory_tree(b, payload, source_label="t")
        inventory_mod._merge_inventory_tree(b, payload, source_label="t")
        assert a.hosts == b.hosts
        assert a.groups == b.groups

    @given(extra=st.dictionaries(
        st.text(min_size=1, max_size=10).filter(
            lambda s: s not in ("hosts", "groups")
        ),
        st.text(max_size=20),
        max_size=3,
    ))
    @settings(max_examples=50, **_PROP_SETTINGS)
    def test_unknown_top_level_keys_silently_ignored(self, inventory_mod, extra):
        """Forward-compat: payloads with keys we don't know about
        (e.g. a future `meta:` or `cache_ttl:` key) must not crash
        the inventory build."""
        payload = {"hosts": {}, "groups": {}}
        payload.update(extra)
        inv = _FakeInventory()
        # Must not raise.
        inventory_mod._merge_inventory_tree(inv, payload, source_label="t")

    def test_completely_empty_payload_is_a_no_op(self, inventory_mod):
        inv = _FakeInventory()
        inventory_mod._merge_inventory_tree(inv, {}, source_label="t")
        assert inv.hosts == {} and inv.groups == {}

    def test_null_hosts_and_groups_are_treated_as_empty(self, inventory_mod):
        """`hosts: null` / `groups: null` in JSON is the same as `{}`."""
        inv = _FakeInventory()
        inventory_mod._merge_inventory_tree(
            inv, {"hosts": None, "groups": None}, source_label="t"
        )
        assert inv.hosts == {} and inv.groups == {}


# ---------------------------------------------------------------------------
# verify_file properties (file-suffix gate)
# ---------------------------------------------------------------------------


class TestVerifyFileProperties:

    @given(stem=st.text(min_size=1, max_size=20).filter(
        lambda s: "/" not in s and "\0" not in s
    ))
    @settings(max_examples=100, **_PROP_SETTINGS)
    def test_any_stem_with_akeyless_suffix_accepted(self, inventory_mod, stem):
        """Property: any path ending in `akeyless.yml` or `akeyless.yaml`
        is accepted, regardless of the stem."""
        InventoryModule = inventory_mod.InventoryModule
        instance = InventoryModule()
        for suffix in (".akeyless.yml", ".akeyless.yaml",
                       "akeyless.yml", "akeyless.yaml"):
            assert instance.verify_file(f"{stem}{suffix}"), (
                f"verify_file rejected {stem!r}+{suffix!r}"
            )

    @given(path=st.text(min_size=1, max_size=40).filter(
        lambda s: not s.endswith((".yml", ".yaml")) and "\0" not in s
    ))
    @settings(max_examples=50, **_PROP_SETTINGS)
    def test_non_yaml_suffix_rejected(self, inventory_mod, path):
        """verify_file must reject any path not ending in .yml/.yaml."""
        InventoryModule = inventory_mod.InventoryModule
        assert not InventoryModule().verify_file(path)
