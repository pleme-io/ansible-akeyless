#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, pleme-io
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Jinja2 filters for transforming Akeyless secret payloads.

Filters are registered via FilterModule and addressed as
`{{ value | drzln0.akeyless.<filter_name> }}` in playbooks.
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import base64
import json
from typing import Any, Dict, List, Optional, Tuple

from ansible.errors import AnsibleFilterError


def b64decode_secret(value: str) -> str:
    """Base64-decode a string secret value. Akeyless returns binary
    blobs (keys, certs, .pfx contents) as base64-encoded strings;
    this filter unwraps them to bytes-as-text.

    Raises AnsibleFilterError on invalid base64 input rather than
    silently returning garbage.

    Usage:
        cert_pem: "{{ lookup('drzln0.akeyless.secret', '/certs/app') | drzln0.akeyless.b64decode_secret }}"
    """
    if not isinstance(value, str):
        raise AnsibleFilterError(
            f"b64decode_secret expects a string, got {type(value).__name__}"
        )
    try:
        # validate=True rejects non-base64 alphabet chars rather than
        # silently stripping them (Python's default behavior). For a
        # secret-handling filter the strict failure is the safe default.
        return base64.b64decode(value, validate=True).decode("utf-8")
    except (ValueError, UnicodeDecodeError, base64.binascii.Error) as exc:
        raise AnsibleFilterError(
            f"b64decode_secret failed: {exc}"
        ) from exc


