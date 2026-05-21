# Copyright: (c) 2026, pleme-io
# MIT License
#
# Parameterized AST-based structural assertions across every generated
# module under plugins/modules/. Verifies:
#   * argument_spec is a dict literal with auth keys + at least one input
#   * main() is defined
#   * imports get_client / call_api / build_body from the helper
#   * CRUD modules use PascalCase model + snake_case method
#   * action modules disable check mode
#   * _info modules omit state and exit with changed=False
#   * access_key argspec entries are marked no_log: True

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
MODULES_DIR = REPO_ROOT / "plugins" / "modules"
HELPER_IMPORT = (
    "from ansible_collections.akeyless.akeyless.plugins.module_utils.akeyless_client"
)
HELPER_NAMES = {"get_client", "call_api", "build_body"}
AUTH_KEYS = {"gateway_url", "access_id", "access_key", "access_type"}


def _module_files():
    return sorted(p for p in MODULES_DIR.glob("*.py") if not p.name.startswith("_"))


def _argument_spec_entries(tree: ast.AST):
    """Return {key: argspec dict literal} for the first argument_spec assignment."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "argument_spec":
                    if isinstance(node.value, ast.Dict):
                        return {
                            k.value: v
                            for k, v in zip(node.value.keys, node.value.values)
                            if isinstance(k, ast.Constant) and isinstance(k.value, str)
                        }
    return {}


def _function_defs(tree: ast.AST):
    return {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}


def _call_api_invocations(tree: ast.AST):
    """List of (model_arg, method_arg) literal strings passed to call_api."""
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", None)
        if name != "call_api" or len(node.args) < 3:
            continue
        method_node = node.args[2]
        if isinstance(method_node, ast.Constant) and isinstance(method_node.value, str):
            out.append(method_node.value)
    return out


def _build_body_model_args(tree: ast.AST):
    """List of model-class string literals passed as the first arg to build_body."""
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", None)
        if name != "build_body" or not node.args:
            continue
        model_node = node.args[0]
        if isinstance(model_node, ast.Constant) and isinstance(model_node.value, str):
            out.append(model_node.value)
    return out


def _ansible_module_kwargs(tree: ast.AST):
    """Return the kwargs of the first AnsibleModule(...) call as a dict of constants."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", None)
        if name != "AnsibleModule":
            continue
        kw = {}
        for k in node.keywords:
            if isinstance(k.value, ast.Constant):
                kw[k.arg] = k.value.value
        return kw
    return {}


