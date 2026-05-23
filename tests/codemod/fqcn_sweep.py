#!/usr/bin/env python3
"""One-shot codemod: rewrite bare module references in every
tests/integration/targets/*/tasks/main.yml into the full
drzln0.akeyless.<name>: FQCN form.

The bare form (`role:`, `static_secret:`, ...) works via collection-
path autoloading in most install modes but breaks under others (e.g.
when the collection isn't on the search path explicitly, or when a
playbook is invoked from outside an ansible-galaxy-installed location).
FQCN everywhere is the Ansible-recommended modern shape.

Each target directory's name matches the module it tests, so the
rewrite is mechanical: any task body line `  <module_name>:` (where
<module_name> matches the target's directory name) becomes
`  drzln0.akeyless.<module_name>:`.

Skip-safe: lines already on FQCN form are left untouched.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGETS = ROOT / "tests" / "integration" / "targets"


def rewrite_one(target_dir: Path) -> int:
    """Rewrite one target's tasks/main.yml. Returns the number of
    line-level changes made."""
    module_name = target_dir.name
    tasks_file = target_dir / "tasks" / "main.yml"
    if not tasks_file.exists():
        return 0

    text = tasks_file.read_text()
    new_text = text
    changes = 0

    # Pattern: leading whitespace + `<module_name>:` at end of line,
    # NOT preceded by `drzln0.akeyless.` already.
    # Matches the YAML task-module dispatch line.
    pattern = re.compile(
        rf"^(\s+)(?<!drzln0\.akeyless\.){re.escape(module_name)}:\s*$",
        flags=re.MULTILINE,
    )
    # Replace bare form with FQCN.
    def _sub(match):
        nonlocal changes
        changes += 1
        return f"{match.group(1)}drzln0.akeyless.{module_name}:"
    new_text = pattern.sub(_sub, new_text)

    if changes:
        tasks_file.write_text(new_text)
    return changes


def main() -> int:
    if not TARGETS.is_dir():
        print(f"ERROR: {TARGETS} not found", file=sys.stderr)
        return 1

    target_dirs = sorted(d for d in TARGETS.iterdir() if d.is_dir())
    total_changes = 0
    rewritten = 0
    for d in target_dirs:
        n = rewrite_one(d)
        if n:
            rewritten += 1
            total_changes += n
            print(f"  + {d.name}: {n} task(s) rewritten")
    print(f"\n[done] {rewritten}/{len(target_dirs)} targets touched; "
          f"{total_changes} task(s) rewritten to FQCN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
