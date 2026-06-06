# Changelog — Enterprise SDD Workflow

> **Last updated:** June 6, 2026
> **Scope:** Full delivery history from initial implementation through Wave 27 (complete).
> **Source documents:** All entries are traced to planning, completion, and validation documents in [`_plan/`](_plan/).

---

## Wave 27 — Multi-Framework Public Refresh Harvest (June 6, 2026)

> **Status:** ✅ Complete (Phases A/B/C/T/V/Z all delivered — 724 passed)
> **Plan:** [`_plan/WAVE-27-PUBLIC-REFRESH-JUN06-IMPLEMENTATION-PLAN.md`](_plan/WAVE-27-PUBLIC-REFRESH-JUN06-IMPLEMENTATION-PLAN.md)
> **Source:** June 6, 2026 multi-framework public-refresh harvest (§26) — 8 additive features from GSD-2 v3.0.0, APM v0.18.0, BMAD v6.8.0, AI-RPI v1.2.0, Spec Kit v0.10.0, OpenSpec v1.4.1, grouped into three coherent sub-tracks.

### Phase A — Provenance & Integrity (✅ Complete — 15 tasks)

- **§26 #1 — Derived dedup memory index (strangler-fig, ≤ 5 append-only PRs).** Added `memory-index.schema.json` and `sdd.utils.memory_index` builder producing a disposable `.specify/memory/.index.json` (one entry per decision/lesson with `id`, `source_file`, `source_anchor`, `kind`, `fingerprint` (sha256, reuse §23 #3), `last_referenced_at`/`reference_count` (reuse §23 #4), `duplicate_of`). Markdown stays canonical (Constraint #9). `sdd memory index` builds it, `sdd doctor` rebuilds/validates it (proves the disposable guarantee: delete → rebuild → identical), `sdd memory list --duplicates` surfaces collisions for human merge, and `sdd bridge` consumes the index to dedupe selection (authoritative record = highest `reference_count`, then most recent) with `--explain` annotation. `.index.json` is gitignored. Staging recorded in [`_plan/WAVE-27-MEMORY-INDEX-STRANGLER-LOG.md`](_plan/WAVE-27-MEMORY-INDEX-STRANGLER-LOG.md).
- **§26 #2 — Reverse-traceability lookup.** Added `sdd trace --reverse <path>` (`sdd.utils.traceability`) that inverts the forward US→AC→TC→Task→Code chain into a `path → {task, AC, US, spec}` answer (exit `0` on a tracked path, `1` on an untracked path), `--json` conforming to the Wave 26 §B.8 `cli-output.schema.json` envelope, and `sdd analyze --provenance` for bulk untraced-file listing (the reverse complement of `--gaps`).
- **§26 #3 — Unmanaged-artifact audit.** Added `sdd doctor --registry-audit` flagging on-disk skills/modules/extensions with no `.sdd-modules/registry.json` entry as UNMANAGED, `--strict` for fail-closed CI emitting SARIF rule `sdd-unmanaged-artifact`, and `sdd module adopt <path>` / `sdd skill adopt <path>` to register an artifact (hash + Unicode scan + policy-compliance) after review.

### Phase B — Intake & Discipline (✅ Complete — 7 tasks)

- **§26 #4 — Intent-distillation kernel.** Created `.github/skills/intent-kernel/SKILL.md` (≤ 80 lines) producing a 5-field kernel (Problem, Capabilities, Constraints, Non-goals, Success signal) plus a `sources:` provenance list, routed under the `sdd-specify` namespace meta-skill. Added `sdd new --from-brief <file>` to seed the Phase 1 spec from a raw brief without bypassing the spec/Gate 1. The kernel is explicitly subordinate to the formal spec (Constraint #4) — `sdd doctor` never accepts a kernel in place of a spec.
- **§26 #5 — Ordered activation guardrail.** Created `agent-activation-discipline.instructions.md` (≤ 50 lines, `applyTo: .github/agents/**`) requiring ordered `mandatory-startup-files` reads, no inference of startup-file values, and a one-line confirmation per step. Added `sdd doctor --activation-discipline` asserting every agent frontmatter declares an ordered startup block, cross-referenced from the agent-design instruction index.

### Phase C — Module & Lifecycle (✅ Complete — 10 tasks)

- **§26 #6 — FE design→engineering file contract.** Created `design-tokens-template.md` (DESIGN spine — named visual tokens) and `experience-template.md` (EXPERIENCE spine — flows/states/IA/a11y) scoped strictly to `std-fe`/`aws-fe` (Constraint #8), with `{design-tokens.TOKEN}` reference syntax and an `experience` ↔ `design` reference-integrity WARN in the FE extension diagnostics (`sdd extension doctor`). Documented in `PLAYBOOK-std-fe.md` and `PLAYBOOK-aws-fe.md`.
- **§26 #7 — Task-granular verification handoff.** Added an opt-in per-task verification checkpoint to `software-engineer.agent.md` reusing the Wave 13 verdict schema (`passed/retry/blocked` + `confidence` + `repair_hint`) — **no new agent, no loop** (Constraint #9 + §22 governed-outer-loop rejection). Gated behind ceremony level (`full`) in `ceremony-levels.instructions.md` and documented in PLAYBOOK § Phase 4.
- **§26 #8 — Deprecation-gate auto-migration.** Extended `sdd init --upgrade` with an auto-migration pass over `CLI-DEPRECATIONS.md` for past-gate entries, `--preview` dry-run printing the plan and writing a per-change audit log (`.specify/upgrade-migration-audit.jsonl`), and a `sdd doctor` WARN when a past-gate deprecated artifact is still present.

### Phase T/V — Tests (✅ Complete)

- Added `TestWave27ProvenanceIntegrity` (Phase A), `TestWave27IntakeDiscipline` (Phase B), and `TestWave27ModuleLifecycle` (Phase C) plus integrity-list additions: `agent-activation-discipline` → `EXPECTED_INSTRUCTIONS`; `design-tokens-template.md` + `experience-template.md` → `EXPECTED_TEMPLATES`; `intent-kernel` skill-existence test; `trace` → `TestCommandTaxonomy.expected_commands`; `memory-index.schema.json` → `TestSchemaFiles`.
- Full suite: **724 passed**. The 5 pre-existing failures previously tracked as tech debt have been resolved (see Follow-up below).

### Follow-up — Pre-existing gap closure (✅ Complete)

Five structural-integrity tests that pre-dated Wave 27 (carried as tech debt) were resolved by closing the underlying documentation/CLI gaps — no test was weakened:

