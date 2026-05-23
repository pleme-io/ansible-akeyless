# Copyright: (c) 2026, pleme-io
# MIT License
#
# Sweep every plugin file (excluding plugins/modules/, which has its
# own dedicated load sweep) and verify it imports cleanly AND exposes
# the entry-point class/symbol Ansible's plugin loader looks for.
#
# Catches the class of regressions where a plugin file is syntactically
# valid but missing the expected class (LookupModule / FilterModule /
# TestModule / CallbackModule / ActionModule / InventoryModule).
#
# This is the "every non-module plugin works at the loader level"
# certainty layer -- complement to tests/mock/test_every_module_loads.py.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import importlib.util
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PLUGINS_DIR = REPO_ROOT / "plugins"


# Plugin-type -> (subdir name, entry-point symbol, "extra-stub" key).
# entry_point can be a tuple of acceptable names when more than one is
# valid (e.g. test plugins use TestModule with a tests() method,
# filter plugins use FilterModule with a filters() method).
PLUGIN_TYPES = [
    {"subdir": "lookup",    "entry_point": "LookupModule",    "needs_lookup_stub": True},
    {"subdir": "inventory", "entry_point": "InventoryModule", "needs_inventory_stub": True},
    {"subdir": "filter",    "entry_point": "FilterModule",    "needs_errors_stub": True},
    {"subdir": "test",      "entry_point": "TestModule",      "needs_errors_stub": False},
    {"subdir": "callback",  "entry_point": "CallbackModule",  "needs_callback_stub": True},
    {"subdir": "action",    "entry_point": "ActionModule",    "needs_action_stub": True},
    {"subdir": "cache",     "entry_point": "CacheModule",     "needs_cache_stub": True},
]


def _all_plugin_files():
    """Yield (subdir, entry_point, plugin_path) for every plugin file."""
    for spec in PLUGIN_TYPES:
        d = PLUGINS_DIR / spec["subdir"]
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.py")):
            if p.name.startswith("_"):
                continue
            yield spec["subdir"], spec["entry_point"], p


def _install_minimal_stubs():
    """Install the bare minimum stub modules so every plugin type
    can import. Each block is idempotent + additive."""
    ansible_pkg = sys.modules.setdefault("ansible", types.ModuleType("ansible"))

    # ansible.errors with every exception class our plugins might import.
    errors_mod = sys.modules.get("ansible.errors")
    if errors_mod is None:
        errors_mod = types.ModuleType("ansible.errors")
        sys.modules["ansible.errors"] = errors_mod
        ansible_pkg.errors = errors_mod
    for cls_name in ("AnsibleError", "AnsibleLookupError",
                     "AnsibleFilterError", "AnsibleActionFail"):
        if not hasattr(errors_mod, cls_name):
            setattr(errors_mod, cls_name, type(cls_name, (Exception,), {}))

    # ansible.plugins.* hierarchy.
    plugins_mod = sys.modules.setdefault(
        "ansible.plugins", types.ModuleType("ansible.plugins")
    )
    ansible_pkg.plugins = plugins_mod

    # Lookup
    if "ansible.plugins.lookup" not in sys.modules:
        m = types.ModuleType("ansible.plugins.lookup")

        class _LB:
            def __init__(self):
                self._opts = {}
            def set_options(self, var_options=None, direct=None):
                self._opts = dict(direct or {})
            def get_option(self, name):
                return self._opts.get(name)

        m.LookupBase = _LB
        sys.modules["ansible.plugins.lookup"] = m

    # Inventory
    if "ansible.plugins.inventory" not in sys.modules:
        m = types.ModuleType("ansible.plugins.inventory")

        class _BIP:
            def __init__(self):
                self._opts = {}
            def verify_file(self, p): return True
            def _read_config_data(self, p): pass
            def get_option(self, n): return self._opts.get(n)
            def parse(self, *a, **k): pass

        class _Const:
            pass

        m.BaseInventoryPlugin = _BIP
        m.Constructable = _Const
        sys.modules["ansible.plugins.inventory"] = m

    # Action
    if "ansible.plugins.action" not in sys.modules:
        m = types.ModuleType("ansible.plugins.action")

        class _AB:
            def __init__(self):
                self._task = None
                self._templar = None
                self._loader = None
            def run(self, tmp=None, task_vars=None):
                return {}
            def _execute_module(self, **kw):
                return {"changed": True}

        m.ActionBase = _AB
        sys.modules["ansible.plugins.action"] = m

    if "ansible.plugins.loader" not in sys.modules:
        m = types.ModuleType("ansible.plugins.loader")
        m.lookup_loader = MagicMock(name="lookup_loader")
        sys.modules["ansible.plugins.loader"] = m

    # Callback
    if "ansible.plugins.callback" not in sys.modules:
        m = types.ModuleType("ansible.plugins.callback")

        class _CB:
            def __init__(self):
                self._opts = {}
            def set_options(self, **kw): pass
            def get_option(self, n): return self._opts.get(n)
            def v2_runner_on_ok(self, r): return None
            def v2_runner_on_failed(self, r, **kw): return None
            def v2_runner_on_unreachable(self, r): return None

        m.CallbackBase = _CB
        sys.modules["ansible.plugins.callback"] = m
    if "ansible.plugins.callback.default" not in sys.modules:
        m = types.ModuleType("ansible.plugins.callback.default")
        m.CallbackModule = sys.modules["ansible.plugins.callback"].CallbackBase
        sys.modules["ansible.plugins.callback.default"] = m

    # Cache
    if "ansible.plugins.cache" not in sys.modules:
        m = types.ModuleType("ansible.plugins.cache")

        class _BCM:
            def __init__(self, *args, **kwargs): self._opts = {}
            def get_option(self, n): return self._opts.get(n)
            def set_options(self, **kw): self._opts.update(kw)

        m.BaseCacheModule = _BCM
        sys.modules["ansible.plugins.cache"] = m

    # ansible.module_utils.basic (for the secret_to_file module wrapper).
    if "ansible.module_utils.basic" not in sys.modules:
        util = sys.modules.setdefault(
            "ansible.module_utils", types.ModuleType("ansible.module_utils")
        )
        ansible_pkg.module_utils = util
        basic = types.ModuleType("ansible.module_utils.basic")
        basic.AnsibleModule = MagicMock(name="AnsibleModule")
        sys.modules["ansible.module_utils.basic"] = basic
        util.basic = basic

    # ansible_collections.<...>.module_utils path for lookup_auth helper.
    for name in (
        "ansible_collections",
        "ansible_collections.drzln0",
        "ansible_collections.drzln0.akeyless",
        "ansible_collections.drzln0.akeyless.plugins",
        "ansible_collections.drzln0.akeyless.plugins.module_utils",
    ):
        sys.modules.setdefault(name, types.ModuleType(name))
    full = ("ansible_collections.drzln0.akeyless.plugins.module_utils"
            ".akeyless_lookup_auth")
    if full not in sys.modules:
        helper_path = PLUGINS_DIR / "module_utils" / "akeyless_lookup_auth.py"
        spec = importlib.util.spec_from_file_location(full, helper_path)
        m = importlib.util.module_from_spec(spec)
        sys.modules[full] = m
        spec.loader.exec_module(m)


