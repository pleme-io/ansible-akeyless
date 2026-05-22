# Copyright: (c) 2026, pleme-io
# MIT License
#
# Per-module live-API coverage matrix.
#
# Runs every plugins/modules/*.py against the real Akeyless API with
# minimal auto-derived required args + a unique cleanup-friendly name,
# captures the outcome per module, and writes a markdown report.
#
# Categories:
#   - WORKS         : exit_json with no error (api 2xx, module returned ok)
#   - ARGSPEC_DRIFT : api responded 4xx "Missing required parameter X"
#                     (module sent shape upstream rejects)
#   - API_404       : api responded 404 on the operation itself (path drift)
#   - NEEDS_PREREQ  : api returned 404 on a *referenced* item the test
#                     stub didn't pre-create (e.g. target_db needs a real
#                     target name). The module dispatched fine; the test
#                     just doesn't have the supporting state.
#   - DISPATCH_FAIL : Python-level crash before reaching the API (real
#                     module bug — argspec/body construction broken)
#   - SKIP          : opted out (auth/info modules with no clean stub flow)
#
# Run:
#   nix run .#live-coverage
#
# Or: pytest tests/live/coverage_matrix.py (pytest mode emits one test
# per module so CI can show per-module pass/fail).

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import ast
import datetime as _dt
import importlib.util
import io
import json
import os
import re
import socket
import sys
import time
import types
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Cap any single SDK request at 20s. When pointed at a local gateway
# (AKEYLESS_GATEWAY_URL=http://localhost:8081), the gateway does real
# network checks against the stub URLs/hosts/passwords we send -- each
# can hang for ~30s on DNS / TCP connect failures. We want a fail-fast
# classification, not a 90-minute matrix run. Public api.akeyless.io
# responds in well under 20s for every op, so this only kicks in on
# gateway-bound ops with bad stub data.
socket.setdefaulttimeout(20)

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULES_DIR = REPO_ROOT / "plugins" / "modules"
HELPER_PATH = REPO_ROOT / "plugins" / "module_utils" / "akeyless_client.py"

# Globally skip modules that need orchestration we can't auto-stub.
_SKIP_MODULES = {
    # info-only that needs a known existing item (no stub will satisfy)
    "secret_value_info.py": "reads existing secret; needs setup",
    "role_info.py":         "reads existing role",
    "roles_info.py":        "list — no required args triggers full list",
    "items_info.py":        "list",
    "item_info.py":         "needs existing item",
    "kmip_clients_info.py": "list",
    "sra_bastions_info.py": "list",
    "targets_info.py":      "list",
    # cryptographic actions need real keys
    "decrypt.py":           "needs existing key + ciphertext",
    "encrypt.py":           "needs existing key",
    "sign_jwt_with_classic_key.py": "needs existing classic key",
    "verify_pkcs1.py":      "needs key + signature",
    # token-flow modules need orchestrated parent
    "uid_list_children.py":  "needs uid_token_id from a generated parent",
    "uid_revoke_token.py":   "needs revoke_token",
    "uid_create_child_token.py": "needs uid_token_id from parent",
    # id-based CRUD (SDK Get/Update/Delete take `id`, not `name`).
    # Idempotent dispatch would need a list-by-name fallback — not in
    # the current generator. Module dispatches fine when caller passes
    # an explicit `id`; the auto-stub can't synthesize a valid id.
    "account_custom_field.py": "SDK Get/Update/Delete use `id`, not `name` — needs explicit id from list",
    "policy.py":               "SDK PoliciesGet/Update/Delete use `id`, not path — needs id discovery",
    # esm read_resource currently uses `name`, but SDK's EsmGet requires
    # esm_name + secret_id — secret_id needs list-discovery from
    # secret_name. Module dispatches fine when caller pre-orchestrates.
    "esm.py": "EsmGet needs secret_id — needs list-then-find from secret_name",
    "usc.py": "UscGet/Update/Delete use secret_id, UscCreate uses secret_name — split CRUD",
}


def _all_module_files():
    return sorted(p.name for p in MODULES_DIR.glob("*.py") if p.name != "__init__.py")