def _exit_json_kwargs(tree: ast.AST):
    """Yield each (kw_name -> constant_value) dict from every exit_json call."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", None)
        if name != "exit_json":
            continue
        kw = {
            k.arg: k.value.value if isinstance(k.value, ast.Constant) else None
            for k in node.keywords
        }
        yield kw


def _is_pascal_case(name: str) -> bool:
    return bool(name) and name[0].isupper()


def _is_snake_case(name: str) -> bool:
    return bool(name) and name == name.lower() and " " not in name


# ---------------------------------------------------------------------------
# Parametrisation
# ---------------------------------------------------------------------------


MODULE_PATHS = _module_files()


@pytest.fixture(scope="session")
def all_module_trees():
    """Pre-parsed AST for every module: speed + diagnostics."""
    out = {}
    for p in MODULE_PATHS:
        out[p.name] = (p, ast.parse(p.read_text()))
    return out


@pytest.mark.parametrize("module_path", MODULE_PATHS, ids=lambda p: p.name)
def test_module_has_argument_spec_with_auth_keys(module_path):
    tree = ast.parse(module_path.read_text())
    spec = _argument_spec_entries(tree)
    assert spec, f"{module_path.name}: argument_spec missing or not a dict literal"
    assert AUTH_KEYS.issubset(set(spec)), (
        f"{module_path.name}: argument_spec missing auth keys "
        f"{AUTH_KEYS - set(spec)}"
    )
    # Most CRUD / action modules require user inputs beyond auth + state.
    # A handful of list-style info modules (e.g. groups_info, roles_info)
    # legitimately have no filters at all because the upstream API is
    # parameter-free, so we allow those to have only auth keys.
    non_auth = set(spec) - AUTH_KEYS - {"state"}
    if not module_path.name.endswith("_info.py"):
        assert non_auth, f"{module_path.name}: argument_spec has no input keys"


@pytest.mark.parametrize("module_path", MODULE_PATHS, ids=lambda p: p.name)
def test_module_has_main(module_path):
    tree = ast.parse(module_path.read_text())
    assert "main" in _function_defs(tree), f"{module_path.name}: missing def main()"


@pytest.mark.parametrize("module_path", MODULE_PATHS, ids=lambda p: p.name)
def test_module_imports_helper_functions(module_path):
    source = module_path.read_text()
    assert HELPER_IMPORT in source, f"{module_path.name}: helper import missing"
    # Must import at least one of the helper symbols.
    tree = ast.parse(source)
    imported = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.ImportFrom)
            and node.module
            and node.module.endswith("akeyless_client")
        ):
            imported.update(alias.name for alias in node.names)
    assert imported & HELPER_NAMES, (
        f"{module_path.name}: imports nothing from akeyless_client; expected one of "
        f"{HELPER_NAMES}, got {imported}"
    )


@pytest.mark.parametrize("module_path", MODULE_PATHS, ids=lambda p: p.name)
def test_crud_modules_use_pascal_and_snake(module_path):
    tree = ast.parse(module_path.read_text())
    fns = _function_defs(tree)
    if "create_resource" not in fns:
        pytest.skip("not a CRUD module")
    # Every build_body model arg should be PascalCase; every call_api method
    # arg should be snake_case.
    for model in _build_body_model_args(tree):
        assert _is_pascal_case(model), (
            f"{module_path.name}: build_body model {model!r} not PascalCase"
        )
    for method in _call_api_invocations(tree):
        assert _is_snake_case(method), (
            f"{module_path.name}: call_api method {method!r} not snake_case"
        )


@pytest.mark.parametrize("module_path", MODULE_PATHS, ids=lambda p: p.name)
def test_action_modules_disable_check_mode(module_path):
    tree = ast.parse(module_path.read_text())
    if "run_action" not in _function_defs(tree):
        pytest.skip("not an action module")
    kw = _ansible_module_kwargs(tree)
    assert kw.get("supports_check_mode") is False, (
        f"{module_path.name}: action module must set supports_check_mode=False"
    )
    assert _argument_spec_entries(tree), (
        f"{module_path.name}: action module missing argument_spec"
    )


@pytest.mark.parametrize("module_path", MODULE_PATHS, ids=lambda p: p.name)
def test_info_modules_have_no_state_and_exit_unchanged(module_path):
    if not module_path.name.endswith("_info.py"):
        pytest.skip("not an info module")
    tree = ast.parse(module_path.read_text())
    spec = _argument_spec_entries(tree)
    assert "state" not in spec, (
        f"{module_path.name}: info module must not declare a `state` parameter"
    )
    # At least one exit_json must have changed=False; data sources never mutate.
    saw_unchanged = any(
        kw.get("changed") is False for kw in _exit_json_kwargs(tree)
    )
    assert saw_unchanged, (
        f"{module_path.name}: info module never calls exit_json(changed=False)"
    )


@pytest.mark.parametrize("module_path", MODULE_PATHS, ids=lambda p: p.name)
def test_access_key_has_no_log_true(module_path):
    tree = ast.parse(module_path.read_text())
    spec = _argument_spec_entries(tree)
    if "access_key" not in spec:
        pytest.skip("no access_key in spec (impossible for generated modules)")
    entry = spec["access_key"]
    assert isinstance(entry, ast.Dict), (
        f"{module_path.name}: access_key spec must be a dict literal"
    )
    no_log = None
    for k, v in zip(entry.keys, entry.values):
        if isinstance(k, ast.Constant) and k.value == "no_log":
            if isinstance(v, ast.Constant):
                no_log = v.value
    assert no_log is True, (
        f"{module_path.name}: access_key argspec missing 'no_log': True"
    )


def test_module_count_is_reasonable():
    """Stat: every PR should keep the collection at >=150 modules."""
    assert len(MODULE_PATHS) >= 150, (
        f"only {len(MODULE_PATHS)} modules under {MODULES_DIR}"
    )
