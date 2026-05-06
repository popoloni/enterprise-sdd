# CLI Deprecations Catalog (Wave 20 §20.C.8)

> **Policy reference:** [`.github/instructions/cli-deprecation-policy.instructions.md`](.github/instructions/cli-deprecation-policy.instructions.md)
>
> Every deprecated CLI surface element (flag, sub-command, environment variable)
> MUST appear in the **Active** table below before merging. When the removal
> version is reached, the entry moves to the **Removed** table.
>
> The `@deprecated` decorator in `sdd.utils.deprecation` reads from this catalog
> at runtime to emit structured warnings; `sdd doctor` (Wave 20 §20.C.10) scans
> committed scripts and config for entries in the **Active** table.

---

## Active Deprecations

| ID | Flag / Sub-command / Env Var | Deprecated In | Removal Version | Replacement | Migration Link |
|----|------------------------------|:-------------:|:---------------:|-------------|----------------|
| _(seed)_ `skill-validate--legacy-mode` | `sdd skill validate --legacy-mode` | 0.5.0 | 0.7.0 | `sdd skill validate --eval` (Wave 20 §20.B.2) | [#skill-validate--legacy-mode](#skill-validate--legacy-mode) |

> The single seed entry above is illustrative — `--legacy-mode` is a sentinel
> flag carried in the catalog so the deprecation tooling has a worked example.
> The flag is not exposed by the parser; it exists only to validate the doctor
> scan and the `@deprecated` decorator emission path.

### Active Migration Notes

#### skill-validate--legacy-mode

Replaced by the Wave 20 behavioral evaluation harness:

```bash
# Old (deprecated, emits warning):
sdd skill validate <skill-id> --legacy-mode

# New:
sdd skill validate <skill-id> --eval
```

The new `--eval` flag reads `<skill-dir>/.sdd-eval.yaml` and writes a
structured `SKILL-EVAL-REPORT.md`. See PLAYBOOK §"Lifecycle Coverage Extensions".

---

## Removed Deprecations

| ID | Flag / Sub-command / Env Var | Removed In | Date | Final Replacement |
|----|------------------------------|:----------:|:----:|-------------------|
| _(none yet)_ | — | — | — | — |

---

## Maintenance Checklist

When adding a new deprecation:

- [ ] Catalog entry added to **Active** with all five columns populated
- [ ] Migration note appended under **Active Migration Notes** with anchor id
- [ ] Parser hook decorated with `@deprecated(...)` from `sdd.utils.deprecation`
- [ ] PLAYBOOK section that documents the old flag references the new one
- [ ] Test case added in `_tests/test_framework_integrity.py` or
      `_tests/test_cli_unit.py` asserting the warning is emitted

When removing a deprecation:

- [ ] Entry moved to **Removed** with date and final-replacement column
- [ ] Parser hook removed; `@deprecated(...)` decorator removed
- [ ] PLAYBOOK references purged
- [ ] CHANGELOG records the removal under the wave that delivered it