def _parse_argspec(module_path):
    tree = ast.parse(module_path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "argument_spec":
                    try:
                        return ast.literal_eval(node.value)
                    except (ValueError, SyntaxError):
                        return None
    return None


def _parse_required_if(module_path):
    """Extract field names that become required when state=present from
    the AnsibleModule(..., required_if=[...]) call. Lets the stub fill
    them so the SDK model constructor doesn't reject None on dispatch."""
    fields = []
    tree = ast.parse(module_path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            for kw in node.keywords:
                if kw.arg == "required_if" and isinstance(kw.value, ast.List):
                    for cond in kw.value.elts:
                        if isinstance(cond, ast.Tuple) and len(cond.elts) >= 3:
                            try:
                                key, val, required = ast.literal_eval(cond)[:3]
                            except (ValueError, SyntaxError):
                                continue
                            if key == "state" and val == "present" and isinstance(required, (list, tuple)):
                                fields.extend(required)
    return fields


# Type-aware stubs. Tweak by module-specific heuristic for fields that
# carry semantic constraints (name conventions, etc.).
_STUBS = {
    'str':   "stub",
    'int':   1,
    'bool':  False,  # safer default (some `delete_protection: True` would prevent cleanup)
    'list':  [],
    'dict':  {},
    'path':  "/tmp/stub",
    'raw':   "stub",
    'float': 1.0,
}


def _smart_stub(field_name):
    """Per-field semantic stubs so the API doesn't reject obvious junk.
    Matches by substring on the field name; ordered from most specific
    to least specific."""
    n = field_name.lower()
    if "url" in n or "endpoint" in n:
        return "https://example.invalid/akeyless-coverage-stub"
    if "email" in n:
        return "akeyless-coverage-stub@example.invalid"
    if n.endswith("_arn") or n == "role_arn":
        return "arn:aws:iam::000000000000:role/stub"
    if "region" in n:
        return "us-east-1"
    if "algorithm" in n or n.endswith("_algo"):
        return "RSA2048"
    if "host" in n or "address" in n:
        return "stub.example.invalid"
    if "port" in n:
        return "443"
    if n in {"private_key", "ssh_password", "password"}:
        return "stub-credential"
    return "stub"


def _minimal_params(argspec, run_id, module_name, required_if_fields=()):
    params = {}
    for name, opts in (argspec or {}).items():
        if not isinstance(opts, dict):
            continue
        if opts.get("required") or name in required_if_fields:
            t = opts.get("type", "str")
            if t == "str":
                params[name] = _smart_stub(name)
            else:
                params[name] = _STUBS.get(t, "stub")
    # Identity fields → unique cleanup-friendly path
    test_path = f"/test-live/{run_id}/{module_name}"
    for key in ("name", "role_name", "am_name"):
        if key in params and isinstance(params[key], str):
            params[key] = test_path
            break
    # Sensible elements for list-of-strings
    for k, opts in (argspec or {}).items():
        if isinstance(opts, dict) and opts.get("type") == "list" and (opts.get("required") or k in required_if_fields) and opts.get("elements") == "str":
            params[k] = [_smart_stub(k)]
    return params


def _classify(outcome):
    """Categorize an exit_json/fail_json kwargs dict."""
    msg = (outcome.get("msg") or "").lower()
    failed = outcome.get("failed", False)
    if not failed:
        # No msg = create or update happened cleanly.
        # "already in desired state" = the new idempotency path returning
        # changed=False because compute_diff found no drift. Honest
        # convergence is the *goal*, not a failure — count both as WORKS.
        if not msg or "already in desired state" in msg or "already absent" in msg:
            return "WORKS"
    # Timeout = network/connection didn't return within socket timeout.
    # Common when pointing at a local gateway that's actually trying
    # to validate stub data against the real internet.
    if "timed out" in msg or "timeout" in msg or "read timed out" in msg:
        return "TIMEOUT"
    # API drift signatures
    if "missing required parameter" in msg:
        return "ARGSPEC_DRIFT"
    if "status 404" in msg and "endpoint" in msg.lower():
        return "API_404"
    if "status 404" in msg:
        # Most 404s are missing-prereq (e.g., target_name references nothing)
        return "NEEDS_PREREQ"
    if "failed to obtain item" in msg or "not found" in msg:
        return "NEEDS_PREREQ"
    if "akeyless api call" in msg and "failed" in msg:
        return "API_REJECTED"
    return "OTHER"


# Reuse the mock conftest's module-loading machinery, but route SDK
# calls to a *real* akeyless client instead of a stub.
def _run_module_against_real_api(module_filename, params):
    """Load plugins/modules/<file>, run main() against the real
    akeyless SDK, capture exit_json/fail_json kwargs. Returns the
    kwargs dict and exit code."""

    # Install a real-ansible-shaped AnsibleModule that doesn't sys.exit.
    class _ExitJson(SystemExit):
        def __init__(self, **kw):
            super().__init__(0)
            self.kwargs = kw

    class _FailJson(SystemExit):
        def __init__(self, **kw):
            super().__init__(1)
            self.kwargs = kw

    ansible_mod = sys.modules.get("ansible") or types.ModuleType("ansible")
    util_mod = sys.modules.get("ansible.module_utils") or types.ModuleType("ansible.module_utils")
    basic_mod = types.ModuleType("ansible.module_utils.basic")
    sys.modules["ansible"] = ansible_mod
    sys.modules["ansible.module_utils"] = util_mod
    sys.modules["ansible.module_utils.basic"] = basic_mod
    ansible_mod.module_utils = util_mod
    util_mod.basic = basic_mod

    def factory(argument_spec=None, supports_check_mode=False, required_if=None, **_kw):
        module = MagicMock(name="AnsibleModule")
        resolved = {}
        for key, opts in (argument_spec or {}).items():
            if isinstance(opts, dict) and "default" in opts:
                resolved[key] = opts["default"]
            else:
                resolved[key] = None
        resolved.update(params or {})
        # Inject auth from env so the SDK can authenticate. Three of
        # the auto-generated modules (gateway_allowed_access,
        # gateway_k8s_auth_config, target_aws) have resource fields
        # whose names collide with auth fields (`access_id` /
        # `access_key`). In real use, the user passes one or the other
        # — in this stub run we always want env-based auth to win, so
        # we overwrite (not setdefault) when env is present.
        for env_key, param_key in (
            ("AKEYLESS_ACCESS_ID", "access_id"),
            ("AKEYLESS_ACCESS_KEY", "access_key"),
            ("AKEYLESS_GATEWAY_URL", "gateway_url"),
        ):
            env_val = os.environ.get(env_key)
            if env_val:
                resolved[param_key] = env_val
        resolved.setdefault("gateway_url", "https://api.akeyless.io")
        module.params = resolved
        module.check_mode = False
        module.argument_spec = argument_spec

        def _exit_json(**kw):
            raise _ExitJson(**kw)

        def _fail_json(**kw):
            raise _FailJson(failed=True, **kw)

        module.exit_json.side_effect = _exit_json
        module.fail_json.side_effect = _fail_json
        return module

    basic_mod.AnsibleModule = factory

    # Map ansible_collections.drzln0.akeyless.* → the on-disk helper
    namespace = "drzln0"
    name = "akeyless"
    for n in (
        "ansible_collections",
        f"ansible_collections.{namespace}",
        f"ansible_collections.{namespace}.{name}",
        f"ansible_collections.{namespace}.{name}.plugins",
        f"ansible_collections.{namespace}.{name}.plugins.module_utils",
    ):
        if n not in sys.modules:
            sys.modules[n] = types.ModuleType(n)
    spec = importlib.util.spec_from_file_location(
        f"ansible_collections.{namespace}.{name}.plugins.module_utils.akeyless_client",
        HELPER_PATH,
    )
    helper = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = helper
    spec.loader.exec_module(helper)

    # Load the target module fresh
    mod_spec = importlib.util.spec_from_file_location(
        f"akeyless_live_target_{module_filename[:-3]}",
        MODULES_DIR / module_filename,
    )
    target = importlib.util.module_from_spec(mod_spec)
    sys.modules[mod_spec.name] = target
    try:
        mod_spec.loader.exec_module(target)
    except Exception as e:
        return {"msg": f"module import failed: {type(e).__name__}: {e}"}, "DISPATCH_FAIL"

    try:
        target.main()
    except SystemExit as e:
        kw = getattr(e, "kwargs", {})
        code = getattr(e, "code", None)
        return kw, code
    except Exception as e:
        return {"msg": f"unhandled exception: {type(e).__name__}: {e}"}, "DISPATCH_FAIL"
    return {"msg": "main() returned without exit"}, "DISPATCH_FAIL"


# --- pytest entry: parametrize over every module ---


@pytest.fixture(scope="session")
def run_id():
    return _dt.datetime.utcnow().strftime("%Y%m%d-%H%M%S")


@pytest.mark.parametrize("module_file", _all_module_files())
def test_module_live_dispatch(module_file, run_id):
    """Smoke-dispatch every module against real Akeyless.

    Categorizes the outcome and asserts only DISPATCH_FAIL (real
    module-side crashes) fail the test. ARGSPEC_DRIFT and other
    API-side disagreements are reported via the matrix but don't
    fail the suite (those need iac-forge regen, not in-place
    patches)."""

    if not os.environ.get("AKEYLESS_ACCESS_ID"):
        pytest.skip("AKEYLESS_ACCESS_ID not in env (run via nix run .#live-coverage)")

    if module_file in _SKIP_MODULES:
        pytest.skip(_SKIP_MODULES[module_file])

    argspec = _parse_argspec(MODULES_DIR / module_file)
    if argspec is None:
        pytest.skip("could not parse argspec")

    required_if_fields = _parse_required_if(MODULES_DIR / module_file)
    params = _minimal_params(argspec, run_id, module_file[:-3], required_if_fields)
    kwargs, code = _run_module_against_real_api(module_file, params)
    category = _classify(kwargs) if code == 0 else (code if isinstance(code, str) else _classify(kwargs))

    # Record in the matrix. With pytest-xdist multiple workers may write
    # concurrently — use fcntl.flock on a sibling lockfile + atomic
    # rename so partial writes can't corrupt the JSON.
    import fcntl
    matrix_path = REPO_ROOT / "tests" / "live" / "MATRIX.json"
    lock_path = matrix_path.with_suffix(".lock")
    matrix_path.parent.mkdir(parents=True, exist_ok=True)
    with open(lock_path, "w") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        try:
            matrix = json.loads(matrix_path.read_text()) if matrix_path.exists() else {}
        except Exception:
            matrix = {}
        matrix[module_file] = {
            "category": category,
            "msg": (kwargs.get("msg") or "")[:300],
            "run_id": run_id,
        }
        tmp_path = matrix_path.with_suffix(".json.tmp")
        tmp_path.write_text(json.dumps(matrix, indent=2, sort_keys=True))
        tmp_path.replace(matrix_path)

    # Only DISPATCH_FAIL (real bug) fails the test. Others are reported.
    if category == "DISPATCH_FAIL":
        pytest.fail(f"{module_file}: {category} — {kwargs.get('msg')}")
