<!--
Thanks for the contribution! A few quick prompts to help reviewers.
Delete sections that don't apply.
-->

## Summary

<!-- 1–3 sentences: what does this PR change and why? -->

## Related issue

<!-- "Closes #123" or "Refs #123" — leave blank if standalone -->

## Type of change

- [ ] Bug fix (non-breaking; existing behaviour preserved)
- [ ] New feature / module
- [ ] Docs / examples
- [ ] Test / CI
- [ ] Chore (build, deps, refactor with no behaviour change)
- [ ] Breaking change (please justify in Summary)

## Where the change belongs

This collection is auto-generated. Most changes belong elsewhere:

- [ ] My change is in `tests/`, `examples/`, `README.md`, or other hand-maintained files (PR fine here)
- [ ] My change adds or fixes a module → it belongs in [`akeyless-terraform-resources`](https://github.com/pleme-io/akeyless-terraform-resources) (the TOML spec source)
- [ ] My change fixes how modules are emitted → it belongs in [`ansible-forge`](https://github.com/pleme-io/ansible-forge) (the emitter)

If you're not sure, leave a note and a maintainer will route it.

## Checklist

- [ ] `python3 tests/sanity/smoke.py` passes locally
- [ ] `pytest tests/unit/` passes locally
- [ ] Added or updated tests covering the change
- [ ] Updated `CHANGELOG.md` under `[Unreleased]` if user-visible
- [ ] No credentials, tokens, or other secrets in the diff
