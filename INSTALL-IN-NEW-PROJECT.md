# Install Enterprise SDD in a New Project

This guide explains how to install and operate Enterprise SDD in a project that does not currently contain the framework.

It supports two adoption models:
- **Model A (Recommended for fast start):** start from the Enterprise SDD repository as your project baseline.
- **Model B (Recommended for existing repos):** add Enterprise SDD as a submodule/tooling source, then sync framework assets into your project root.

The structure follows the same practical style used in `ai-framework/README.md` (add framework, customize, verify).

## Prerequisites

- VS Code with GitHub Copilot + Copilot Chat extensions
- Python >= 3.11
- Git
- Bash (or Git Bash/WSL on Windows)

## Model A: Start Directly from Enterprise SDD

Use this when your repository is new and you want Enterprise SDD as the default project structure.

```bash
git clone https://github.com/your-org/enterprise-sdd-workflow.git my-project
cd my-project
chmod +x .specify/scripts/*.sh
./.specify/scripts/init.sh
pip install -e .specify/cli
```

Then initialize your first feature:

```bash
sdd new my-first-feature --template standard --dry-run
```

## Model B: Add Enterprise SDD to an Existing/New App Repo

Use this when you already have an application repository and want to adopt Enterprise SDD tooling.

### Step 1: Add framework source

```bash
# from your application repository root
git submodule add https://github.com/your-org/enterprise-sdd-workflow.git tools/enterprise-sdd
git submodule update --init --recursive
```

### Step 2: Sync framework assets into project root

```bash
# from your application repository root
rsync -a tools/enterprise-sdd/.github/ .github/
rsync -a tools/enterprise-sdd/.specify/ .specify/
rsync -a tools/enterprise-sdd/.sdd-extensions/ .sdd-extensions/
rsync -a tools/enterprise-sdd/.sdd-modules/ .sdd-modules/
cp -n tools/enterprise-sdd/.env.example .env.example.sdd || true
```

If you cannot use `rsync` (for example on Windows without WSL), copy the same directories manually.

### Step 3: Initialize and install CLI

```bash
chmod +x .specify/scripts/*.sh
./.specify/scripts/init.sh
pip install -e tools/enterprise-sdd/.specify/cli
```

### Step 4: Verify installation

Run these checks from your project root:

```bash
sdd --version
sdd init --dry-run
sdd new install-smoke --template standard --dry-run
```

In VS Code Copilot Chat:
- Type `@` and verify agent list is visible.
- Run `@constitution` to create `.specify/memory/constitution.md`.

## First Run Checklist

1. Create constitution with `@constitution`.
2. Create a feature scaffold with `sdd new <feature-name>`.
3. Populate artifacts (`business-context.md`, `spec.md`, `plan.md`, `test-cases.md`, `tasks.md`).
4. Validate gates using `sdd gate <feature-id> <1|2|3|4>`.

## Optional: Install Frontend Modules and Extension Packs

If your project is a React/Stratos microfrontend, install domain-specific modules and extension packs:

```bash
# Install frontend modules
sdd module install std-fe
sdd module install aws-fe          # only for Acme FE projects

# Install extension packs (order matters: base pack first)
sdd extension install sdd-extension-frontend-stratos-core
sdd extension install sdd-extension-frontend-enterprise-search   # if search features are needed
sdd extension install sdd-extension-frontend-dual-agent-review   # if dual-agent review is needed
```

See the **Frontend Tailored Packs** section in `PLAYBOOK.md` for composition recipes and execution mode guidance.

## Update Strategy (Model B)

When Enterprise SDD is updated:

```bash
git submodule update --remote --recursive
rsync -a tools/enterprise-sdd/.github/ .github/
rsync -a tools/enterprise-sdd/.specify/ .specify/
rsync -a tools/enterprise-sdd/.sdd-extensions/ .sdd-extensions/
rsync -a tools/enterprise-sdd/.sdd-modules/ .sdd-modules/
```

Re-run lightweight verification after each update:

```bash
sdd init --dry-run
sdd skill validate-mapping
```

## Choosing an Install Profile *(Wave 23 §23.A.15–§23.A.18)*

