# Copyright: (c) 2026, pleme-io
# MIT License
#
# Every plugins/modules/*.py must carry the same GPL-3.0+ header at
# the top of the file. Ansible modules in the official ecosystem are
# conventionally GPL3 (the modules run inside the GPL3 ansible-core
# process at runtime); a mix of MIT / GPL3 headers in a collection is
# a sanity-test fail downstream that doesn't surface until release.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
MODULES_DIR = REPO_ROOT / "plugins" / "modules"

MODULE_PATHS = sorted(p for p in MODULES_DIR.glob("*.py") if not p.name.startswith("_"))

EXPECTED_HEADER_LINES = [
    "#!/usr/bin/python",
    "# -*- coding: utf-8 -*-",
    "",
    "# Copyright: (c) 2026, pleme-io",
    "# GNU General Public License v3.0+ "
    "(see LICENSES/GPL-3.0-or-later.txt or "
    "https://www.gnu.org/licenses/gpl-3.0.txt)",
]


@pytest.mark.parametrize("module_path", MODULE_PATHS, ids=lambda p: p.name)
def test_module_has_shebang_and_encoding(module_path):
    """Ansible's validate-modules sanity check requires both lines
    verbatim. Without them, `ansible-test sanity` fails the module."""
    lines = module_path.read_text().splitlines()
    assert len(lines) >= 2, f"{module_path.name}: file too short for header"
    assert lines[0] == "#!/usr/bin/python", (
        f"{module_path.name}: line 1 must be `#!/usr/bin/python`, got {lines[0]!r}"
    )
    assert lines[1] == "# -*- coding: utf-8 -*-", (
        f"{module_path.name}: line 2 must be `# -*- coding: utf-8 -*-`, got {lines[1]!r}"
    )


@pytest.mark.parametrize("module_path", MODULE_PATHS, ids=lambda p: p.name)
def test_module_has_gpl3_license_header(module_path):
    """All Ansible modules in this collection carry GPL-3.0-or-later
    licensing (matching ansible-core's runtime license). A mix of
    licenses is a sanity-test fail."""
    text = module_path.read_text()
    gpl_line = (
        "# GNU General Public License v3.0+ "
        "(see LICENSES/GPL-3.0-or-later.txt or "
        "https://www.gnu.org/licenses/gpl-3.0.txt)"
    )
    assert gpl_line in text, (
        f"{module_path.name}: missing GPL-3.0+ header line. "
        f"Every module must declare GPL-3.0+ to match ansible-core's runtime license."
    )
    # No accidental MIT carry-over.
    assert "# MIT License" not in text, (
        f"{module_path.name}: contains a `# MIT License` header line; "
        f"modules must be GPL-3.0+ exclusively."
    )


@pytest.mark.parametrize("module_path", MODULE_PATHS, ids=lambda p: p.name)
def test_module_has_metaclass_directive(module_path):
    """validate-modules requires `__metaclass__ = type` for legacy
    Python-2-compat hygiene. Even on modern Ansible (3.10+), the
    sanity check still verifies its presence."""
    text = module_path.read_text()
    assert "__metaclass__ = type" in text, (
        f"{module_path.name}: missing `__metaclass__ = type` declaration"
    )
    assert "from __future__ import absolute_import, division, print_function" in text, (
        f"{module_path.name}: missing standard `from __future__` import"
    )
