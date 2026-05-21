# Examples

Runnable playbooks demonstrating the collection. Each one is self-contained — set `AKEYLESS_ACCESS_ID` + `AKEYLESS_ACCESS_KEY` in your environment and run with `ansible-playbook <file>.yml`.

| File | Demonstrates |
|---|---|
| [`static_secret.yml`](static_secret.yml) | Full CRUD lifecycle of a static secret. |
| [`dynamic_secret_aws.yml`](dynamic_secret_aws.yml) | Provision an AWS dynamic-secret producer + issue short-lived credentials. |
| [`role_and_auth_method.yml`](role_and_auth_method.yml) | Create an API-key auth method, a role, associate them, attach rules. |
| [`uid_token_lifecycle.yml`](uid_token_lifecycle.yml) | Universal Identity auth method + generate / rotate / revoke tokens (PRM-1790). |
| [`certificate_provision.yml`](certificate_provision.yml) | Issue a certificate via the PKI cert-issuer action module. |
| [`rotated_secret_with_target.yml`](rotated_secret_with_target.yml) | Wire a target to a rotated secret + trigger a manual rotation. |
| [`check_mode_demo.yml`](check_mode_demo.yml) | Use `--check` for a non-destructive diff before applying. |

## Running

```bash
export AKEYLESS_ACCESS_ID='p-xxxxxxxxxxxx'
export AKEYLESS_ACCESS_KEY='your-access-key-base64=='

ansible-playbook examples/static_secret.yml
```

These playbooks use the access-key auth path. To use a different auth method (k8s / aws_iam / azure_ad / oidc / etc.), set `access_type` accordingly on each task (or globally via `vars`). See the [main README](../README.md#authentication-options) for the full list.
