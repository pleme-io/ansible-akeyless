# Live-only examples

These playbooks need a real Akeyless gateway + credentials (not a mock):
- they read state created by previous tasks (which mocks return as generic
  blobs, not real shape),
- they reference filesystem inputs (CSRs, key files), or
- they exercise modules whose argspec is currently mid-regen and doesn't
  match the upstream OpenAPI shape they use.

The integration-live CI test runs `examples/*.yml` against a mock gateway,
so anything here is *intentionally* excluded from that smoke pass.

When you have a real Akeyless gateway + credentials wired in CI (`AKEYLESS_ACCESS_ID`,
`AKEYLESS_ACCESS_KEY`, `AKEYLESS_GATEWAY_URL`), run these locally to verify.