`sdd init` supports three mutually-exclusive install profiles. The profile is recorded in `.specify/install-profile.json` and influences the cold-start surface and `sdd doctor --suggest-upgrade` recommendations.

| Profile | Tier | When to use |
|---------|------|-------------|
| `--minimal` | 1 | Solo experimentation, tiny repos, hackathons. Just the cold-start surface, no optional modules. |
| (default) `--full` | 3 | Teams adopting the full Enterprise SDD workflow, including all phases, agents, gates, modules. |
| `--upgrade` | promote to ≥ 2 | Existing minimal install that has outgrown tier 1; no-op if already at tier ≥ 2. |

```bash
sdd init --minimal               # smallest install
sdd init                         # default = --full
sdd init --upgrade               # promote tier
sdd doctor --suggest-upgrade     # recommend a tier bump based on usage
```

After installation, `sdd skill list` shows the cold-start surface (6 namespace meta-skills); `sdd skill list --flat` lists every skill on disk.

## Troubleshooting

- If `sdd` is not found: verify `pip install -e .../.specify/cli` completed in the active Python environment.
- If agents do not appear in chat: confirm `.github/agents/` exists in project root.
- If scripts fail with permissions: re-run `chmod +x .specify/scripts/*.sh`.
- If gate validation fails immediately: ensure required artifacts are present under `.specify/specs/<feature-id>/`.

---

## Brownfield Onboarding

If your project already has existing documentation (PRDs, ADRs, design docs, API specs), you can accelerate SDD adoption by ingesting those documents into the SDD artifact structure.

### Step 1: Run document ingestion

```bash
sdd ingest ./docs/
```

This scans the target directory, classifies each document (ADR → constitution, PRD → spec, etc.), runs injection scanning on all content, and produces a mapping report at `.specify/ingest-mapping.md`.

### Step 2: Review the mapping report

Open `.specify/ingest-mapping.md` and verify:
- Document classifications are correct
- No injection warnings were raised
- Conflicts between overlapping documents are identified

### Step 3: Resolve conflicts and copy content

For each mapped document:
1. Create SDD features with `sdd new <feature-name>`
2. Copy classified content into the appropriate SDD templates
3. Remove the `[INGESTED — requires human review]` tags after verification
4. Run `sdd gate <feature-id> 1` to validate the ingested specs

### Workflow Summary

```
Existing docs → sdd ingest ./docs/ → Review mapping → sdd new per feature → Gate 1
```

> **Important:** Ingested artifacts are always flagged with `[INGESTED — requires human review]`. They must be verified by a human before passing any quality gate.

---

## Working with APM

If your project also uses [APM (Agent Package Manager)](https://github.com/microsoft/apm) to manage agent dependencies, both SDD and APM write to the same `.github/` subdirectories. Follow these conventions to avoid conflicts.

### File Ownership

| Owner | Tracked by | Scope |
|-------|-----------|-------|
| **SDD** | `.sdd-modules/registry.json` | Files under `.specify/`, module-installed instructions/skills |
| **APM** | `apm.lock.yaml` | Files installed by `apm install` from `apm.yml` dependencies |
| **Team** | Neither | Directly authored instructions, skills, agents, prompts |

### Recommended Directory Layout

- **SDD module files:** `.github/instructions/sdd-*`, `.github/skills/sdd-*`
- **APM package files:** `.github/instructions/<package-name>/`, `.github/skills/<package-name>/`
- **Team-authored files:** `.github/instructions/<domain>.instructions.md`, `.github/agents/<role>.agent.md`

Avoid flat namespace collisions by using directory or name prefixes that make ownership obvious.

### Integrity Verification

Run **both** tools for comprehensive coverage:

- `sdd doctor` — verifies SDD-managed files (registry-tracked hashes, instruction sizing, hidden Unicode)
- `apm audit` — verifies APM-managed files (lockfile consistency, content security, policy compliance)

Neither tool should verify the other's files. `sdd doctor` detects `apm.lock.yaml` and prints an INFO message reminding operators to run `apm audit` separately.

### Install Order

1. `apm install` first (infrastructure layer — resolves community packages)
2. `sdd module install <module>` second (SDD-specific modules may override or extend APM defaults)
