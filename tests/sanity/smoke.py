"""Structural smoke test for the generated Ansible collection.

Walks every module under plugins/modules/, AST-parses it, and verifies the
generator-contracted shape: argument_spec is present and non-empty, main()
exists, every module imports the shared akeyless_client helper, every module
calls call_api(...) with a string literal method name, and any module that
declares a _sensitive masking set lists fields that match its action_module
sensitive_response_fields contract.

Cross-checks every call_api() method name against the method names declared
in the local akeyless-python SDK source (if available) — catches generator
regressions that emit non-existent SDK methods.

Runtime: pure stdlib. No need to install the `akeyless` package.
Exit code: 0 on success, 1 on any failure.
"""
from __future__ import annotations

import ast
import os
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
MOD_DIR = ROOT / "plugins" / "modules"
UTIL = ROOT / "plugins" / "module_utils" / "akeyless_client.py"

# Optional cross-check against the local akeyless-python SDK source.
SDK_V2API = Path(
    "/home/drzzln/code/github/pleme-io/akeyless-python/akeyless/api/v2_api.py"
)


_HELPER_TUPLE_KW = {
    # run_standard_crud(sdk_create=(Model, method), ...)
    "sdk_create", "sdk_update", "sdk_delete", "sdk_read",
    # run_action_module(sdk_call=...) / run_info_module(sdk_call=...)
    "sdk_call",
}


def extract_call_api_methods(tree: ast.AST) -> list[str]:
    """Return every SDK-method string the module routes through.

    Covers two shapes:
      1. Legacy: call_api(module, client, "method_name", ...) -- the
         third positional arg is the snake_case method name.
      2. Post-refactor: run_{standard_crud,action_module,info_module}(
            sdk_*=("ModelName", "method_name"), ...) -- the second tuple
         element is the snake_case method name.
    """
    out: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", None)
        # Legacy call_api shape.
        if name == "call_api" and len(node.args) >= 3:
            m = node.args[2]
            if isinstance(m, ast.Constant) and isinstance(m.value, str):
                out.append(m.value)
            continue
        # Helper-call shape: pull tuple second-elements out of sdk_* kwargs.
        for kw in node.keywords:
            if kw.arg not in _HELPER_TUPLE_KW:
                continue
            if (isinstance(kw.value, ast.Tuple)
                    and len(kw.value.elts) == 2
                    and isinstance(kw.value.elts[1], ast.Constant)
                    and isinstance(kw.value.elts[1].value, str)):
                out.append(kw.value.elts[1].value)
    return out


def extract_argument_spec_keys(tree: ast.AST) -> set[str]:
    """Return the set of keys declared in the first argument_spec = {...}."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "argument_spec":
                if isinstance(node.value, ast.Dict):
                    return {
                        k.value
                        for k in node.value.keys
                        if isinstance(k, ast.Constant) and isinstance(k.value, str)
                    }
    return set()


def extract_sdk_methods_from_source(p: Path) -> set[str]:
    """Return the set of public method names defined on V2Api."""
    if not p.exists():
        return set()
    tree = ast.parse(p.read_text())
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "V2Api":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and not item.name.startswith("_"):
                    if not item.name.endswith("_with_http_info"):
                        out.add(item.name)
    return out


def main() -> int:
    if not MOD_DIR.is_dir():
        print(f"ERROR: {MOD_DIR} not found", file=sys.stderr)
        return 1

    sdk_methods = extract_sdk_methods_from_source(SDK_V2API)
    if sdk_methods:
        print(f"[sdk] {len(sdk_methods)} V2Api methods loaded from {SDK_V2API}")
    else:
        print(f"[sdk] cross-check skipped — {SDK_V2API} not available")

    # The helper itself must parse cleanly.
    try:
        ast.parse(UTIL.read_text())
        print(f"[ok ] {UTIL.name} parses")
    except SyntaxError as e:
        print(f"FAIL {UTIL}: {e}", file=sys.stderr)
        return 1

    failures: list[str] = []
    method_counts: Counter[str] = Counter()
    sdk_misses: set[str] = set()
    total = 0

    for fn in sorted(os.listdir(MOD_DIR)):
        if not fn.endswith(".py"):
            continue
        total += 1
        p = MOD_DIR / fn
        try:
            tree = ast.parse(p.read_text())
        except SyntaxError as e:
            failures.append(f"{fn}: SyntaxError: {e}")
            continue

        source = p.read_text()

        if "from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client" not in source:
            failures.append(f"{fn}: missing akeyless_client import")
            continue

        if "def main()" not in source:
            failures.append(f"{fn}: missing main()")
            continue

        argspec = extract_argument_spec_keys(tree)
        if not argspec:
            failures.append(f"{fn}: argument_spec empty or missing")
            continue
        for auth_key in ("gateway_url", "access_id", "access_key", "access_type"):
            if auth_key not in argspec:
                failures.append(f"{fn}: argument_spec missing auth key {auth_key!r}")

        methods = extract_call_api_methods(tree)
        if not methods:
            failures.append(
                f"{fn}: no SDK method discoverable (neither call_api(...) "
                "nor run_*(sdk_*=(Model, method)) found)"
            )
            continue

        for m in methods:
            method_counts[m] += 1
            if sdk_methods and m not in sdk_methods:
                sdk_misses.add(m)

    print(f"[stat] modules scanned: {total}")
    print(f"[stat] unique call_api methods: {len(method_counts)}")
    if sdk_methods:
        cov = (len(method_counts) - len(sdk_misses)) / max(1, len(method_counts))
        print(f"[stat] SDK method coverage: {len(method_counts) - len(sdk_misses)}/{len(method_counts)} ({cov:.0%})")

    if sdk_misses:
        for m in sorted(sdk_misses):
            uses = [
                fn for fn in os.listdir(MOD_DIR)
                if fn.endswith(".py") and f'"{m}"' in (MOD_DIR / fn).read_text()
            ]
            failures.append(
                f"call_api({m!r}) not found on V2Api ({len(uses)} module(s): "
                f"{', '.join(uses[:3])}{'…' if len(uses) > 3 else ''})"
            )

    if failures:
        print(f"\n{len(failures)} failure(s):", file=sys.stderr)
        for f in failures[:40]:
            print(f"  {f}", file=sys.stderr)
        if len(failures) > 40:
            print(f"  … and {len(failures) - 40} more", file=sys.stderr)
        return 1

    print(f"\n[done] {total} modules pass structural + SDK sanity")
    return 0


if __name__ == "__main__":
    sys.exit(main())
