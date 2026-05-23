# Skip per-task auth — the `akeyless_token` cache plugin

By default every Akeyless task in a playbook costs one auth
round-trip to your gateway. The `akeyless_token` cache plugin
turns that into one auth round-trip PER PLAYBOOK (or whatever
TTL you set), file-backed with `0600` perms.

## When to use it

- Your playbook makes more than ~5 Akeyless calls and you want to
  cut the auth overhead.
- You're running playbooks at scale (many hosts, many runs per hour)
  and the gateway is the bottleneck.
- You're running in CI / AWX / AAP where re-auth on every call adds
  noticeable latency.

## Setup — `ansible.cfg`

```ini
[defaults]
fact_caching = drzln0.akeyless.akeyless_token
fact_caching_connection = /var/cache/ansible/akeyless
fact_caching_timeout = 1500
```

What each option means:
- `fact_caching` → activates the plugin.
- `fact_caching_connection` → directory where the JSON cache files
  live (created lazily, `0600`-perm-protected).
- `fact_caching_timeout` → TTL in seconds. Default `1500` (25
  minutes), which leaves ~35 minutes of headroom on Akeyless's
  typical 60-minute token lifetime.

## What the cache holds

One JSON file per `(gateway_url, access_id)` tuple. The file holds:

```json
{
  "token": "t-abc123def456...",
  "obtained_at": 1716489000,
  "expires_at": 1716492600
}
```

The plugin handles:
- Atomic writes (`tmpfile + rename`) so a partial write never
  corrupts the cache.
- TTL expiry (file mtime + `fact_caching_timeout`).
- Self-healing — a corrupt JSON file is silently deleted on next
  read, and the next call re-auths.
- Per-tenant keying so different Akeyless tenants / access IDs don't
  collide.

## Where the directory should live

| Environment | Suggested path |
|---|---|
| Bare metal / VM | `/var/cache/ansible/akeyless` |
| Local dev / laptop | `~/.cache/ansible/akeyless` |
| Container (e.g. ee-builder, AWX EE) | `/runner/cache/akeyless` |
| CI runner | `${RUNNER_TEMP}/akeyless-cache` (per-job, ephemeral) |

In every case, the directory should be writable by the user running
ansible AND not world-readable.

## Verifying it's wired up

After a playbook run:

```bash
$ ls -la /var/cache/ansible/akeyless/
-rw-------  1 me  me  192 May 23 04:00 akeyless_token_p_abc123_https_api_akeyless_io.json
```

If the file exists and the mtime is recent, the cache is in use. If
the next playbook run completes faster, you've saved an auth call.

## Forcing a re-auth

Delete the cache file (or set `fact_caching_timeout` to 0 in
`ansible.cfg` for one-off scripts). The plugin's `flush()` method
is also exposed if you want to clear all cached tokens
programmatically.

## What it does NOT cache

- Individual secret values (the lookup is for secret fetches; the
  cache is for AUTH tokens only).
- Dynamic secret credentials (those are intentionally fresh per
  call — that's the whole point of dynamic secrets).
- Per-resource metadata (modules' read-then-decide-write path
  always queries Akeyless for the current state).

The cache is JUST for the auth token. Everything else still goes
through the gateway each call.

## Composing with `module_defaults`

The cache plugin runs transparently underneath
`module_defaults: group/drzln0.akeyless.all:`. Set both in the same
`ansible.cfg` + playbook and every task gets BOTH the inherited auth
config AND the cached token.