- **`sdd skill install` implemented (Wave 26 §25 #1 A.7).** Registered the missing `install` subcommand on `sdd skill` with `--explain-policy`, mirroring `sdd module install` (A.5/A.9) and `sdd extension install` (A.6): resolves the project policy via `gate_install`, prints the JSON decision under `--explain-policy`, then copies the skill into `.github/skills/<id>` (refusing to overwrite). Documented in README CLI surface and `SKILL-INDEX.md`.
- **`stub-scan` routed under `sdd-review` (Wave 24).** Added the `stub`/`placeholder`/`TODO`/`not implemented` → `stub-scan` row to the `sdd-review` namespace meta-skill routing table.
- **`drift-analysis` routed under `sdd-doctor` (Wave 24).** Added the `drift`/`orphaned AC`/`orphaned test`/`stale AC` → `drift-analysis` row to the `sdd-doctor` namespace meta-skill routing table.
- **EVOLUTION §8 dual-dispatch design boundary (Wave 26 §25 #4).** Added the "Dual dispatch paths for the same command" rejected-feature row (GSD-2 v3.0.0 #5786–#5789) to the Rejected Features table, aligning with Constraint #10 in `sdd-philosophy.instructions.md` and the PLAYBOOK Architecture Invariants.
- **README version header** bumped to `v4.9 — May 15, 2026` to match the shipped version.

---

## Wave 23 — Public Refresh May 11 (May 11, 2026)

> **Status:** 🟡 In progress (Phase A ✅ Complete; Phase B–C planned)
> **Plan:** [`_plan/WAVE-23-PUBLIC-REFRESH-MAY11-IMPLEMENTATION-PLAN.md`](_plan/WAVE-23-PUBLIC-REFRESH-MAY11-IMPLEMENTATION-PLAN.md)
> **Source:** May 11 public-framework refresh harvest (§23) — Phase A targets cold-start optimisation harvested from anthropic-skills, mlx-knife, claude-code-templates patterns.

### Phase A — Cold-Start Optimisation (✅ Complete)

- **§23.A.1–§23.A.6 — Namespace meta-skills.** Created six 80-line cold-start meta-skills under `.github/skills/` (`sdd-specify`, `sdd-architect`, `sdd-implement`, `sdd-review`, `sdd-doctor`, `sdd-module`) that route to specialised sub-skills on demand instead of front-loading them.
- **§23.A.7–§23.A.8 — Skill mapping cold-start surface.** Extended `.specify/skill-mapping.yaml` with a top-level `coldStartSurface:` list. `sdd skill list` now returns only the 6 namespace meta-skills by default; `sdd skill list --flat` lists every skill on disk.
- **§23.A.9–§23.A.14 — Time-decay memory ranking.** Every `.specify/memory/*.md` file now carries `last_referenced_at` / `reference_count` frontmatter (and `decay_floor: true` for inviolable charters). Added `sdd/utils/memory_ranking.py` (relevance × exp(−days/30) scoring with stale detection), `sdd bridge --explain` (decision-table view), and `sdd memory list [--stale --threshold-days N]`.
- **§23.A.15–§23.A.18 — Install profiles.** `sdd init --minimal | --upgrade | --full` writes a tier-tracked `.specify/install-profile.json`. `sdd doctor --suggest-upgrade` recommends upgrades when sub-phase usage exceeds the installed tier.
- **§23.A.19–§23.A.21 — Description-length budget.** Authoring guidance enforces ≤100 char (WARN) / ≤200 char (ERROR) `description:` frontmatter. Added `sdd doctor --description-length` scanner and an audit (`_plan/WAVE-23-DESCRIPTION-AUDIT.md`) — 0 ERROR-level findings after tightening.
- **§23.A.22–§23.A.25 — Context-utilisation guard.** New `sdd/utils/tokenizer.py` (tiktoken with character-fallback) provides per-model windows. `sdd bridge --context-check` and `sdd doctor --context` report current bridge-payload utilisation against the active model window with WARN at 60% and CRITICAL at 70%.
- **§23.A.27 — Lazy phase-prompt loader.** Added `.github/prompts/sdd-phase-loader.prompt.md` so phase 0–5 prompt bundles are referenced only when needed.
- **§23.A.26 / §23.A.28 — Deferred.** Per-phase prompt extraction and skill-pre-load registry deferred (filed in plan with rationale: existing prompts are already phase-scoped and on-demand).
- **Tests.** 566 tests pass. Added `TestWave23PhaseAFlags` (CLI surface), `TestWave23NamespaceMetaSkills`, `TestWave23ColdStartSurface`, `TestWave23MemoryFrontmatter`, `TestWave23PhaseLoaderPrompt`, `TestWave23DescriptionLengthBudget`.

---

## Wave 22 — APM + Genesis Harvest (April 27, 2026)

> **Status:** ✅ Complete
> **Plan:** [`_plan/WAVE-22-APM-GENESIS-HARVEST-IMPLEMENTATION-PLAN.md`](_plan/WAVE-22-APM-GENESIS-HARVEST-IMPLEMENTATION-PLAN.md)
> **Source:** APM + Genesis new-framework harvest (§22) — 3 accepted features from 16 evaluated.

### Phase A — Hidden Unicode Scanning (✅ Complete)
- Created `hidden-unicode-scan.instructions.md` (46 lines) — 6 Unicode codepoint categories (Tag Characters, Bidi Overrides, Zero-Width, Variation Selectors, Invisible Operators, Deprecated Formatting), detection protocol, integration points.
- Extended `injection-scan.instructions.md` with Hidden Unicode Detection cross-reference section.
- Documented `sdd doctor --scan-unicode` flag and hidden Unicode scan behavior in PLAYBOOK.
- Documented `sdd module install` pre-write Unicode scan in PLAYBOOK and instruction file.

### Phase B — SARIF CI Gate Output (✅ Complete)
- Documented `sdd doctor --format sarif` flag and `--output` file redirect in PLAYBOOK.
- Added SARIF rule ID table with 6 rules: `sdd/broken-ref`, `sdd/deprecated-flag`, `sdd/module-drift`, `sdd/instruction-oversized`, `sdd/skill-oversized`, `sdd/hidden-unicode`.
- Created `sdd-doctor-ci.yml.example` — sample GitHub Actions workflow for SARIF upload.
- Added CI Integration subsection to PLAYBOOK CI/CD section.

### Phase C — APM Coexistence Guide (✅ Complete)
- Added "§ Working with APM" to `INSTALL-IN-NEW-PROJECT.md` — file ownership table, recommended directory layout, integrity verification separation, install order guidance.
- Added APM exclusion note in PLAYBOOK User Modules section.
- Documented APM lockfile detection INFO behavior in `sdd doctor` section.

### Phase T — Test Suite (✅ Complete — 359 passed)
- Added `hidden-unicode-scan` to `EXPECTED_INSTRUCTIONS`.
- Added `test_playbook_sarif_rule_ids` validating all 6 SARIF rule IDs.
- Added `test_sdd_doctor_ci_example_workflow_exists` in `TestCICDWorkflows`.
- Added `test_install_guide_apm_section_exists` validating APM coexistence content.

---

## Wave 21 — Agentic SDLC Handbook Harvest + Codebase Hygiene (April 27, 2026)

> **Status:** ✅ Complete
> **Plan:** Appendix J of [`_plan/MASTER-PLAN.md`](_plan/MASTER-PLAN.md)
> **Source:** The Agentic SDLC Handbook book harvest (§21) — instruction sizing, session discipline, ADAPT recovery loop, context-debt audit, skill design test, G2R metric, adoption business case, co-location architecture pattern.

### Phase A — Context Engineering Discipline (✅ Complete)
- Added `instruction-authoring.instructions.md` — sizing contract (≤ 50 lines global, ≤ 50 domain, ≤ 80 skills) + co-location principle + DRY corollary.
- Added `session-discipline.instructions.md` — 3 reset triggers + carry-forward `SESSION-HANDOFF.md` protocol + feedback-loop procedure.
- Added `sdd doctor` size-warning check — warns when any `.github/instructions/*.instructions.md` exceeds 50 lines.
- Updated PLAYBOOK: added §§ Instruction Sizing, Session Management, Knowledge Co-Location.

### Phase B — Recovery & Quality Feedback (✅ Complete)
- Extended `stuck-detection.instructions.md` with ADAPT sub-procedure section (5 steps + `RECOVERY-DISPATCH.md` artifact definition).
- Added Skill Design Test 3-criteria decision tree to `session-discipline.instructions.md`.
- Added G2R Metrics section to PLAYBOOK § Measuring SDD Health with 2:1/4:1 interpretation thresholds.
- Extended `sdd report --format md` template to include § Quality Metrics block with G2R + Intervention Rate prompt fields.

### Phase C — File Hygiene: Instruction Sizing (✅ Complete)
- Trimmed 8 moderately oversized instructions (51–80 lines) to ≤ 50 lines.
- Split 6 significantly oversized instructions (81–130 lines) into core + detail companion pairs.
- Split 4 large instructions (131+ lines) into core + detail/catalog companions; restructured `anti-patterns-examples`.
- Removed all wave-attribution text from instruction, skill, and agent file content.

### Phase D — Skill Reclassification (✅ Complete)
- Created `api-patterns/SKILL.md` — REST API design decision framework skill (60 lines).
- Created `messaging-patterns/SKILL.md` — async messaging design decision framework skill (57 lines).
- Created `source-verification/SKILL.md` — DETECT→FETCH→IMPLEMENT→CITE workflow skill (68 lines).
- Trimmed all 21 skills to ≤ 80 lines (Python `.strip().splitlines()` counting).
- Updated `skill-mapping.yaml` with 3 new skills (api-patterns, messaging-patterns, source-verification).

### Phase E — Organizational Adoption Support (✅ Complete)
- Added `context-debt-audit.prompt.md` — 5-phase audit workflow producing `CONTEXT-DEBT.md`.
- Added `adoption-timeline-template.md` — 3-phase adoption template with rollback criteria + kill criterion.
- Added `adoption-business-case.prompt.md` — 5-step TCO + ROI framework producing `ADOPTION-BUSINESS-CASE.md`.
- Updated `TEAM-ADOPTION-GUIDE.md` with § Organizational Adoption referencing all three artifacts.

### Phase T — Tests (✅ Complete)
- Added `TestWave21PhaseDSkillReclassification` (9 tests) — skill existence, instruction references, sizing assertions.
- Added `TestWave21PhaseEOrganizationalAdoption` (7 tests) — prompt/template existence, content validation, guide references.
- Added instruction sizing assertion (all ≤ 50 lines, companions ≤ 200) and skill sizing assertion (all ≤ 80 lines).
- Final test run: **355 passed in 1.44s**, 0 failures.

### Phase Z — Documentation & Coherency Sync (✅ Complete)
- `analysis/ENTERPRISE-SDD-ANALYSIS.md` coherency block updated (instructions 26 core + 17 companion, prompts 32, skills 21, templates 19).
- `ENTERPRISE-SDD-EVOLUTION.md` coherency sync block updated.
- `enterprise-sdd/PLAYBOOK.md` prompt count updated to 32; new prompts added to prompt library table.
- `enterprise-sdd/_plan/MASTER-PLAN.md` — Wave 21 marked ✅ Complete.

---

## Wave 20 — Multi-Framework Public Refresh (April 26, 2026)

> **Status:** ✅ Complete
> **Plan:** [`_plan/WAVE-20-PUBLIC-REFRESH-APR26-IMPLEMENTATION-PLAN.md`](_plan/WAVE-20-PUBLIC-REFRESH-APR26-IMPLEMENTATION-PLAN.md)
> **Source:** Public refresh harvest covering AIDD v3.0.0, BMAD v6.5.0, GSD v1 v1.38.5, GSD-2 v2.78.1, Spec Kit v0.8.1.

### Phase A — Reasoning & Review Hardening (✅ Complete)
- Added `hotspot-review` skill — churn-aware review prioritisation; emits `HOTSPOTS.md` consumed by the reviewer agent.
- Added `sdd analyze --hotspots` and wired hotspot context into `review.agent.md`.
- Added `rtc-reasoning.instructions.md` — Recursive Thought Criticism protocol; activated by `--with-reasoning` on `sdd new` and `sdd gate`.
- Added `checkpoint-preview.prompt.md` — concern-ordered preview that surfaces blockers before commit; surfaced via `sdd ship --preview`.

### Phase B — Lifecycle Coverage Extensions (✅ Complete)
- Added skill-eval harness: `.sdd-eval.yaml` schema + `skill-eval-template.yaml` + `sdd skill validate --eval` runner that scores a skill against curated test cases.
- Added `prfaq-working-backwards` skill — Amazon-style press-release-FAQ specs, with eval set.
- Added `sdd gate post-merge <feature>` — runs `gates.post_merge.build_command` / `test_command` and writes `gate-post-merge.report.md`.
- Added custom-branch planning lock: `sdd new --on-branch <branch>` + `feature.lock.json` (4-tier resolution: explicit → `SDD_FEATURE` env → lock file → branch heuristic).
- Added `--feature` flag to `sdd analyze`, `sdd gate`, and `sdd ship` for explicit feature targeting.

### Phase C — Operational Polish (✅ Complete)
- Added `.specify/skill-mapping.yaml` — per-agent skill scoping registry (4 scoped, 5 globally available); enforced by new `sdd skill list --scope <agent>`.
- Added sha256-tracked module manifests: `module-install.{sh,ps1}` now records `fileHashes` + `manifestSha256` in `.sdd-modules/registry.json`; `sdd module verify [--reset|--accept]` reconciles drift; `sdd doctor` surfaces drift as `WARN`.
- Established CLI deprecation lifecycle: `CLI-DEPRECATIONS.md` Active/Removed catalog, `cli-deprecation-policy.instructions.md`, `@deprecated(replacement=…, removal_version=…, migration=…)` decorator in `sdd.utils.deprecation`, and a `sdd doctor` scan over `.specify/config.yaml` and `.specify/scripts/*.{sh,ps1}` that warns on usage of Active deprecated tokens.

### Phase T — Test Suite Update (✅ Complete)
- Added `rtc-reasoning` and `cli-deprecation-policy` to `EXPECTED_INSTRUCTIONS`.
- Added `checkpoint-preview` to `EXPECTED_PROMPTS`; `hotspot-review` and `prfaq-working-backwards` to `TestSkillDescriptors`; `skill-eval-template.yaml` to `EXPECTED_TEMPLATES`.
- Added `TestWave20PhaseBLifecycle` (12 tests) and `TestWave20PhaseCOperationalPolish` (10 tests) in `test_framework_integrity.py`.
- Added `TestWave20CLIFlagAcceptance` (12 help-text tests) in `test_cli_unit.py`.
- Added `TestWave20FeatureResolver` (3 priority-chain tests) and `TestWave20ModuleHashDrift` (2 hash-drift tests) in `test_integration.py`.

### Phase V — Test Execution & Fix (✅ Complete)
- Final test run: **481 passed in 109.59s**, 0 failures across all 5 layers (CLI unit, integration, end-to-end, framework integrity, edge cases).
- Run report archived at [`.specify/reports/wave-20-test-run.md`](.specify/reports/wave-20-test-run.md).

### Phase Z — Documentation Update (✅ Complete)
- `enterprise-sdd/README.md` bumped to **v4.6** with Wave 20 development-history entry.
- `enterprise-sdd/PLAYBOOK.md` extended with Phase B and Phase C operational sections.
- `analysis/ENTERPRISE-SDD-ANALYSIS.md` coherency block reconciled (instructions 25, prompts 30, skills 18, templates 18) and Wave 20 row added to Recent Changes.
- `enterprise-sdd/REQUIREMENTS.md` — new §7 "Wave 20 — Operational Contracts" documents post-merge config keys, feature-resolution precedence, manifest hashing schema, and CLI deprecation contract.
- `enterprise-sdd/_plan/MASTER-PLAN.md` — Wave 20 marked ✅ Complete (status banner, Appendix I, end-of-file status line).
- `ENTERPRISE-SDD-EVOLUTION.md` coherency sync block updated.

---

## Rename — Modules and Brand Neutralization (April 26, 2026)

> **Status:** ✅ Complete
> **Plan:** [`_plan/MODULE-RENAME-PLAN.md`](_plan/MODULE-RENAME-PLAN.md)

### Module ids renamed
- `convergence-core` → `core-be` (backend Quarkus/Hexagonal module)
- `convergence-fe` → `std-fe` (standard React/TS frontend module)
- `myenx` → `aws-fe` (AWS-targeted frontend module)
- All directory paths, schemas, registries, agents, prompts, instructions, CLI scripts, sandbox tests, and module-level playbooks updated.
- No back-compat shims (single-PR migration; consumers update references directly).

### Brand neutralized to `Acme` family
- `Euronext Securities` → `Acme Securities`
- `Euronext` → `Acme`; `myEuronext` → `Acme Portal`
- `MyENX`/`MyEnx`/`myENX` (as brand) → `Acme FE`
- `enx.sec` → `acme.sec`
- Java packages `com.euronext.securities` / `com/euronext/securities` → `com.acme.securities` / `com/acme/securities` (dot- and slash-form)
- Java instruction docs in `core-be/instructions/*` carry a fictional-placeholder banner.

### New mapping registry
- Added [.github/instructions/brand-and-module-mapping.instructions.md](../.github/instructions/brand-and-module-mapping.instructions.md) — workspace-wide canonical mapping (allow-list, anti-list, external-framework→module table). Referenced by `analyse-framework`, `compare-frameworks`, `evolve-enterprise-sdd`, `improvement-plan`, `implement-sdd-plan`.

### Allow-list (preserved verbatim)
- `ENTERPRISE-SDD-EVOLUTION.md` (historical record; rename note added at top).
- `_plan/bak/`, `_plan/outdated/` (archive).
- Standalone token `Convergence` (Wave 18 product feature, e.g., `convergence-review`).
- One anchor link in `MASTER-PLAN.md` line 2270 pointing to a preserved EVOLUTION heading.

### Validation
- Test suite: 429 passing (unchanged from baseline). The 1 pre-existing failure (`test_playbook_prompt_count_27`) predates the rename and is unrelated.
- Final residual sweep: zero matches for `Euronext|MyENX|MyEnx|myENX|myEuronext|enx.sec|euronext|com.euronext|com/euronext` outside the allow-list.

### Post-audit follow-ups (April 26, 2026)
- **R1 — Mapping registry test added.** New `TestBrandAndModuleMappingRegistry` class in `_tests/test_framework_integrity.py` (7 tests) enforces that `.github/instructions/brand-and-module-mapping.instructions.md` exists, has correct YAML frontmatter, lists every legacy module/brand token from this plan, lists current `core-be`/`std-fe`/`aws-fe` and `Acme` tokens, contains all required sections, and is referenced by the 5 key agents (`analyse-framework`, `compare-frameworks`, `evolve-enterprise-sdd`, `improvement-plan`, `implement-sdd-plan`). Closes Phase 8 step 4 of [`_plan/MODULE-RENAME-PLAN.md`](_plan/MODULE-RENAME-PLAN.md).
- **R2 — `test_playbook_prompt_count_27` fixed.** Renamed to `test_playbook_prompt_count_matches_filesystem` and rewritten to derive the expected count from `.github/prompts/*.prompt.md` (currently 29) instead of hard-coding `28`. The previous assertion was stale — Wave 19 added a prompt without updating the test.
- **Final test suite: 438 passing, 0 failing** (was 429 passing + 1 pre-existing failure; +8 = 7 new registry tests + 1 fixed test now green).

---

## Wave 19 — Agent Skills, VORTEX & FE Harvest (April 24, 2026)

> **Status:** ✅ Complete
> **Plan:** [`_plan/WAVE-19-AGENT-SKILLS-VORTEX-FE-IMPLEMENTATION-PLAN.md`](_plan/WAVE-19-AGENT-SKILLS-VORTEX-FE-IMPLEMENTATION-PLAN.md)

### Phase A — Behavioral Reliability Hardening (✅ Complete)
- Created `skill-authoring.instructions.md` — canonical anti-rationalization rubric; mandates `## Common Rationalizations` section (≥3 entries, exact-wording quotes, step-referencing rebuttals) in every SDD skill
- Created `source-verification.instructions.md` — DETECT→FETCH→IMPLEMENT→CITE workflow for all external-knowledge decisions; mandates `## External References` table in artifacts citing external sources
- Created `source-citation-check` skill — audits artifacts for citation completeness; defines 6 finding types (MISSING_SECTION, EMPTY_TABLE, MISSING_SOURCE, MISSING_SECTION_REF, ASSUMPTION_NO_NOTE, PASS)
- Created `skill-template.md` — canonical template for new SDD skills with pre-populated `## Common Rationalizations` instructional block
- Added `--rationalizations` flag to `sdd skill validate` — additionally verifies `## Common Rationalizations` section presence and non-empty rows
- Added `## External References` section to `spec-template.md` and `plan-template.md`

### Phase B — Triad Synthesis + Enterprise Integration (✅ Complete)
- Created `release-triad-synthesis.prompt.md` — 5-step agent prompt synthesising Gate 4 release decision from 3 parallel reviews (code, security, test evidence)
- Created `gate4-release-packet-template.md` — standardised Gate 4 release artifact with Evidence Artifacts, Traceability Check, Blockers, Risks, Rollback Plan, and GO/NO-GO Verdict sections
- Added `--synthesize` flag to `sdd gate 4` — activates triad synthesis mode for Gate 4 evaluation
- Created `jira-rest-ops` skill — token-safe Jira Cloud REST fallback skill for when MCP is unavailable; Safety Defaults: read-free, write requires confirmation, token from env only
- Created `scripts/jira-rest.sh` — shell template with full Jira REST function library and env-var guards
- Created `jira-endpoint-map-template.md` — Jira Cloud REST v3 endpoint reference card (Issue, Search, Project, Sprint/Board, User ops)
- Extended `sdd-agent-lint/SKILL.md` with IN-07 (instruction wiring: `applyTo` or parent-agent reference required) and IN-08 (version-drift: all files in same pack must share stack version tuple); added `## Common Rationalizations` section
- Added `--phase-ledger` flag to `sdd status` — generates read-only phase execution ledger

### Phase C — Optional Domain Specialisation (✅ Complete)
- Created `convergence-ddd-aggregate` optional module — DDD aggregate boundary design skill + ADR template; activated via `sdd module add convergence-ddd-aggregate`
- Created `ddd-aggregate-design.skill.md` — 5-step invariant-first aggregate boundary guide with anti-pattern detection (God Aggregate, Anemic, Cross-ref, Missing Repo, Shared Mutable State)
- Created `aggregate-decision-record-template.md` — structured ADR template with Bounded Context, Invariants, Anti-Patterns Checked, Trade-off Record, Domain Events, Cross-Aggregate References
- Created `phase-ledger-template.md` — read-only derivative ledger for all 6 SDD phases; human-auditable phase timeline with Gate Evidence per phase

### Phase T — Test Suite Update (✅ Complete)
- Added `skill-authoring` and `source-verification` to `EXPECTED_INSTRUCTIONS`
- Added `release-triad-synthesis` to `EXPECTED_PROMPTS`
- Added `skill-template.md`, `gate4-release-packet-template.md`, `jira-endpoint-map-template.md`, `phase-ledger-template.md` to `EXPECTED_TEMPLATES`
- Added `test_source_citation_check_skill_exists` and `test_jira_rest_ops_skill_exists` to `TestSkillDescriptors`
- Added 3 new test classes: `TestWave19BehavioralReliability` (14 assertions), `TestWave19TriadSynthesis` (13 assertions), `TestWave19PhaseTemplate` (10 assertions)

### Phase V — Test Execution (✅ Complete)
- All 279 tests pass across all layers; 1 test fixed (endpoint path format in jira-endpoint-map test)

---

## Wave 18 — Multi-Framework Public Harvest (April 23, 2026)

> **Status:** ✅ Complete
> **Plan:** [`_plan/PUBLIC-HARVEST-APR23-IMPLEMENTATION-PLAN.md`](_plan/PUBLIC-HARVEST-APR23-IMPLEMENTATION-PLAN.md)

### Phase A — Adaptive Planning Foundation (✅ Complete)
- Created `progressive-planning.instructions.md` — sketch-then-refine protocol for multi-phase deliveries (Tier 1 full-detail, Tier 2 sketch)
- Created `escalation-protocol.instructions.md` — 3-level decision framework (Resolve/Escalate/Block) for mid-execution ambiguity
- Created `escalation-template.md` — structured template for escalation artifacts
- Added `--progressive` flag to `sdd new` — activates sketch mode for subsequent phases
- Added `--escalations` flag to `sdd status` — lists pending escalation artifacts

### Phase B — Validation Enrichment (✅ Complete)
- Created `convergence-review.prompt.md` — multi-model review orchestration with convergence rule, max 2 rounds, stall detection
- Created `convergence-review.instructions.md` — trigger criteria for convergence review (>3 components, security-sensitive, opt-in)
- Created `red-team-spec` skill — adversarial spec analysis with 7 dimensions and severity classification
- Enhanced `analysis.agent.md` with gap-closure analysis step (coverage gaps, decision gaps, wiring gaps)
- Added `--gaps` flag to `sdd analyze` — runs gap-closure analysis only
- Created `gap-report-template.md` — structured 3-category gap report template

### Phase C — Operational Polish (✅ Complete)
- Created `gate-hooks.instructions.md` — post-gate automation hooks (notify, auto-commit, trigger-next, export-report)
- Added `--hooks` and `--convergence` flags to `sdd gate` — post-gate hook dispatch and convergence review
- Created `sdd doctor` CLI command — validates framework installation integrity (agents, instructions, skills, templates, CLI, modules, schemas)
- Added `--extract` flag to `sdd retrospect` — automated learnings extraction from feature artifacts
- Added `--wrap` flag to `sdd preset apply` — overlay preset stacking with precedence
- Added `show` subcommand with `--resolved` flag to `sdd preset` — display effective merged configuration
- Added `doctor` to `command-taxonomy.json` under new `maintenance` domain

### Phase T — Test Suite Update (✅ Complete)
- Added 4 instructions to `EXPECTED_INSTRUCTIONS`: `progressive-planning`, `escalation-protocol`, `convergence-review`, `gate-hooks`
- Added `convergence-review` to `EXPECTED_PROMPTS`
- Added `escalation-template.md` and `gap-report-template.md` to `EXPECTED_TEMPLATES`
- Added `test_red_team_spec_skill_exists` to `TestSkillDescriptors`
- Added `doctor` to `expected_commands` in `TestCommandTaxonomy`
- Added 3 Wave 18 test classes with 22 new assertions

### Phase V — Test Execution (✅ Complete)
- All 234 tests pass across all layers

---

## Wave 17 — Cross-Platform Test Suite & CLI Dispatch (April 19, 2026)

> **Status:** ✅ Complete
> **Plan:** [`_plan/CROSS-PLATFORM-TEST-SUITE-IMPLEMENTATION-PLAN.md`](_plan/CROSS-PLATFORM-TEST-SUITE-IMPLEMENTATION-PLAN.md)

### A — Platform Dispatch Layer (✅ Complete)
- Added `IS_WINDOWS` constant, `script_command(stem, repo_root)` function, and `venv_bin_dir(venv_dir)` function to `config.py`
- `script_command()` returns PowerShell invocation on Windows, bash on Unix — validates script existence

### B — CLI Command Migration (✅ Complete)
- Migrated all 16 CLI command files from hardcoded `["bash", str(script)]` to `script_command()` dispatch
- Updated `_SCRIPT_MAP` / `_ACTION_TO_SCRIPT` dicts to store stems (no `.sh` suffix)
- Removed dead `_SCRIPT_MAP` in `ingest.py`

### C — Test Infrastructure (✅ Complete)
- Fixed `_bash_version()` to early-return on Windows (no `/usr/bin/env bash` call)
- Fixed `Sandbox.env()` to use `os.pathsep` instead of hardcoded `":"`
- Fixed `Sandbox.env()` to use `venv_bin_dir()` instead of hardcoded `venv/bin/`
- Added `PYTHONUTF8=1` to sandbox env on Windows for encoding safety
- Fixed `Sandbox.install_cli()` to use `python -m pip` instead of `pip.exe` (avoids Windows permission errors)
- Fixed `Sandbox.sdd()` to use `python -m sdd` on Windows instead of `sdd.exe` wrapper
- Fixed `Sandbox.sdd_py()` to use `venv_bin_dir()` for Python path
- Made `install_mock_gh()` cross-platform: `.cmd` wrapper on Windows, shebang script on Unix
- Made `install_mock_extension()` cross-platform: `.ps1` hooks on Windows, `.sh` on Unix
- Added `skip_no_powershell` marker

### D — Async Test Support (✅ Complete)
- Created `_tests/requirements-test.txt` with `pytest-asyncio>=0.23`
- Created `pyproject.toml` at enterprise-sdd root with `asyncio_mode = "auto"`

### T — Test Suite Update (✅ Complete)
- Added `TestCrossPlatformDispatch` class (6 tests): config.py exports verification
- Added `TestCLICommandsNoBashHardcode` class (32 tests): no bash hardcode + script_command import
- Added `TestConftestCrossPlatform` class (3 tests): os.pathsep, venv_bin_dir, IS_WINDOWS checks

### V — Verification (✅ Complete)
- Framework integrity tests: 208 passed (167 existing + 41 new)
- Full suite: 349 passed, 0 failed, 10 skipped, 0 errors
- Previous: 260 passed, 1 failed, 8 skipped, 91 errors

### Z — Documentation (✅ Complete)
- Updated README.md: cross-platform script dispatch noted
- Updated PLAYBOOK.md: cross-platform support table in CLI section
- Updated ENTERPRISE-SDD-ANALYSIS.md: coherency sync block, Wave 17 in changes table

---

## Wave 16 — Internal Frameworks Harvest (April 19, 2026)

> **Status:** ✅ Complete
> **Plan:** [`_plan/INTERNAL-FRAMEWORKS-HARVEST-IMPLEMENTATION-PLAN.md`](_plan/INTERNAL-FRAMEWORKS-HARVEST-IMPLEMENTATION-PLAN.md)

### A — Foundation: Behavioral Discipline & Agent Standards (✅ Complete)
- Added Rule 7 (Sycophantic Agreement) to `anti-patterns.instructions.md` — challenge-first behavior for unvalidated proposals
- Added Rule 7 before/after examples to `anti-patterns-examples.instructions.md` (cache root-cause, GraphQL trade-off)
- Enhanced `question-format.instructions.md` with P1/P2/P3 priority tiers and ambiguity resolution principle
- Created `agent-design-principles.instructions.md` — 6 codified principles (Less Is More, Explicit Boundaries, Failure Behavior, Template Discipline, Tool Minimalism, Handoff Clarity)
- Referenced design principles from `agent-builder.agent.md` Prime Directive
- Added `TestWave16PhaseA` test class (4 tests) + updated `EXPECTED_INSTRUCTIONS` and Rule coverage range

### B — Security Pipeline (✅ Complete)
- Created `security-reviewer.agent.md` — dedicated security agent with OWASP Top 10 checklist, severity levels (Critical/High/Medium/Low/Info), read-only tools, boundary rules
- Created `malicious-code-detection` skill — scans for eval injection, dynamic imports, base64 payloads, crypto-mining, data exfiltration
- Created `supply-chain-risk` skill — CVE checks, typosquatting detection, unmaintained package flagging, lockfile integrity
- Created `secrets-scan` skill — API keys, tokens, passwords, certificates, configuration file checks
- Updated `review.agent.md` with upstream `security-reviewer` reference and "Security Review Needed" handoff
- Added Gate 4 security evidence requirement to `ship-checklist-template.md` (Section 3.3)

### C — Review & Quality Enhancement (✅ Complete)
- Added Instruction Compliance Review mode to `review.agent.md` — compares branch diff against applicable `.instructions.md` files with Critical/Warning/Info severity
- Added Security Review Integration section to `review.agent.md` — verifies `security-report.md` exists before final verdict
- Created `sdd-agent-lint` skill — verifies agent/instruction structural quality (YAML frontmatter, boundary rules, size budget, naming conventions)
- Created `agent-lint-checks.instructions.md` — lint checklist reference defining structural rules for agents and instructions

### D — Frontend Extension Enrichment (✅ Complete)
- Extended `fe-component-ambiguity-resolution.instructions.md` with DateField vs RangeField and Table vs DataGrid pairs
- Generic ambiguity resolution principle already present in `question-format.instructions.md` (from Phase A)
- Added Figma MCP configuration to `react-vite-vitest-setup.md` setup template (`.vscode/mcp.json` entry)
- Created `frontend-stratos-core/README.md` with Figma MCP integration documentation

### E — Enterprise Tooling & Knowledge Patterns (✅ Complete)
- Created `sdd-docx-builder` skill — Word document generation using Python stdlib (zipfile + XML)
- Created `sdd-xlsx-builder` skill — Excel generation with traceability matrix support
- Created `sdd-pptx-builder` skill — PowerPoint generation with gate summary support
- Added `--format md|docx|xlsx|pptx` flag to `sdd report` CLI command
- Documented "Project-Specific Prompt Libraries" pattern in PLAYBOOK (directory convention, naming, template)
- Added ticket-specific prompt pattern hint to `prompt-builder.agent.md`

### T — Test Suite Update (✅ Complete)
- Added `security-reviewer` to `EXPECTED_AGENTS` (16 total)
- Added `agent-lint-checks` to `EXPECTED_INSTRUCTIONS` (17 total)
- Added 7 new skill existence tests (malicious-code-detection, supply-chain-risk, secrets-scan, sdd-agent-lint, sdd-docx-builder, sdd-xlsx-builder, sdd-pptx-builder)
- Added `TestWave16PhaseBSecurityPipeline` (8 tests), `TestWave16PhaseCReviewQuality` (3 tests), `TestWave16PhaseDFrontendEnrichment` (3 tests), `TestWave16PhaseEEnterpriseTooling` (2 tests)
- All 167 framework integrity tests passing

### Z — Documentation Update (✅ Complete)
- Updated `README.md` to v4.5 with 16 agents, 17 instructions, 13 skills, security pipeline, all new features
- Updated `PLAYBOOK.md` with security review step (§5.1b), `@security-reviewer` in agent map, `sdd report --format` docs, ticket prompt pattern
- Updated `ENTERPRISE-SDD-ANALYSIS.md` coherency sync block with Wave 16 counts and completion status

---

## Wave 15 — Security, Governance & Brownfield Harvest (April 18, 2026)

> **Status:** ✅ Complete
> **Plan:** [`_plan/SECURITY-GOVERNANCE-BROWNFIELD-HARVEST-IMPLEMENTATION-PLAN.md`](_plan/SECURITY-GOVERNANCE-BROWNFIELD-HARVEST-IMPLEMENTATION-PLAN.md)

### Q — Security Hardening & Spec Quality (✅ Complete)
- Created `injection-scan.instructions.md` — prompt injection defense instruction applied to all agents (7 injection patterns, "Never Do" rules)
- Cross-referenced injection scanning from `anti-patterns.instructions.md`
- Created `sdd-ambiguity-score` skill — scores spec artifacts for ambiguity on 1–5 scale across 5 dimensions
- Added ambiguity scoring step to `clarification.agent.md`
- Registered `sdd-ambiguity-score` in command taxonomy

### R — Pre-Pipeline & Brownfield Adoption (✅ Complete)
- Created `spike.prompt.md` — structured spike/experiment template
- Implemented `sdd spike start|wrap` CLI commands with `.specify/spikes/` directory
- Created `ingest-docs` skill — classifies existing documents into SDD slots with conflict detection
- Implemented `sdd ingest` CLI command delegating to ingest-docs skill
- Registered `spike` and `ingest` in command taxonomy with `pre-pipeline` domain
- Documented brownfield onboarding workflow in `INSTALL-IN-NEW-PROJECT.md`

### S — Agent Governance & Context Efficiency (✅ Complete)
- Defined agent size budget tiers (compact ≤200, standard ≤400, extended ≤600) in `agent-builder.agent.md`
- Created `lint-agent-size.sh` and `lint-agent-size.ps1` for size enforcement
- Defined `<!-- sdd:section:NAME -->` marker convention in `tech-context-maintainer.agent.md`
- Updated `context-bridge-template.md` with section markers
- Added `--section` flag to `sdd context compile` for marker-based upsert

### T — Test Suite Update (✅ Complete)
- Added `injection-scan` to `EXPECTED_INSTRUCTIONS`, `spike` to `EXPECTED_PROMPTS`
- Added `test_ambiguity_score_skill_exists` and `test_ingest_docs_skill_exists`
- Added `spike` and `ingest` to taxonomy expected commands
- New test classes: `TestWave15AgentSizeLint`, `TestWave15ContextBridgeMarkers`, `TestWave15InjectionScan`

### V — Test Execution & Fix (✅ Complete)
- All 137 framework integrity tests passing
- Fixed version assertions (v4.3→v4.4, prompt count 26→28)

### Z — Documentation Update (✅ Complete)
- Updated `README.md` to v4.4 with new capabilities, counts, and CLI surface
- Updated `PLAYBOOK.md` to v4.4 with spike/ingest/section CLI docs and prompt count
- Updated `ENTERPRISE-SDD-ANALYSIS.md` coherency sync block
- Updated `ENTERPRISE-SDD-EVOLUTION.md` coherency sync block

---

## Wave 14.3 — Modular Agent Composition: Phases A–E Complete (April 17, 2026)

> **Status:** ✅ Complete
> **Plan:** [`_plan/MODULAR-AGENTS-PLAN.md`](_plan/MODULAR-AGENTS-PLAN.md)

### MOD-E1 — `.sdd-modules/README.md` Updated (✅ Complete)

- Added `agentContributions` to module manifest example with tool-overlay and agents entries
- Documented tool-overlay vs agent contribution with annotated JSON examples
- Added agent-patches vs agent-contributions comparison table

### MOD-E2 — PLAYBOOK.md Module Section Updated (✅ Complete)

- `sdd module install|remove` section now documents the automatic `compose-agents.py` step
- Added callout about `agentContributions` for module authors linking to `.sdd-modules/README.md`

### MOD-E3 — CHANGELOG Updated (✅ Complete)

- Added Phase D+E entries to Wave 14.3; header updated to "Phases A–E Complete"

### MOD-E4 — MIGRATION-GUIDE Section Added (✅ Complete)

- New section: "Module Author Migration: Agent Patches → `agentContributions`"
- Step-by-step for tool overlays, contributed agents, and what does NOT need migration (behavioral patches)

### MOD-D1 — `test_compose_agents.py` Created (✅ Complete)

- 17 tests across 4 classes: `TestCoreOnlyComposition`, `TestToolOverlay`, `TestAgentContributions`, `TestRealWorkspaceComposition`
- Covers: core-only, tool overlays (add/dedup/unknown-target), agent contributions (add/track/dup-slug/multi-module), real-workspace integration (27 total, 15 core, integration tools on requirement-analyst)

### MOD-D2 — Full Suite Green (✅ Complete)

- **277 tests passing** (259 baseline + 1 schema count + 17 compose tests)
- No regressions from any Phase A–E change

### MOD-B1 — `agentContributions` Schema Defined (✅ Complete)

- **Created `.specify/schemas/agent-contributions.schema.json`** — JSON Schema for the `agentContributions` key in `module.json`.
- Schema defines two contribution types: `tool-overlays` (add tools to an existing core agent) and `agents` (entirely new agents with full canonical definition).
- Agent slug pattern enforced: `^[a-z][a-z0-9-]*$` for contributed agents.

### MOD-B2 — `compose-agents.py` Script Created (✅ Complete)

- **Created `.specify/scripts/compose-agents.py`** — composition script that merges core canonical + module contributions into a single effective agent set.
- Reads `agents-canonical.json` + `registry.json` + each module's `agentContributions`.
- Applies tool overlays (deduplication, warning on unknown targets), appends contributed agents (duplicate slug detection).
- Writes `.specify/adapters/agents-composed.json` with a manifest header (coreAgentCount, totalAgentCount, appliedOverlays, contributedAgents).
- Supports `--dry-run` and `--verbose` flags.

### MOD-B3 — `generate-adapters.py` Updated (✅ Complete)

- `load_canonical()` now prefers `agents-composed.json` when present, falls back to `agents-canonical.json` for clean installs.
- No change to adapter generation logic — fully transparent to downstream consumers.

### MOD-B4 — `route.py` Updated (✅ Complete)

- `_load_canonical_agents()` follows the same composed→canonical fallback pattern as B.3.

### MOD-B5/B6 — Module Install/Remove Scripts Updated (✅ Complete)

- `module-install.sh` and `module-remove.sh` now run `compose-agents.py` automatically after updating the registry.
- Ensures `agents-composed.json` is always current after any module lifecycle event.
- Graceful degradation: if compose fails, a warning is emitted and the script continues.

### MOD-C1 — core-be Module Declares Tool Overlay (✅ Complete)

- **Added `agentContributions.tool-overlays`** to `.sdd-modules/modules/core-be/module.json`.
- Overlay targets `requirement-analyst` and adds `githubRepo`, `mcp-atlassian/confluence_get_page`, `mcp-atlassian/jira_get_issue`.
- When core-be is installed, `compose-agents.py` automatically restores these integration tools to the agent's effective definition.

### MOD-C2 — sdd-evolution Module Declares All 12 Agents (✅ Complete)

- **Added `agentContributions.agents`** to `.sdd-modules/modules/sdd-evolution/module.json` with all 12 meta agents in canonical JSON format.
- Builder agents: `agent-builder`, `instruction-builder`, `guidance-builder`, `prompt-builder`, `workflow-builder`.
- Evolution agents: `framework-analyst`, `framework-comparator`, `framework-updater`, `sdd-evolver`, `evolution-planner`, `module-designer`, `extension-designer`.
- Existing `.agent.md` files remain as the human-readable copy (documentation + VS Code Copilot). The module.json is the machine-readable source for composition.

### MOD-C3/C4 — std-fe and aws-fe Evaluated (✅ Not needed)

- Agent patches in std-fe (`agent-severus-generator.patch.md`) and aws-fe (`agent-neo-generator.patch.md`, `agent-smith-reviewer.patch.md`) are behavioral guidance (behavior deltas for agent instruction profiles) — they do not add tools or register new agents.
- Conversion to `agentContributions` is not applicable for behavioral patches. These remain as-is (human review + manual behavior merge).

### MOD-A1 — Integration Tools Removed from Core Agent (✅ Complete)

- **Removed 3 module-specific tools** (`githubRepo`, `mcp-atlassian/confluence_get_page`, `mcp-atlassian/jira_get_issue`) from `requirement-analyst.tools[]` in `agents-canonical.json`. These tools require the `core-be` module and MCP-Atlassian integration.
- `requirement-analyst` core tools are now: `["read", "edit", "search", "fetch"]` — generic and tech-agnostic.
- Integration tools will be re-introduced via module `agentContributions` (Phase B/C work).

### MOD-A2 — Builder Agents Removed from Core Canonical (✅ Complete)

- **Removed 5 builder agents** (`agent-builder`, `instruction-builder`, `guidance-builder`, `prompt-builder`, `workflow-builder`) from `agents-canonical.json`. These agents belong exclusively to the `sdd-evolution` module.
- `agents-canonical.json` now contains exactly **15 core agents**: the complete Phase 0–5 development pipeline.
- Agent files for builders remain in `.sdd-modules/modules/sdd-evolution/agents/`; they will be contributed to the composed agent set when sdd-evolution is installed (Phase B/C).

### MOD-A3 — Schema `tools` Enum Opened (✅ Complete)

- **Changed `tools` in `agent-definition.schema.json`** from a closed enum (10 hardcoded values) to an open `anyOf` pattern.
- Core tools (`read`, `edit`, `search`, `fetch`, `runCommand`, `runSubagent`, `terminalLastCommand`) are still validated by enum.
- Module-contributed tools (e.g. `githubRepo`, `mcp-atlassian/*`) are accepted via open string — no schema violation.

### MOD-A4 — Prompt Moved to core-be Module (✅ Complete)

- **Moved `requirements-from-issue.prompt.md`** from `.github/prompts/` to `.sdd-modules/modules/core-be/prompts/`.
- This prompt assumes MCP-Atlassian availability; it is meaningless without the core-be module.
- **PLAYBOOK.md** updated: prompt count changed from 27 to **26 core prompts**; table entry removed; note added directing users to core-be module for this prompt.

### MOD-A5 — Extension Schema Enums Opened (✅ Complete)

- **Opened `domainCategory`** in `sdd-tailored-extension.schema.json` from hardcoded `["stratos", "search", "review"]` enum to open `string` with `minLength: 1`. Custom domain categories (e.g. `charts`, `forms`) are now valid.
- **Opened `namespacePrefix`** from hardcoded `^(fe|aws-fe)$` pattern to generic `^[a-z][a-z0-9-]*$` — any lowercase identifier is valid.
- **Updated `AUTHORING-GUIDE.md`** to reflect extensible namespace/domain conventions, with built-in values documented as examples.

---

## Wave 14.2 — Builder Agents Migration & PLAYBOOK Restructure (April 17, 2026)

> **Status:** ✅ Complete

### BLD-01 — Builder Agents Moved to sdd-evolution Module (✅ Complete)

- **Moved 5 meta-builder agents** (`agent-builder`, `instruction-builder`, `guidance-builder`, `prompt-builder`, `workflow-builder`) from `.github/agents/` to `.sdd-modules/modules/sdd-evolution/agents/`. These agents form a self-referencing network with zero dependencies on core Phase 0–5 agents, making the move architecturally clean.
- **Updated `module.json`** — agents count from 7 to 12; added 5 builder files to `files.agents` array.
- **Updated `copilot-instructions-supplement.md`** — added 5 builder agents to module agents table.
- **Updated `sdd-evolution/README.md`** — agents count from 7 to 12; updated component table and file structure tree.

### BLD-02 — Core Agent Count Updated (✅ Complete)

- **Updated `EXPECTED_AGENTS` in tests** — removed 5 builder agents; core count now 15 (was 20). Module tests expect 12 agents (was 7).
- **Updated `copilot-instructions.md`** — agent folder section now says "15 core development agents"; builders referenced as sdd-evolution module.
- **Updated `README.md`** — agent count changed from "20 Specialized" to "15 Core"; agent table builder rows replaced with module note.
- **Updated `PLAYBOOK.md`** — all references changed from 20 to 15 agents; Step 4 agent list updated; ASCII workflow map updated; model tier and artifact/gate tables annotated with "(sdd-evolution module)".

### BLD-03 — Per-Module PLAYBOOK Files Created (✅ Complete)

- **Created `PLAYBOOK-sdd-evolution.md`** — full documentation including Meta Agents section (builder collaboration, step-by-step examples, SDD conventions), evolution workflow, and 12-agent reference table. Content migrated from main PLAYBOOK.
- **Created `PLAYBOOK-core-be.md`** — backend module playbook with step-by-step workflow and recommended scenarios. Content migrated from main PLAYBOOK.
- **Created `PLAYBOOK-std-fe.md`** — frontend module playbook with tailored packs (stratos-core, enterprise-search), composition recipes, installation order, and execution mode guidance.
- **Created `PLAYBOOK-aws-fe.md`** — Acme FE module playbook with dual-agent-review pack, composition recipes, and pack prompts.

### BLD-04 — PLAYBOOK.md Restructured (✅ Complete)

- **Meta Agents section** condensed to summary table with link to `PLAYBOOK-sdd-evolution.md` (was ~143 lines of examples/diagrams).
- **Available Modules table** — added `sdd-evolution` entry; added cross-reference links to all 4 per-module playbooks.
- **Step-by-Step: Core-BE** condensed to link to `PLAYBOOK-core-be.md`.
- **Frontend Tailored Packs** condensed to summary table with links to `PLAYBOOK-std-fe.md` and `PLAYBOOK-aws-fe.md`.
- **Test suite:** 259 tests passing (125 framework integrity + 134 integration/unit).

---

## Wave 14.1 — Post-Wave Cleanup (April 17, 2026)

> **Plan:** [`POST-WAVE-14-REVIEW-REPORT.md`](_plan/POST-WAVE-14-REVIEW-REPORT.md) (11 deviations)
> **Status:** ✅ Complete

### DEV-01 — Duplicate Test File Removed (✅ Complete)

- **Deleted `_tests/test_04_framework_integrity.py`** — byte-for-byte duplicate of `test_framework_integrity.py` (MD5 identical); was inflating test count from 121 to 242. Canonical Layer 4 tests now run once in `test_framework_integrity.py` only.

### DEV-02 — Module Registry Updated (✅ Complete)

- **Added `sdd-evolution` to `.sdd-modules/registry.json`** — module existed on filesystem since Wave 14 Phase S but was missing from the registry. Registry version bumped to 1.1.0.

### DEV-03 — EXPECTED_AGENTS Completed (✅ Complete)

- **Added 7 missing agents to `EXPECTED_AGENTS` in `_tests/test_framework_integrity.py`** — `agent-builder`, `instruction-builder`, `prompt-builder`, `guidance-builder`, `workflow-builder`, `tech-context-maintainer`, `brainstorming`. List now contains all 20 agents matching `.github/agents/` filesystem. Bidirectional validation via `test_agent_count_matches` catches both missing and unexpected agents. Test count: 129.

### DEV-04 — Missing Template Added to Tests (✅ Complete)

- **Added `data-model-template.md` to `EXPECTED_TEMPLATES`** in `_tests/test_framework_integrity.py` — template existed in `.specify/templates/` and was referenced by `architect.agent.md` but was not validated by the test suite. `EXPECTED_TEMPLATES` now has 10 entries. Test count: 130.

### DEV-05 — Duplicate Section 4.12 Fixed (✅ Complete)

- **Renumbered second `# 4.12 Adapters canonical source` to `# 4.13`** — cascaded renumbering through all subsequent sections. Sequential numbering now runs 4.1–4.19 with no duplicates.

### DEV-06 — Duplicate Section 4.15 Fixed (✅ Complete)

- **Renumbered duplicate `# 4.15 Wave 14 Phase S` to `# 4.19`** — resolved as part of full sequential renumbering. Added missing `# 4.18 Wave 14 Phase R — Documentation alignment` section header for `TestWave14PhaseR`.

### DEV-07 — PLAYBOOK Date Updated (✅ Complete)

- **Updated PLAYBOOK.md date from `April 15, 2026` to `April 17, 2026`** — now matches README.md version header date.

### DEV-08 — Guidances Directory Created (✅ Complete)

- **Created `.github/guidances/.gitkeep`** — the `guidance-builder` agent references this directory in 12 places but it did not exist. Now Git-tracked so users don't encounter missing-directory errors on first invocation.

### DEV-09 — Autonomy Command Added to Taxonomy (✅ Complete)

- **Added `autonomy` to `extensions` domain in `command-taxonomy.json`** — command was registered in CLI dispatcher and had backing scripts but was missing from the canonical taxonomy. Also added `"J": ["autonomy"]` to `phaseMapping`. Updated `test_taxonomy_covers_all_commands` expected list to 21 commands.

### DEV-10 — Scripts README Created (✅ Complete)

- **Created `.specify/scripts/README.md`** — catalogs all scripts with CLI mapping, purpose, and calling chain. Distinguishes CLI-mapped scripts (26) from internal helper scripts (4: `extension-resolve-conflicts`, `memory-index`, `worktree-create`, `autonomy-evidence.py`). Documents the `sdd <command> → CLI module → shell script → internal script` chain.

### DEV-11 — Prompts README Catalog Created (✅ Complete)

- **Created `.github/prompts/README.md`** — catalogs all 27 prompts organized by phase (Foundation, Requirements, Implementation, Quality, Diagnostic, Learning). Each entry includes the filename and one-line description extracted from YAML frontmatter. Improves team discoverability per SDD's team-oriented design principle.

---

## Wave 14 — Consolidation, Robustness & Meta-Evolution (April 17, 2026)

> **Plan:** [`WAVE-14-CONSOLIDATION-AND-META-EVOLUTION-PLAN.md`](_plan/WAVE-14-CONSOLIDATION-AND-META-EVOLUTION-PLAN.md) (Phases O–S)
> **Tasks:** 36 total (4 Phase O + 6 Phase P + 5 Phase Q + 5 Phase R + 16 Phase S)
> **Status:** ✅ Complete

### Phase O — Critical Fixes (✅ Complete)

- **O.1 Populated `copilot-instructions.md`** — Was empty; now provides global SDD context including agent folder reference, constitution-first protocol, session startup checklist, anti-pattern summary, quality gates, and context-window discipline (60+ lines)
- **O.2 Added `SPEC_MEMORY_PATH` to `.env.example`** — Documented with default path `./.specify/memory`
- **O.3 Added HTTP timeouts to MCP servers** — `confluence-server` and `jira-server` now use `timeout=30` on all httpx calls (spec-memory-server is filesystem-only, no HTTP)
- **O.4 Sanitized CQL input in confluence-server** — Added `_sanitize_cql_value()` to escape special characters before CQL concatenation; eliminated raw string interpolation injection vector

### Phase P — CLI & Script Hardening (✅ Complete)

- **P.1 Finalized `sdd spell`** — Replaced simulation with real context resolver that reads the prompt file, builds a context bridge from feature artifacts (spec, decisions, constitution excerpt), and outputs copyable markdown; `--dry-run` shows what would be collected
- **P.2 Hardened `skill-list.sh`** — Now reads from SKILL-INDEX.md and produces formatted table with NAME/PHASE/PURPOSE columns; exits 1 on missing index
- **P.3 Hardened `skill-validate.sh`** — Validates skill files have required sections (Steps, Output Contract); reports pass/fail; searches both `.specify/skills/` and `.github/skills/`
- **P.4 Hardened `worktree-create.sh`** — Now copies `.specify/specs/{id}/` into the created worktree
- **P.5 Hardened `memory-sync.sh`** — Added freshness drift detection (>24h threshold), conflict detection between session-state and feature-meta, structured sync report
- **P.6 Hardened `memory-doctor.sh`** — Checks all 6 memory files, validates constitution has Articles I–VI, detects stale entries (>7 days), prints structured diagnostic report

### Phase Q — MCP Server Security & Testing (✅ Complete)

- **Q.1 Unit tests for spec-memory-server** — 8 tests covering list_resources, read_resource, set/get active feature, add_decision, get_constitution_section (existing/missing)
- **Q.2 Unit tests for confluence-server** — 8 tests covering CQL sanitization (3 tests), search (2 tests), get_page, list_space_pages, HTTP timeout verification
- **Q.3 Unit tests for jira-server** — 7 tests covering get_issue (2 tests), search_issues, epic/sprint JQL, HTTP timeout, error handling
- **Q.4 Tests for generate-adapters.py** — 9 tests covering canonical loading, tier routing (4 tests), VS Code adapter (2 tests), Cursor adapter (2 tests), model map (2 tests)
- **Q.5 Layer 4 tests for sdd-evolution module** — 12 tests added to `test_framework_integrity.py`: module.json validity, 7 agents present, 2 instructions present, 5 prompts present, 3 templates present, 2 scaffolds complete, README exists, copilot-instructions-supplement exists, setup-module.sh executable, agents have boundary rules and YAML frontmatter, module.json files match filesystem

### Phase R — Documentation Alignment (✅ Complete)

- **R.1 Updated REQUIREMENTS.md** — Date to April 17 2026; closed gaps #1 (PS already documented), #2 (added `pip install mcp-atlassian` + GitHub URL), #4 (fixed in Phase O); #5 deferred with rationale
- **R.2 README.md version header** — Added `> **v4.3** — April 17, 2026` after title
- **R.3 Prompt count aligned** — PLAYBOOK updated from 26 to 27 prompts; added missing `retrospective.prompt.md` row to table
- **R.4 Extension vs module terminology** — Added distinct “Extension” entry in PLAYBOOK Glossary; added “Module vs Extension” clarification in MIGRATION-GUIDE Step 12
- **R.5 TEAM-ADOPTION-GUIDE v2.0** — Version bumped; added Waves 12–14 features section with rollout plan; Month 5+ autonomy-guided in progressive mandate; cross-functional team guidance table

### Phase S — Meta-Evolution Module (✅ Complete)

- **S.1 Module manifest** — Created `module.json` for `sdd-evolution` module: 7 agents, 2 instructions, 5 prompts, 3 templates, 2 scaffolds, post-install hook
- **S.2 Framework Analyst agent** — Adapted from parent workspace `analyse-framework.agent.md`; 5-phase analysis process (Discovery→Classify→Analyse→Write→Validate); model-tier: deep; handoffs to comparator and evolver
- **S.3 Framework Comparator agent** — Adapted from `compare-frameworks.agent.md`; 4-phase comparison process; master table with 18+ dimensions; handoffs to evolver and analyst
- **S.4 Framework Updater agent** — Adapted from `update-frameworks.agent.md`; 7-step workflow (pull repos, read WHATSNEW, investigate changes, update WHATSNEW, update analyses minor, update comparisons minor, verify); model-tier: standard
- **S.5 SDD Evolver agent** — Adapted from `evolve-enterprise-sdd.agent.md`; 6-step harvest process; references sdd-philosophy constraints; outputs numbered evolution sections
- **S.6 Evolution Planner agent** — Adapted from `improvement-plan.agent.md`; creates phased plans with priority/effort/dependency/AC; mandatory T/V/Z closure phases
- **S.7 Module Designer agent** — NEW agent for interactive module scaffolding; 4-step Q&A workflow; generates complete module directories
- **S.8 Extension Designer agent** — NEW agent for interactive extension scaffolding; lightweight alternative to module designer
- **S.9 SDD Philosophy instruction** — 9 inviolable constraints, design boundaries table, feature evaluation criteria, plan task conventions
- **S.10 Framework Repos instruction** — Canonical map of 9 tracked public repos with analysis file locations
- **S.11 Five prompt files** — `analyse-framework`, `compare-frameworks`, `evolve-sdd`, `design-module`, `design-extension`
- **S.12 Templates & scaffolds** — 3 document templates (analysis, comparison, evolution-section); 2 scaffold directories (module-scaffold with 3 templates, extension-scaffold with 2 templates)
- **S.13 Module README** — Comprehensive documentation: component inventory, workflow overview, file structure, installation/removal
- **S.14 Copilot instructions supplement** — Module context for Copilot: lists all 7 agents, key concepts, important files
- **S.15 Post-install hook** — `setup-module.sh` creates `_evolution/` directory with placeholder EVOLUTION.md and WHATSNEW.md
- **S.16 Module validation** — 12 structural tests added to test suite; 255 tests passing

---

## Wave 13 — Autonomy Diagnostics Hardening (April 15, 2026)

> **Plan:** [`MASTER-PLAN.md`](_plan/MASTER-PLAN.md) (§17, Phase N)
> **Tasks:** 3 (N.1, N.2, N.3)
> **Status:** ✅ Complete

Wave 13 implemented the targeted autonomy-loop hardening backlog identified in `ENTERPRISE-SDD-EVOLUTION.md` §15.

- **N.1 Per-attempt evidence pack**
  - New evidence sync engine: `.specify/scripts/autonomy-evidence.py`
  - Per-cycle artifacts under `.specify/checkpoints/autonomy-runs/{feature}/cycle-{NNN}/`
  - Snapshots include `prompt.md`, `result.md`, and structured `verdict.json`

- **N.2 Structured verifier verdict schema**
  - Verdict status normalized to `passed|retry|blocked`
  - `confidence` and `repair_hint` serialized consistently for autonomous diagnostics
  - `sdd status <feature> --autonomy` now surfaces structured autonomy summary fields

- **N.3 Derived progress ledger**
  - `autonomy-progress.md` generated per feature from checkpoint evidence
  - Includes current cycle, latest verdict, blocker, and next suggested action

Validation notes:
- Full `_tests/` suite passed after CLI argument and pytest config alignment fixes.
- Bash/PowerShell parity preserved for autonomy status surfaces.

### Cumulative Baseline After Wave 13

| Component | Count |
|-----------|-------|
| Agents | 20 |
| Prompts | 27 |
| Shared Instructions | 14 |
| Curated Skills | 4 (`sdd-auto-implement`, `sdd-challenge`, `sdd-spec-review`, `pattern-analyze`) |
| CLI Commands | 23 (adds `autonomy status`; includes `context compile`, `retrospect`) |

---

## Wave 12 — Multi-Framework Harvest & Behavioral Discipline (April 14, 2026)

> **Plan:** [`WHATSNEW-HARVEST-IMPLEMENTATION-PLAN.md`](_plan/WHATSNEW-HARVEST-IMPLEMENTATION-PLAN.md), [`KARPATHY-HARVEST-IMPLEMENTATION-PLAN.md`](_plan/KARPATHY-HARVEST-IMPLEMENTATION-PLAN.md)
> **Phases:** N, O, P, T, V, Z (33 tasks) + Karpathy harvest (7 steps)
> **Status:** ✅ Complete

### Multi-Framework WHATSNEW Harvest (§14 — 9 adopted features, 33 tasks)

Improvements harvested from the April 14, 2026 public framework updates (AI-RPI Protocol v1.1.0, BMAD Method v6.3.0, GSD v1 v1.36.0, GSD-2 v2.74.0).

**Phase N — Behavioral Safety & Session Coherence (6 tasks):**
- Anti-fabrication turn-taking guards in `clarification.agent.md` and `requirement-analyst.agent.md`
- Turn-taking fabrication pattern added to `anti-patterns.instructions.md` sycophancy section
- New `team-preferences.md` template in `.specify/memory/`
- Team-preferences load directive in `question-format.instructions.md`
- Session Startup Checklist (5-step ordered startup sequence) in shared instructions

**Phase O — Workflow Quality (6 tasks):**
- New `sdd context compile` CLI subcommand — generates `feature-{slug}-context.md` for quick session resume
- Context bridge template updated with link to compiled feature context
- New `sdd-spec-review` curated skill in `.github/skills/` — maps PR diff against spec ACs and TCs
- Review agent handoff hint for `sdd-spec-review` skill
- New `retrospective.prompt.md` — structured post-feature learning template
- New `sdd retrospect` CLI entry point — prints/saves retrospective output

**Phase P — Developer Experience Tuning (7 tasks):**
- Opt-in TDD pipeline: `tdd_mode` in constitution + `--tdd` flag for `sdd gate 2`
- New `tdd-enforce.instructions.md` shared instruction file (14th instruction)
- New `pattern-analyze` curated skill in `.github/skills/` — scans codebase for structural patterns
- Pattern-analyze invocation hint in `tech-context-maintainer.agent.md`
- Context-window thinning: `context_budget` section in `ceremony-levels.instructions.md`
- Model-tier verbosity hints in `agent-builder.agent.md`

**Phase T/V — Tests (10 tasks):**
- 7 new test assertions in `test_framework_integrity.py` covering all Wave 12 artifacts
- Full 5-layer test suite executed and verified green

**Phase Z — Documentation (4 tasks):**
- README.md, PLAYBOOK.md, ENTERPRISE-SDD-ANALYSIS.md, and ENTERPRISE-SDD-EVOLUTION.md updated

### Karpathy Skills Behavioral Harvest (§13 — 4 improvements, 7 steps)

Improvements harvested from the Karpathy-Inspired Claude Code Guidelines analysis.

- **Orphan cleanup precision rule** (Rule 6) — agents clean up only changes THEY made unused; never pre-existing dead code
- **Simplicity self-test** — "Would a senior engineer say this is overcomplicated?" checkpoint added to Rule 2
- **Verification loop pattern** — lightweight `[Step] → verify: [check]` micro-task format in Software Engineer agent
- **Anti-pattern code examples** — new `anti-patterns-examples.instructions.md` with before/after diffs for all 6 rules

### Cumulative Baseline After Wave 12 (Historical Snapshot)

| Component | Count |
|-----------|-------|
| Agents | 20 |
| Prompts | 27 |
| Shared Instructions | 14 |
| Curated Skills | 4 (`sdd-auto-implement`, `sdd-challenge`, `sdd-spec-review`, `pattern-analyze`) |
| CLI Commands | 22 (including `context compile`, `retrospect`) |

---

## Wave 11 — Tailored Evolution (April 5–11, 2026)

> **Plan:** [`MASTER-PLAN.md`](_plan/MASTER-PLAN.md) (Phases H–M)
> **Completion report:** [`PHASE-M-COMPLETION-REPORT.md`](_plan/PHASE-M-COMPLETION-REPORT.md)
> **Verification:** [`verification-matrix-wave11.md`](_plan/verification-matrix-wave11.md) (31 tests, all pass)
> **Pilot:** [`adoption-pilot-results.md`](_plan/adoption-pilot-results.md) (4.05/5 average confidence)
> **Tasks:** 50 across 6 phases
> **Status:** ✅ Complete

### Phase H — Memory-First Operating Layer (10 tasks)

- Indexed structured memory system with freshness tracking
- `sdd memory status` / `sdd memory sync` / `sdd memory doctor` CLI commands
- Memory integration in reporting and gate validation
- Operating loop: `Phase Start → sdd memory status → execute → sdd memory sync → sdd gate`

### Phase I — Command + Skill Convergence (8 tasks)

- Command taxonomy (`command-taxonomy.json`) with lifecycle-stage grouping
- 8 curated command prompts: `/challenge`, `/plan-implementation`, `/assert-quality`, `/review-functional`, `/review-code`, `/test-journey`, `/debug-5-whys`, `/reproduce-bug`
- 2 curated skills: `sdd-auto-implement` (multi-step autonomous implementation) and `sdd-challenge` (critical challenge analysis)
- `sdd skill list|validate|run|validate-mapping` CLI surface
- `sdd spell` command — context-aware prompt execution by name

### Phase J — Controlled Autonomy (7 tasks)

> **Decision analysis:** [`PHASE-J-AUTONOMY-DECISION-ANALYSIS.md`](_plan/PHASE-J-AUTONOMY-DECISION-ANALYSIS.md)
> **Implementation plan:** [`PHASE-J-IMPLEMENTATION-PLAN.md`](_plan/PHASE-J-IMPLEMENTATION-PLAN.md)

- Governed-hybrid autonomy model (Alexia governance + Ralph structural invariants)
- 3 execution modes: `standard` (default), `autonomous-guided`, `autonomous-governed`
- `autonomy-policy.instructions.md` shared instruction
- `/autonomous-implement` prompt with single-cycle discipline
- `sdd autonomy status` CLI command
- 7-step runtime protocol: Read → Select → Intent → Execute → Persist → Stop → Resume
- Safety trial: proven no gate bypass in any mode

### Phase K — Tailored Extension Specialization (8 tasks)

- Extension specialization schema (`sdd-tailored-extension.schema.json`)
- Namespace enforcement: `fe-*` / `aws-fe-*` for instructions, `/fe/*` / `/aws-fe/*` for prompts
- Conflict detection and resolution: `sdd extension validate|doctor|resolve-conflicts`
- Extension lifecycle hooks in gate validation scripts

### Phase L — Frontend Tailored Packs (9 tasks)

> **Checklist:** [`PHASE-L-CHECKLIST.md`](_plan/PHASE-L-CHECKLIST.md) (46/46 items complete)

- 3 production-ready frontend extension packs:
  - `frontend-stratos-core` — React/Vite/Stratos microfrontend patterns
  - `frontend-enterprise-search` — search feature patterns and hooks
  - `frontend-dual-agent-review` — dual-agent review workflow with agent patches and templates
- 5 new domain-specific prompts (`fe-scaffold`, `fe-design`, `fe-search`, etc.)
- Packs stack conflict-free with clean diagnostics

### Phase M — Validation & Adoption (8 tasks)

> **Completion report:** [`PHASE-M-COMPLETION-REPORT.md`](_plan/PHASE-M-COMPLETION-REPORT.md)
> **Parity validation:** [`parity-validation-results.md`](_plan/parity-validation-results.md)

- Migration guide created (MIGRATION-GUIDE.md v2.0)
- Verification matrix: 31 tests across 8 dimensions — 30/31 pass (1 deferred: Linux CI)
- Bash/PowerShell parity validated: 29/29 scripts at 100% parity
- Adoption pilot: standard mode 4.2/5, autonomous-guided 3.9/5 (both exceed ≥3.8 threshold)
- OpenSpec/BMAD minimum viable harvest: artifact graph + explain-mode diagnostics
- Rollout documentation: README, PLAYBOOK v4.2, Team Adoption Guide updated

---

## Wave 10 — Optimization (April 4–5, 2026)

> **Plan:** [`MASTER-PLAN.md`](_plan/MASTER-PLAN.md) (Phase G)
> **Tasks:** 12
> **Status:** ✅ Complete

### Phase G — Cost Tracking, Routing, Worktree Isolation

- **Cost tracking**: `cost-tracking.instructions.md` shared instruction for per-task token/cost ledger with budget ceilings
- **Dynamic model routing**: `sdd route` CLI command — routes commands to cheapest model tier matching task complexity
- **Worktree isolation**: `sdd worktree create|ship` — feature-level git worktree isolation with 3 git modes
- Operational visibility improvements through cost logs and routing reports

---

## Wave 9 — Portability (April 3, 2026)

> **Completion report:** [`PHASE-F-COMPLETION-REPORT.md`](_plan/PHASE-F-COMPLETION-REPORT.md)
> **Review summary:** [`SESSION-PHASE-F-REVIEW-SUMMARY.md`](_plan/SESSION-PHASE-F-REVIEW-SUMMARY.md)
> **Tasks:** 25
> **Status:** ✅ Complete

### Phase F — CLI, Multi-IDE, Multi-LLM, Extensions, Issue Sync

- **Python CLI (`sdd`)**: 13 commands at launch — `init`, `new`, `gate`, `status`, `analyze`, `report`, `resume`, `bridge`, `module`, `adapters`, `preset`, `sync`, `spell`
- **5 IDE adapters**: VS Code/Copilot, Cursor, Claude Code, Windsurf, Codex — all generated from single canonical source via `sdd adapters generate`
- **Model-tier abstraction**: Article VI in constitution maps `light|standard|deep` to provider-specific models; all 20 agents tagged with `model-tier`
- **Extension framework**: `sdd-extension.json` schema + lifecycle hooks in gate scripts
- **3 workflow presets**: `sdd-preset-api`, `sdd-preset-event-driven`, `sdd-preset-monorepo`
- **Issue tracker sync**: `sdd sync push|pull` for GitHub + GitLab backends (bidirectional)
- **User Modules system**: `.sdd-modules/` with `install|remove|list|update` lifecycle; 3 modules shipped: `core-be`, `std-fe`, `aws-fe`

---

## Waves 6–8 — Cross-Framework Feature Harvest (March 23 – April 2, 2026)

> **Source:** [ENTERPRISE-SDD-EVOLUTION.md §6–7](../ENTERPRISE-SDD-EVOLUTION.md)
> **Items harvested:** 20 from 6 public frameworks (OpenSpec, BMAD Method, AI-RPI Protocol, Spec Kit, Get Shit Done, GSD-2)
> **Status:** ✅ All 20 items complete

### Wave 8 — Context & Verification (4 features)

- **Context isolation strategy** — prevent context rot across long sessions via context bridges and structured memory
- **Goal-backward verification** — phase goals checked systematically (backward-pass validation)
- **Stuck detection** — `stuck-detection.instructions.md` with oscillation prevention, 80% threshold, 2-strike escalation
- **Structured memory protocol** — 5-file `.specify/memory/` system with constitution, tech-context, decisions, challenges, session-log

### Wave 7 — Adaptive Process (4 features)

- **Adaptive ceremony levels** — `ceremony-levels.instructions.md` with ultra-light, standard, and full modes
- **Crash recovery** — auto-restart with state checkpointing and lock files (`resume-feature.sh/.ps1`)
- **Parallel execution markers** — `[P]`/`[S]`/`[T]` markers for parallelizable tasks
- **Cross-platform scripts** — Bash + PowerShell parity across all automation scripts

### Wave 6 — AI Reliability (4 features)

- **Anti-pattern rules** — `anti-patterns.instructions.md` with 5 rules: anti-sycophancy, anti-eager-beaver, anti-hallucination, anti-anchoring, confidence calibration
- **[NEEDS CLARIFICATION] markers** — explicit uncertainty markers in agent output
- **Confidence calibration** — Low/Medium/High confidence ratings for agent assertions
- **Reviewer focus guidance** — directs human attention to high-risk areas

---

## Waves 0–5 — AI Framework Adoption & Foundation (March 14–26, 2026)

> **Source:** [ENTERPRISE-SDD-EVOLUTION.md §2, §9](../ENTERPRISE-SDD-EVOLUTION.md)
> **Items adopted:** 16 from AI Framework + 6 additional improvements
> **Status:** ✅ All 22 items complete

### Wave 5 — Meta Agents

- **Agent Builder** + **Instruction/Guidance Builder** — meta agents for extending the framework itself

### Wave 4 — Developer Experience

- **RefactoringPal agent** — tech debt analysis and refactoring guidance
- **Tech Context Maintainer agent** — architectural drift detection
- **Prompt Library** — 25+ pre-built prompts for common workflow scenarios

### Wave 3 — Pipeline Expansion

- **Brainstorming Agent** — pre-Phase 0 ideation with 12-phase workflow
- **Gherkin Analyst Agent** — BDD specialist for Phase 3.1b

### Wave 2 — Design Depth

- **Architect design phases** — 5-phase architecture workflow with NEW/EXTEND/HYBRID classification
- **API patterns shared instruction** — `api-patterns.instructions.md`
- **Messaging patterns shared instruction** — `messaging-patterns.instructions.md`

### Wave 1 — Traceability & Intelligence

- **Story linking logic** — duplicate/relates/blocks detection in Requirement Analyst
- **Teaching mode** — RA mentoring alongside Vision/Detailed modes
- **Gate cross-reference validation** — automated traceability chain verification

### Wave 0 — Foundations

- **Shared instruction files** — `.instructions.md` pattern for cross-cutting concerns
- **Question format standard** — Q-NNN structured question format
- **Phase field in YAML** — `phase: "X.Y"` in all agent frontmatter
- **Jira/Confluence MCP integration** — `mcp-atlassian` tool declarations in RA agent

---

## Pre-Wave — Critical Review (March 14–16, 2026)

> **Source:** [ENTERPRISE-SDD-EVOLUTION.md §1](../ENTERPRISE-SDD-EVOLUTION.md)

- **22 issues found** across documentation, logic, cross-references, scripts, design, and templates
- **18 issues fixed** on March 16, 2026
- **3 issues by design** (documented as known limitations: Issues 9, 12, 16)
- **1 issue deferred** (duplicate shell script concern)

Key fixes:
- Agent count inconsistency (11 vs. 20) corrected in PLAYBOOK
- Missing `@workflow-builder` added to registries
- `@test-explorer` → `@gherkin-analyst` handoff added
- Review agent post-approval handoff redesigned
- Shell script Windows compatibility documented
- Gate 4 silent swallowing of Gate 1–3 output fixed

---

## Pre-Wave — Initial Implementation

- Enterprise SDD Workflow created with 20 specialized AI agents
- 6-phase pipeline: Foundation → Specification → Design → Preparation → Implementation → Ship
- 4 quality gates with automated validation
- Constitution-first governance model
- Full traceability chain: US → AC → TC → Task → Code
- Template-driven artifact generation
- 3 custom MCP servers: Confluence, Jira, Spec Memory

---

## Additional Harvests

### OpenSpec + BMAD Compatibility Harvest (April 9, 2026)

> **Source:** [ENTERPRISE-SDD-EVOLUTION.md §12](../ENTERPRISE-SDD-EVOLUTION.md)

- Artifact graph visibility (`sdd status --graph`)
- Workflow-map driven onboarding (one-page map in PLAYBOOK)
- Module catalog discoverability (`sdd module list --details`)
- Human-readable workflow diagnostics (explain-mode with actionable next steps)

### User Modules Architecture (March 26, 2026)

> **Source:** [ENTERPRISE-SDD-EVOLUTION.md §10–11](../ENTERPRISE-SDD-EVOLUTION.md)

- Modular, additive package system in `.sdd-modules/`
- `core-be` — Java 21 / Quarkus / DDD / Kafka / PostgreSQL (24 instructions, 3 constitution articles)
- `std-fe` — React 19 / Vite / Stratos microfrontend (5 instructions)
- `aws-fe` — React / Redux Toolkit / Stratos (9 instructions, 46 prompts)

### Additional AI Framework Improvements (March 26, 2026)

> **Source:** [ENTERPRISE-SDD-EVOLUTION.md §9](../ENTERPRISE-SDD-EVOLUTION.md)

- `applyTo` glob-scoping for instruction files
- Materialize-then-compact timing rules
- TCM-before-architecture onboarding pattern
- Agent-consumable project scaffolding templates
- Model tier per-agent-type recommendations
- Story batch sizing guidance (3–7 related stories per pipeline run)

---

## Summary Timeline

| Date | Milestone |
|------|-----------|
| March 14, 2026 | Critical review: 22 issues identified |
| March 16, 2026 | 18 issues resolved |
| March 23, 2026 | 6-framework expansion; Waves 6–8 cross-framework harvest (20 items) |
| March 26, 2026 | AI Framework updates (6 additional items); User Modules architecture |
| April 3, 2026 | Wave 9 — Phase F complete: CLI, 5 IDE adapters, extensions, issue sync (25 tasks) |
| April 4–5, 2026 | Wave 10 — Phase G complete: cost tracking, routing, worktrees (12 tasks) |
| April 5–11, 2026 | Wave 11 — Phases H–M complete: memory, skills, autonomy, frontend packs (50 tasks) |
| April 9, 2026 | OpenSpec + BMAD compatibility harvest |
| April 11, 2026 | Wave 11 release gate passed (PHASE-M-COMPLETION-REPORT) |
| April 14, 2026 | Wave 12 — Karpathy harvest (4 items) + WHATSNEW harvest (9 features, 33 tasks) |
| April 15, 2026 | Wave 13 — autonomy diagnostics hardening complete (3 tasks: N.1/N.2/N.3) |
| April 17, 2026 | Wave 14 — Consolidation, Robustness & Meta-Evolution (36 tasks, Phases O–S) |
| April 17, 2026 | Wave 14.1 — Post-Wave Cleanup complete (11 deviations resolved: DEV-01–DEV-11) |
| April 17, 2026 | Wave 14.2 — Builder agents migrated to sdd-evolution module; per-module PLAYBOOK files created |

**Total tasks delivered:** 175+ across Waves 0–14.2
