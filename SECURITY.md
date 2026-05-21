# Security Policy

## Reporting a vulnerability

**Do not open public issues for security bugs.**

Use GitHub's [Private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability) on this repository — the "Security" tab → "Report a vulnerability".

If that's not available to you, email `security@pleme.io` <!-- TODO: replace with real address before launch --> with:

- A description of the issue
- Affected versions
- Reproduction steps
- Suggested fix (optional)

## Response targets

| Step | Target |
|---|---|
| Acknowledgement | 5 business days |
| Triage + severity assessment | 10 business days |
| Coordinated disclosure window | 90 days from acknowledgement |

We will keep you informed of progress and credit you in the release notes unless you request otherwise.

## Scope

In scope:

- The generated Ansible modules in `plugins/modules/`
- The shared module helper at `plugins/module_utils/akeyless_client.py`
- The collection's metadata and packaging (`galaxy.yml`, `meta/runtime.yml`)
- The test suite and CI workflows

Out of scope (report upstream):

- The Akeyless API itself → [Akeyless support](https://www.akeyless.io/contact-us/)
- The `akeyless` Python SDK → [`pleme-io/akeyless-python`](https://github.com/pleme-io/akeyless-python) (re-publish of the upstream openapi-generator output)
- The TOML resource specs → [`pleme-io/akeyless-terraform-resources`](https://github.com/pleme-io/akeyless-terraform-resources)

## Supported versions

| Version | Status |
|---|---|
| `0.2.x` | Active |
| `< 0.2` | Unsupported (pre-baseline; do not use) |

Security fixes land in the next patch release on the current minor line.