def _load_plugin(plugin_path):
    """Load a plugin file as a unique synthetic module."""
    name = f"akeyless_plugin_load_test_{plugin_path.parent.name}_{plugin_path.stem}"
    spec = importlib.util.spec_from_file_location(name, plugin_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


PLUGIN_CASES = list(_all_plugin_files())


def _install_fake_akeyless():
    """Install a fake akeyless SDK with the minimum surface our
    plugins reach for. tests/mock/conftest doesn't expose fake_akeyless
    so this test installs its own (idempotent against existing
    sys.modules entries)."""
    if "akeyless" in sys.modules and hasattr(sys.modules["akeyless"], "V2Api"):
        return
    akeyless_mod = types.ModuleType("akeyless")
    akeyless_mod.__getattr__ = lambda name: MagicMock(name=f"akeyless.{name}")  # type: ignore[attr-defined]
    akeyless_mod.Configuration = MagicMock(name="akeyless.Configuration")
    akeyless_mod.ApiClient = MagicMock(name="akeyless.ApiClient")
    akeyless_mod.V2Api = MagicMock(name="akeyless.V2Api")
    akeyless_mod.Auth = MagicMock(name="akeyless.Auth")
    exc_mod = types.ModuleType("akeyless.exceptions")
    exc_mod.ApiException = type("ApiException", (Exception,), {})
    akeyless_mod.exceptions = exc_mod
    sys.modules["akeyless"] = akeyless_mod
    sys.modules["akeyless.exceptions"] = exc_mod


@pytest.fixture(autouse=True, scope="module")
def _bootstrap():
    """Install stubs once per test session."""
    _install_fake_akeyless()
    _install_minimal_stubs()
    yield


@pytest.mark.parametrize(
    "plugin_subdir,entry_point,plugin_path",
    PLUGIN_CASES,
    ids=lambda v: v.name if isinstance(v, Path) else str(v),
)
def test_plugin_imports_cleanly(plugin_subdir, entry_point, plugin_path):
    """Every non-module plugin file must import without error AND
    expose the entry-point symbol Ansible's loader looks for.
    Catches regressions like: rename, accidental class deletion,
    syntax errors that only show up when a non-default Python loads
    the file."""
    mod = _load_plugin(plugin_path)
    assert hasattr(mod, entry_point), (
        f"plugins/{plugin_subdir}/{plugin_path.name} loaded but doesn't "
        f"define `{entry_point}` -- Ansible's {plugin_subdir} loader "
        f"won't be able to dispatch this plugin"
    )
    # The entry point must be a class (Ansible inspects __mro__).
    cls = getattr(mod, entry_point)
    assert isinstance(cls, type), (
        f"plugins/{plugin_subdir}/{plugin_path.name}: {entry_point} "
        f"resolves to {type(cls).__name__}, expected a class"
    )


@pytest.mark.parametrize(
    "plugin_subdir,entry_point,plugin_path",
    PLUGIN_CASES,
    ids=lambda v: v.name if isinstance(v, Path) else str(v),
)
def test_plugin_entry_point_instantiable(plugin_subdir, entry_point, plugin_path):
    """Every entry-point class must construct without arguments
    (Ansible's loader calls `EntryPointClass()` with no args). Catches
    plugins that broke their no-arg __init__ during a refactor."""
    mod = _load_plugin(plugin_path)
    cls = getattr(mod, entry_point)
    try:
        instance = cls()
    except TypeError as exc:
        pytest.fail(
            f"plugins/{plugin_subdir}/{plugin_path.name}: "
            f"{entry_point}() requires arguments: {exc}"
        )
    # Sanity: the instance has the expected dispatch method.
    expected_methods = {
        "LookupModule": "run",
        "InventoryModule": "parse",
        "FilterModule": "filters",
        "TestModule": "tests",
        "CallbackModule": "v2_runner_on_ok",
        "ActionModule": "run",
        "CacheModule": "get",
    }
    method = expected_methods.get(entry_point)
    if method:
        assert hasattr(instance, method), (
            f"plugins/{plugin_subdir}/{plugin_path.name}: "
            f"{entry_point} instance missing expected dispatch method "
            f"`{method}`"
        )