def parse_dotenv_secret(value: str) -> Dict[str, str]:
    """Parse a dotenv-formatted secret value into a {key: value} dict.

    Akeyless secrets commonly store env-file content as a single blob
    so applications can `source /tmp/x.env`. This filter parses it
    into a dict for direct use in Ansible `environment:` blocks or
    template variables.

    Accepts:
      KEY=value
      export KEY=value   (the `export` prefix is stripped)
      KEY="quoted value" (quotes stripped)
      KEY='single quoted' (quotes stripped)
    Skips:
      - Blank lines
      - Lines starting with `#` (comments)

    Raises AnsibleFilterError on lines that don't match KEY=value.

    Usage:
        environment: "{{ lookup('drzln0.akeyless.secret', '/app/.env') | drzln0.akeyless.parse_dotenv_secret }}"
    """
    if not isinstance(value, str):
        raise AnsibleFilterError(
            f"parse_dotenv_secret expects a string, got {type(value).__name__}"
        )
    out: Dict[str, str] = {}
    for lineno, raw in enumerate(value.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if "=" not in line:
            raise AnsibleFilterError(
                f"parse_dotenv_secret: line {lineno} has no '=' separator: {raw!r}"
            )
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip()
        # Strip matching surrounding quotes.
        if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
            val = val[1:-1]
        out[key] = val
    return out


def secret_to_json(value: str) -> Any:
    """Parse a secret value as JSON. Akeyless stores complex structures
    (auth configs, KV maps, embedded certs) as JSON strings;
    callers want them as native dicts/lists in Ansible. Wraps
    json.loads with a clearer error message than the default
    JSONDecodeError stack.

    Usage:
        config: "{{ lookup('drzln0.akeyless.secret', '/app/config') | drzln0.akeyless.secret_to_json }}"
    """
    if not isinstance(value, str):
        raise AnsibleFilterError(
            f"secret_to_json expects a string, got {type(value).__name__}"
        )
    try:
        return json.loads(value)
    except (TypeError, ValueError) as exc:
        # Include a small leading slice of the value to help the user
        # diagnose what went wrong without dumping a potentially-large
        # secret to the log.
        preview = value[:60] + ("..." if len(value) > 60 else "")
        raise AnsibleFilterError(
            f"secret_to_json failed to parse: {exc}; value starts with {preview!r}"
        ) from exc


def split_pem_bundle(value: str) -> List[str]:
    """Split a multi-cert PEM bundle into a list of individual PEM
    blocks. Useful for processing CA bundles where each cert needs
    to be installed to a separate file (e.g. systemd-style
    /etc/ssl/certs/<hash>.0 layout).

    Returns each PEM block including its -----BEGIN/END----- markers.
    Skips blank lines + content outside of begin/end markers.

    Usage:
        ca_certs: "{{ lookup('drzln0.akeyless.secret', '/ca/bundle') | drzln0.akeyless.split_pem_bundle }}"
    """
    if not isinstance(value, str):
        raise AnsibleFilterError(
            f"split_pem_bundle expects a string, got {type(value).__name__}"
        )
    blocks: List[str] = []
    current: List[str] = []
    in_block = False
    for line in value.splitlines():
        stripped = line.strip()
        if stripped.startswith("-----BEGIN "):
            in_block = True
            current = [line]
        elif stripped.startswith("-----END "):
            if not in_block:
                raise AnsibleFilterError(
                    "split_pem_bundle: -----END marker outside an open block"
                )
            current.append(line)
            blocks.append("\n".join(current))
            current = []
            in_block = False
        elif in_block:
            current.append(line)
        # Outside-block lines (whitespace, comments) silently skipped.
    if in_block:
        raise AnsibleFilterError(
            "split_pem_bundle: unterminated -----BEGIN block at end of input"
        )
    return blocks


def secret_keys_to_env(value: Dict[str, Any], prefix: str = "") -> Dict[str, str]:
    """Convert a {key: value} dict (e.g. from secret_to_json) into the
    UPPER_SNAKE_CASE env-var shape Ansible's `environment:` block
    expects. Optionally prefixes every key.

    Usage:
        environment: "{{ config_dict | drzln0.akeyless.secret_keys_to_env(prefix='APP_') }}"
    """
    if not isinstance(value, dict):
        raise AnsibleFilterError(
            f"secret_keys_to_env expects a dict, got {type(value).__name__}"
        )
    if not isinstance(prefix, str):
        raise AnsibleFilterError(
            f"secret_keys_to_env prefix must be a string, got {type(prefix).__name__}"
        )
    out: Dict[str, str] = {}
    for k, v in value.items():
        env_key = (prefix + str(k)).upper().replace("-", "_").replace(".", "_")
        out[env_key] = str(v) if not isinstance(v, str) else v
    return out


def mask_secret(value: str, show_first: int = 4, show_last: int = 0,
                mask_char: str = "*") -> str:
    """Partial-reveal mask for log-safe secret display. Shows the first
    `show_first` chars + last `show_last` chars, replacing the middle
    with a fixed-length block of `mask_char`.

    Defaults (show_first=4, show_last=0) mirror the common "p-abcd***"
    shape that surfaces enough of the value to recognize it without
    leaking the whole thing.

    Usage:
        - debug:
            msg: "Auth ID: {{ access_id | drzln0.akeyless.mask_secret }}"
        - debug:
            msg: "Token: {{ tok | drzln0.akeyless.mask_secret(show_first=6, show_last=4) }}"
    """
    if not isinstance(value, str):
        raise AnsibleFilterError(
            f"mask_secret expects a string, got {type(value).__name__}"
        )
    if not isinstance(show_first, int) or not isinstance(show_last, int):
        raise AnsibleFilterError("mask_secret show_first/show_last must be ints")
    if show_first < 0 or show_last < 0:
        raise AnsibleFilterError("mask_secret show_first/show_last must be >= 0")
    if not isinstance(mask_char, str) or len(mask_char) != 1:
        raise AnsibleFilterError(
            f"mask_secret mask_char must be a single character, got {mask_char!r}"
        )
    # When reveal windows overlap the entire value (e.g. show_first +
    # show_last >= len(value)), fall back to a fully-masked result so
    # we never leak the entire secret. Returning a short fixed-length
    # mask of `*` is safer than echoing the original.
    if show_first + show_last >= len(value):
        return mask_char * 8
    head = value[:show_first]
    tail = value[-show_last:] if show_last else ""
    return f"{head}{mask_char * 8}{tail}"


def secret_strength(value: str) -> Dict[str, Any]:
    """Compute a Shannon-entropy + heuristic strength score for a
    secret string. Returns `{length, entropy_bits, classification}`
    where classification is one of "weak"/"moderate"/"strong"/"vault".

    The entropy estimate is Shannon over the character distribution,
    multiplied by length to approximate total bits. Cutoffs:
      - < 40 bits   -> weak (passwords, dictionary words)
      - 40-80 bits  -> moderate (short random strings)
      - 80-128 bits -> strong (medium random strings, tokens)
      - >= 128 bits -> vault (full-entropy keys)

    Usage:
        - assert:
            that:
              - (rotated_password | drzln0.akeyless.secret_strength).classification != 'weak'
    """
    import math
    from collections import Counter

    if not isinstance(value, str):
        raise AnsibleFilterError(
            f"secret_strength expects a string, got {type(value).__name__}"
        )
    length = len(value)
    if length == 0:
        return {"length": 0, "entropy_bits": 0.0, "classification": "weak"}

    # Shannon entropy per char: H = -sum(p * log2(p))
    counts = Counter(value)
    char_entropy = -sum(
        (c / length) * math.log2(c / length) for c in counts.values()
    )
    total_bits = char_entropy * length

    if total_bits < 40:
        classification = "weak"
    elif total_bits < 80:
        classification = "moderate"
    elif total_bits < 128:
        classification = "strong"
    else:
        classification = "vault"

    return {
        "length": length,
        "entropy_bits": round(total_bits, 2),
        "classification": classification,
    }


class FilterModule:
    """Register the akeyless filters with Ansible's filter registry."""

    def filters(self) -> Dict[str, Any]:
        return {
            "b64decode_secret": b64decode_secret,
            "parse_dotenv_secret": parse_dotenv_secret,
            "secret_to_json": secret_to_json,
            "split_pem_bundle": split_pem_bundle,
            "secret_keys_to_env": secret_keys_to_env,
            "mask_secret": mask_secret,
            "secret_strength": secret_strength,
        }
