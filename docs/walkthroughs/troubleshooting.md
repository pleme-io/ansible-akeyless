# Troubleshooting

The most common errors users hit, with the exact fix for each.

## Authentication failures

### `Akeyless auth failed (401): InvalidAccessId`

The `access_id` doesn't exist in the configured tenant.

Check:
- The env var name: `AKEYLESS_ACCESS_ID` (not `AKEYLESS_ID`).
- That the access ID starts with `p-` (most Akeyless auth methods
  emit `p-`-prefixed IDs).
- That you're hitting the right gateway: a saas access ID won't
  authenticate against a self-hosted gateway and vice-versa. Pin
  `gateway_url` if you're not on `https://api.akeyless.io`.

### `Akeyless auth failed (403): InvalidCredentials`

The `access_id` is correct but the `access_key` is wrong (or
expired).

Check:
- Quote your access_key on the CLI:
  ```bash
  AKEYLESS_ACCESS_KEY='your-key-with-special-chars==' \
    ansible-playbook ...
  ```
  Unquoted `=` / `$` / `\` in shells can mangle the value.
- The key hasn't been rotated. Akeyless lets you list keys via the
  console — confirm the one you're using is still active.

### `access_id is required when no pre-issued token is provided`

You set neither `token` nor `access_id`. The collection raises
this BEFORE any HTTP call so you fail fast.

Fix: set `AKEYLESS_ACCESS_ID` (or `access_id:` on the task) AND
the matching `access_key`. See
[Authentication reference](../reference/authentication.md).

## Lookup-specific issues

### `Secret '/x' not found in Akeyless response`

The lookup fetched the response successfully but the requested
path isn't in it. Causes:

- **Typo in the path**: `/app/db/password` vs `/app/db/passwd`.
- **Permission missing**: the access_id can authenticate but
  doesn't have read permission on this specific path. Check the
  role bindings in the Akeyless console.
- **Deleted secret**: the secret was deleted but is still
  referenced in a playbook.

### `Unexpected get_secret_value response type: list`

Akeyless returned something the lookup can't reshape. Usually
means the path resolves to a folder, not a secret. Akeyless paths
are flat — there's no recursive listing via the secret lookup.

Fix: list children with `drzln0.akeyless.items_list_info` first to
confirm the path resolves to an item, not a folder.

## Module-specific issues

### `Unknown args for drzln0.akeyless.secret_to_file: ['owener']`

You misspelt an arg (`owener` instead of `owner`). The action
plugin validates against a fixed allow-list and rejects unknown
keys to catch typos.

Fix: check the spelling against the
[secret_to_file walkthrough](secret-to-file.md).

### `<module>: argument_spec is missing required OpenAPI schema fields`

The module's argspec doesn't carry every field the upstream
OpenAPI spec marks as required. This is a generator bug — file an
issue against
[ansible-forge](https://github.com/pleme-io/ansible-forge/issues).

Workaround: the field is likely accepted as an extra kwarg
anyway; pass it via `argspec.<name>:` and the SDK call will
include it. Add a note to your own playbook explaining the
workaround.

## docs-lint issues

### `Did not return correct DOCUMENTATION`

The DOCUMENTATION YAML in the module/plugin file has a structural
issue antsibull-docs rejects. Common shapes:

- **Empty `options:`**: `options:` followed by no body parses as
  `None`. Use `options: {}` for genuinely empty.
- **`no_log: true` under options**: not a valid documentation key
  (it belongs in the argspec dict). Strip from DOCUMENTATION YAML.
- **Unquoted colon in description**: a multi-line description with
  `:`-followed-by-space gets parsed as a mapping. Quote the value:
  ```yaml
  description: "Set the TTL: defaults to 1 hour"
  ```
- **Markdown-style links**: `[text](url)` is a markdown link;
  rstcheck warns. Use plain text or RST-style links.

## Performance issues

### "Every task takes 0.5s on auth"

Wire the [token caching plugin](token-caching.md). With it, the
auth round-trip happens once per playbook (per gateway/access_id)
and downstream tasks reuse the cached token. For a 100-task
playbook that's a savings of ~49 seconds per run.

### "Inventory plugin runs slowly"

Each `secrets:` entry triggers ONE round-trip. For large
inventories, batch into one JSON secret rather than many small
ones — the underlying `get_secret_value` API supports multi-secret
batch reads.

## Debugging

### Show what auth options the helper resolved

Run with `-vvv`. The collection's helper logs (at debug level) the
gateway_url, access_type, and whether a pre-issued token was used.
The access_key value is never logged (masked at the source).

### Verify the gateway from the controller

```bash
curl -fsS "$AKEYLESS_GATEWAY_URL/v2/info"
```

Should return JSON. If it hangs or 5xx-errors, the gateway is
unreachable from your controller — fix network / proxy / DNS
before debugging the playbook.

### Reproduce a module's behaviour locally

Every generated module is a self-contained Python file. To trace
what's happening on a specific module:

```bash
ANSIBLE_AKEYLESS_DEBUG=1 \
  ansible-playbook -vvv -i localhost, playbook.yml
```

The `-vvv` flag shows the resolved task args, the SDK call name,
and any ApiException stack with `from exc` chain preserved.

## When to file an issue

[github.com/pleme-io/ansible-akeyless/issues](https://github.com/pleme-io/ansible-akeyless/issues)

Include:
- The collection version (`ansible-galaxy collection list drzln0.akeyless`)
- The Akeyless SDK version (`pip show akeyless`)
- The ansible-core version
- The playbook snippet that fails
- The `-vvv` output (redact the access_id/key)

Generator bugs (typos in module names, missing fields in argspec)
go upstream to
[ansible-forge issues](https://github.com/pleme-io/ansible-forge/issues).
