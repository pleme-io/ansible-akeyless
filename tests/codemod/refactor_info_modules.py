#!/usr/bin/env python3
"""One-shot codemod: collapse every plugins/modules/*_info.py onto
`run_info_module(argument_spec, sdk_call=(Model, method))`.

Extracts the SDK model + method from the existing `read_resource`
function (which always does build_body(Model, ...) + call_api(...,
method, ...)), then rewrites the module to the helper-call shape.

Skip-safe: already-collapsed modules (`run_info_module` present) are
ignored. Runs idempotent.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULES = ROOT / "plugins" / "modules"

HELPER_IMPORT = (
    "from ansible_collections.drzln0.akeyless.plugins.module_utils.akeyless_client "
    "import (\n    run_info_module,\n)"
)


def _argspec_block(src: str) -> str:
    """Extract the argument_spec dict literal as it appears in the
    source (including `argument_spec = {...}`). The legacy info modules
    define it inside main() with 8-space indent on each line; we
    promote it to module level, so we strip 4 spaces off every line of
    the literal (the difference between in-fn and top-level indent)."""
    m = re.search(r"argument_spec\s*=\s*\{", src)
    if not m:
        raise ValueError("argument_spec not found")
    start = m.end() - 1  # the '{'
    depth = 0
    for i in range(start, len(src)):
        ch = src[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                raw = src[m.start():i + 1]
                # The first line begins at column 4 (inside def main()),
                # because the regex matched `argument_spec` -- preceded by
                # 4 spaces in the original source but our slice starts at
                # the 'a' so the first line has no leading indent. Lines
                # 2..N still carry the original 8-space indent. Normalize
                # those by removing exactly 4 leading spaces.
                lines = raw.splitlines()
                fixed = [lines[0]]
                for ln in lines[1:]:
                    fixed.append(ln[4:] if ln.startswith("    ") else ln)
                return "\n".join(fixed)
    raise ValueError("argument_spec braces never closed")


def _extract_sdk_call(tree: ast.AST) -> tuple[str, str]:
    """Walk the module AST for the first build_body(<Model>, ...) and
    call_api(..., <method>, ...) pair inside read_resource."""
    model = method = None
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", None)
        if name == "build_body" and node.args:
            arg = node.args[0]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                model = model or arg.value
        elif name == "call_api" and len(node.args) >= 3:
            arg = node.args[2]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                method = method or arg.value
    if not model or not method:
        raise ValueError(f"could not extract sdk_call (model={model!r}, method={method!r})")
    return model, method


def _rewrite(path: Path) -> bool:
    src = path.read_text()
    if "run_info_module" in src:
        return False  # already collapsed
    tree = ast.parse(src)
    spec_literal = _argspec_block(src)
    model, method = _extract_sdk_call(tree)

    # Preserve everything above the imports (shebang, encoding, copyright,
    # __future__, DOCUMENTATION, EXAMPLES, RETURN). Split at the first
    # "from ansible" import.
    head_match = re.search(r"^from ansible(?:\.|_)", src, flags=re.MULTILINE)
    if not head_match:
        raise ValueError("no 'from ansible...' import found to split header")
    head = src[:head_match.start()].rstrip() + "\n\n"

    body = (
        f"{HELPER_IMPORT}\n\n"
        f"{spec_literal}\n\n\n"
        "def main():\n"
        f"    run_info_module(\n"
        f"        argument_spec=argument_spec,\n"
        f"        sdk_call=({model!r}, {method!r}),\n"
        "    )\n\n\n"
        "if __name__ == '__main__':\n"
        "    main()\n"
    )

    new = head + body
    path.write_text(new)
    return True


def main() -> int:
    info_modules = sorted(MODULES.glob("*_info.py"))
    refactored = []
    skipped = []
    failed = []
    for p in info_modules:
        try:
            if _rewrite(p):
                refactored.append(p.name)
            else:
                skipped.append(p.name)
        except Exception as e:  # noqa: BLE001 -- diagnostic codemod
            failed.append((p.name, repr(e)))

    print(f"refactored: {len(refactored)}")
    for n in refactored:
        print(f"  + {n}")
    print(f"skipped (already on helper): {len(skipped)}")
    for n in skipped:
        print(f"  = {n}")
    if failed:
        print(f"FAILED: {len(failed)}")
        for n, err in failed:
            print(f"  ! {n}: {err}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
