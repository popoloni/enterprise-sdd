# Migration Guide

> **Version:** 2.0
> **Date:** April 11, 2026
> **Plan governance:** Active roadmap execution status is tracked in `_plan/MASTER-PLAN.md`. All Waves 9–11 (Phases F–M) are complete.

This guide covers every migration path into the current Enterprise SDD baseline:

| Starting Point | Target Section |
|----------------|---------------|
| **Pre-Wave 9** (v3 — VS Code + Copilot only) | [Part 1: Migrating from v3](#part-1-migrating-from-v3-pre-wave-9) |
| **Wave 9–10** (CLI, adapters, cost tracking in place) | [Part 2: Adopting Wave 11 Features](#part-2-adopting-wave-11-features) |
| **New project (no Enterprise SDD yet)** | See [INSTALL-IN-NEW-PROJECT.md](INSTALL-IN-NEW-PROJECT.md) |

> **Scope note:** If your repository was initialized recently with the current baseline, most steps are already applied. Skip directly to Part 2 if you only need Wave 11 features.

---

## Part 1: Migrating from v3 (Pre-Wave 9)

> **v3** = any installation before Wave 9 (VS Code + GitHub Copilot only)
> **Current baseline** = Waves 9–11 delivered (CLI, multi-IDE adapters, extensions/presets, issue sync, structured memory, skills, user modules, controlled autonomy, frontend packs)

### What's New Since v3

| Feature | v3 | Current |
|---------|----|----|
| IDE support | VS Code only | VS Code, Cursor, Claude Code, Windsurf, Codex |
| Model configuration | Hardcoded in agent files | `model-tier` abstraction via constitution Article VI |
| CLI | Shell scripts only | `sdd` Python CLI + shell scripts |
| Extensions | None | `.sdd-extensions/` lifecycle hooks |
| Presets | `minimal/standard/full/enterprise` | + `sdd-preset-api`, `sdd-preset-event-driven`, `sdd-preset-monorepo` |
| Issue sync | Manual | `sdd sync push/pull` |
| Adapter generation | Manual edits | `sdd adapters generate` |
| Structured memory | Minimal constitution-only state | `sdd memory status|sync|doctor` + memory files + context bridges |
| Skills | None | Curated skills + `sdd skill list|validate|run|validate-mapping` |
| User modules | None | `.sdd-modules/` with install/update/remove lifecycle |
| Execution modes | None (implicit standard) | `standard`, `autonomous-guided`, `autonomous-governed` |
| Tailored frontend packs | None | 3 frontend extension packs (Stratos core, enterprise search, dual-agent review) |

### Step-by-Step (v3 → Current)

Use this sequence in order. Steps marked "Optional" can be skipped if you do not need that capability.

#### Step 1: Install the `sdd` CLI

```bash
pip install -e .specify/cli
```

Verify:
```bash
sdd --help
```

If you see the command list, the CLI is installed correctly.

#### Step 2: Add `model-tier` to Agent Files

v3 agent files have a hardcoded `model:` field. The current baseline adds `model-tier:` alongside it.

**Automated (recommended):**
```bash
sdd adapters generate --dry-run   # preview changes
sdd adapters generate             # apply changes
```

**Manual alternative:** For each `.github/agents/*.agent.md`, add `model-tier: <deep|standard|light>` after the `recommended-tier:` line.

The `model:` field is kept for backward compatibility with VS Code Copilot. The `model-tier:` field is used by `sdd adapters generate` for other IDEs.

#### Step 3: Add Article VI to constitution.md

Open `.specify/memory/constitution.md` and find the end of Article V. Add:

```markdown
## Article VI: Model Configuration

### 6.1 Model Tier Mapping

| Tier | Provider | Model | Fallback |
|------|----------|-------|----------|
| deep | Anthropic | Claude Opus 4.6 | Claude Sonnet 4.6 |
| standard | Anthropic | Claude Sonnet 4.6 | Claude Sonnet 3.5 |
| light | Anthropic | Claude Haiku 4.5 | Claude Haiku 3.5 |
```

Existing Article VI (Boundaries) and Article VII (Amendments) should be renumbered to VII and VIII respectively.

> **Note:** The constitution template (`.specify/memory/constitution.md`) already includes Article VI in current installations. This step is only needed for repos initialized before Wave 9.

#### Step 4: Generate Multi-IDE Adapters (Optional)

If you use Cursor, Claude Code, Windsurf, or Codex in addition to VS Code:

```bash
sdd adapters generate
```

This creates:
- `.cursor/rules/*.mdc` — Cursor rules
- `.claude/commands/*.md` + `CLAUDE.md` — Claude Code slash commands
- `.windsurfrules` — Windsurf rules
- `agents.md` — Codex agent table

Regenerate any time you modify `.specify/adapters/agents-canonical.json`.

#### Step 5: Set Up Extensions (Optional)

Create `.sdd-extensions/` if not present:

```bash
mkdir -p .sdd-extensions
```

See `.sdd-extensions/README.md` for extension authoring documentation.

#### Step 6: Apply a Preset (Optional)

```bash
sdd preset list                         # see all presets
sdd preset apply sdd-preset-api         # REST API project
sdd preset apply sdd-preset-event-driven # event-driven project
sdd preset apply sdd-preset-monorepo    # monorepo
```

#### Step 7: Set Up Issue Sync (Optional)

For GitHub:
```bash
gh auth login   # authenticate GitHub CLI
```

For GitLab:
```bash
export GITLAB_TOKEN=your-token
export GITLAB_PROJECT_ID=your-project-id
```

Then push existing tasks:
```bash
sdd sync push <feature-id>
```

After completing Steps 1–7, continue to **Part 2** to adopt Wave 11 features.

---

## Part 2: Adopting Wave 11 Features

> **Audience:** Teams already running Enterprise SDD Wave 9–10 (or those who just completed Part 1).
> **Prerequisite:** A working Enterprise SDD installation with CLI and adapters functional.

Wave 11 adds four capability layers on top of the existing Wave 9–10 foundation. **All changes are additive** — your existing standard workflow continues to work unchanged.

| Layer | What It Adds | Impact on Existing Workflow |
|-------|-------------|---------------------------|
| **Memory-First Operating Layer** (Phase H) | Indexed memory with freshness, sync, and doctor commands | New commands available; no changes to existing behavior |
| **Command + Skill Convergence** (Phase I) | 8 curated command prompts + 2 reusable skills | New prompts and `sdd skill run`; existing prompts unchanged |
| **Controlled Autonomy** (Phase J) | Optional `autonomous-guided` and `autonomous-governed` execution modes | Opt-in only; `standard` remains the default |
| **Tailored Frontend Extensions** (Phases K + L) | Extension specialization schema + 3 frontend packs | Optional add-ons; do not affect non-frontend projects |

### Step 8: Initialize Memory Layer

If your project was created before Wave 11, run:

```bash
sdd memory status <feature-id>
```

If the memory index is missing:

```bash
# The init script now creates memory infrastructure automatically
sdd init
```

This creates `memory-index.md` and ensures all memory files are indexed.

**New operating loop** (optional but recommended):

```
Phase Start → sdd memory status → execute → sdd memory sync → sdd gate
```

### Step 9: Use Curated Commands (Optional)

Wave 11 adds 8 command prompts that map to SDD phases:

| Command | Phase | Purpose |
|---------|-------|---------|
| `/challenge` | Design | Falsify assumptions, identify risks |
| `/plan-implementation` | Design | Generate implementation plan from design |
| `/assert-quality` | Preparation | Verify artifact quality and coverage |
| `/review-functional` | Review | Functional requirements review |
| `/review-code` | Review | Code quality review |
| `/test-journey` | Preparation | Generate test scenarios from user stories |
| `/debug-5-whys` | Any | Root cause analysis |
| `/reproduce-bug` | Any | Bug reproduction workflow |

Run them via VS Code prompt picker or CLI:

```bash
sdd spell challenge <feature-id>
```

### Step 10: Use Skills (Optional)

Two skills are available:

```bash
sdd skill run sdd-auto-implement <feature-id>   # Multi-step autonomous implementation
sdd skill run sdd-challenge <feature-id>         # Critical challenge analysis
```

Skills are referenced in `.github/skills/` and can be invoked from prompts or CLI.

### Step 11: Choose Execution Mode (Optional)

Wave 11 introduces three execution modes. **`standard` is the default and requires no changes.**

| Mode | When to Use | How to Enable |
|------|-------------|--------------|
| `standard` | Default for all features | No action needed |
| `autonomous-guided` | Bounded implementation with operator approval per cycle | Set `"executionMode": "autonomous-guided"` in `.feature-meta.json` |
| `autonomous-governed` | Repetitive low-risk tasks with stable artifacts | Set `"executionMode": "autonomous-governed"` in `.feature-meta.json` |

To enable an autonomous mode:

1. Edit `.specify/specs/<feature-id>/.feature-meta.json`
2. Set `executionMode`, `autonomyBudget`, and `escalationThreshold`
3. Run `/autonomous-implement` prompt

To rollback: set `"executionMode": "standard"` at any time.

See PLAYBOOK.md §29 "Execution Modes" for the full decision matrix.

### Step 12: Apply Frontend Packs (Optional, Frontend Teams Only)

> **Module vs Extension**: A *module* (`sdd module install`) injects stack-specific knowledge (instructions, guidances, constitution articles). An *extension* (`sdd extension install`) adds or overrides agents, prompts, and lifecycle hooks for a specific workflow concern. Frontend setup typically requires both: a module for domain knowledge and one or more extensions for specialized workflows.

Three tailored extension packs are available for UI projects:

| Pack | Purpose | Prerequisite |
|------|---------|-------------|
| `frontend-stratos-core` | Shared UI baseline (design tokens, component ambiguity, MFE decomposition) | None (base pack) |
| `frontend-enterprise-search` | Advanced search forms and result rendering | `frontend-stratos-core` |
| `frontend-dual-agent-review` | Neo (generator) + Smith (reviewer) dual-agent profiles | `frontend-stratos-core` |

Install:

```bash
sdd module install std-fe
sdd extension install sdd-extension-frontend-stratos-core
sdd extension install sdd-extension-frontend-enterprise-search   # if search features are needed
sdd extension install sdd-extension-frontend-dual-agent-review   # if dual-agent review are needed
```

Validate before use:

```bash
sdd extension validate .sdd-extensions/extensions/frontend-stratos-core/
sdd extension doctor .sdd-extensions/extensions/frontend-stratos-core/
```

See PLAYBOOK.md §28 "Frontend Tailored Packs" for composition recipes.

### Step 13: Verify Your Migration

Run the status command with the `--graph` flag:

```bash
sdd status <feature-id> --graph
```

This displays the artifact dependency graph showing which artifacts are present, missing, or still templates.

Run a gate to verify explain-mode diagnostics:

```bash
sdd gate <feature-id> 1
```

If the gate fails, you should see a structured `📋 EXPLAIN` block with actionable next steps.

---

## What You Do NOT Need to Change

- **Existing features** continue to work in `standard` mode with no modifications
- **Agent configuration** is unchanged (model-tier, ceremony levels, etc.)
- **Gate criteria** are unchanged (new diagnostics are informational additions)
- **Existing prompts** are unchanged (new prompts are additive)
- **Cost tracking** is unchanged (Wave 10 feature)
- **Worktree isolation** is unchanged (Wave 10 feature)

---

## Breaking Changes

There are **no breaking changes** in any wave. All v3 shell scripts, agent files, and workflows continue to work. Every migration step is fully additive.

---

## Rollback

### Rolling back to pre-Wave 9 (v3)

1. Remove `.specify/cli/` (or uninstall the `sdd` package)
2. Remove `.cursor/`, `.claude/`, `.windsurfrules`, `agents.md` if generated
3. Remove `.sdd-extensions/` if created
4. Remove `.sdd-modules/` if created
5. Remove Article VI: Model Configuration from `constitution.md` and renumber back
6. Remove `model-tier:` lines from agent files (optional — they are ignored by VS Code)

### Rolling back Wave 11 features

1. Set `"executionMode": "standard"` in all `.feature-meta.json` files
2. Uninstall any extension packs (see PLAYBOOK.md §26)
3. Continue using the Wave 9–10 workflow — all commands remain functional

---

## Module Catalog Reference

For recommended module + pack bundles, see [`.sdd-modules/README.md`](.sdd-modules/README.md).

The decision tree in that file helps you choose:
- `core-be` for all projects
- `std-fe` for Stratos/React frontend projects
- `aws-fe` for Acme FE domain-specific projects

---

## Module Author Migration: Agent Patches → `agentContributions`

> **Applies to:** Module authors upgrading their modules to use the automated agent composition system (Wave 14.3+).

Starting with Wave 14.3, modules can declare **machine-readable** agent contributions in `module.json`. This replaces the previous manual workflow for adding agents or tools to core agents.

### What changes

| Before (manual) | After (automated) |
|---|---|
| Agent patches in `agent-patches/` — humans read and manually merge into agent bodies | Agent patches remain for behavioral guidance; tool/metadata contributions go in `agentContributions` |
| Core agents in `agents-canonical.json` only; module agents lived in `.github/agents/` after manual copy | Module agents declared in `module.json` `agentContributions.agents`; composition is automatic |
| `requirement-analyst` had integration tools hardcoded in canonical | Integration tools declared in `core-be/module.json` `agentContributions.tool-overlays` |

### Step-by-step: migrating a module that adds tools to a core agent

If your module provides an MCP server or integration that adds tools to `requirement-analyst` (or another core agent):

1. **Open `module.json`**
2. **Add the `agentContributions` key:**
```json
"agentContributions": {
  "tool-overlays": [
    {
      "target-agent": "requirement-analyst",
      "add-tools": ["my-mcp-tool/read_data", "my-mcp-tool/write_data"]
    }
  ],
  "agents": []
}
```
3. **Run `compose-agents.py`** to regenerate `agents-composed.json`:
```bash
python .specify/scripts/compose-agents.py --verbose
```
4. **Run `generate-adapters.py`** to update the VS Code adapter with the new tools.

### Step-by-step: migrating a module that provides new agents

If your module provides entirely new agents (like `sdd-evolution` with its meta-builder agents):

1. **Keep the `.agent.md` files** in `agents/` directory — these are the human-readable copies used by VS Code Copilot.
2. **Add the `agentContributions.agents` entries** in `module.json` with the canonical JSON definition (name, slug, description, tools, model-tier, phase, instructions, handoffs).
3. **Run `compose-agents.py`** — the new agents appear in `agents-composed.json` and will be included in all adapter generation.

> **Note**: The `.agent.md` files remain the source of truth for agent *body/instructions*. The `agentContributions.agents` entry is the source of truth for agent *metadata* (tools, tier, phase, handoffs).

### What does NOT need migration

- **Behavioral agent patches** (`agent-patches/*.patch.md`) — these are behavioral guidance for domain-specific instruction profiles and are NOT convertible to `agentContributions`. They remain as-is (human review, manual behavior merge).
- **Instruction/prompt/guidance files** — these continue to be installed by `module-install.sh` as before.

---

## FAQ

**Q: Will my existing VS Code workflow break?**
A: No. All `.github/agents/` files continue to work unchanged with VS Code Copilot.

**Q: Do I need to migrate if I only use VS Code?**
A: The `sdd` CLI is optional but recommended. At minimum, run Step 3 (constitution update) for the model-tier system to work correctly.

**Q: What happens if I run `sdd adapters generate` before Step 3?**
A: The generator uses default model names (`Claude Opus 4.6`, `Claude Sonnet 4.6`, `Claude Sonnet 4.6`) if Article VI is missing. Add Article VI for project-specific overrides.

**Q: Can I use both v3 scripts and the CLI?**
A: Yes. The `sdd` CLI wraps the same shell scripts. `sdd gate 1` and `.specify/scripts/validate-gate.sh <id> 1` are equivalent.

**Q: How do I update the canonical agent definitions?**
A: Edit `.specify/adapters/agents-canonical.json`, then run `sdd adapters generate`. The VS Code `.agent.md` files are also updated to sync the `model:` field.

**Q: Can I adopt Wave 11 features incrementally?**
A: Yes. Every Wave 11 feature is opt-in. Start with `sdd memory status` (5 min), then try curated prompts, and only later consider autonomous modes.

---

## Support

- **PLAYBOOK.md** — End-to-end operational flow and configuration reference
- **TEAM-ADOPTION-GUIDE.md** — Change management and rollout strategy
- **_plan/MASTER-PLAN.md** — Execution roadmap and task status
