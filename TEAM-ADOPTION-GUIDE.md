# Team Adoption Guide — Enterprise SDD Workflow

> **Version**: 2.0
> **Date**: April 17, 2026
> **Audience**: team leads, engineering managers, and champions responsible for introducing spec-driven development.

---

## Table of Contents

1. [Purpose](#purpose)
2. [Running a Time-Boxed Experiment](#running-a-time-boxed-experiment)
3. [What to Measure](#what-to-measure)
4. [Handling Resistance](#handling-resistance)
5. [Mandate vs. Recommend](#mandate-vs-recommend)
6. [Scaling Beyond the Experiment](#scaling-beyond-the-experiment)
7. [Organizational Adoption](#organizational-adoption)

---

## Purpose

Enterprise SDD Workflow is a 6-phase, gated pipeline with 20 specialized agents, 4 quality gates, and automated validation scripts. Its power comes from structure, and structure requires adoption discipline. This guide provides a practical adoption approach, informed by external case studies:

- **Witboost** (4 devs, 2-day workshop) — voluntary experiment → permanent SDD adoption. Their workflow mirrors SDD's gated pipeline almost point-by-point.
- **Mollie** (12 engineers, 1-month mandate) — forced AI adoption → 100% want to continue. Their survey revealed that structured approaches outperform ad-hoc AI usage.

The core principle from both experiences: **shared technique should precede shared tools.** A common failure mode is installing agents without aligning on the workflow. `PLAYBOOK.md` provides the operational technique; this guide focuses on change management.

---

## Running a Time-Boxed Experiment

### Why time-box

SDD's gated pipeline can look intimidating on paper — 6 phases, 20 agents, 4 gates, 8 artifact types. A time-boxed experiment lets the team experience the workflow on a real feature before committing to permanent adoption. It answers: "Does the pipeline improve our output quality enough to justify the process overhead?"

### Recommended format: 2-day intensive

Based on the Witboost model (which spent Day 1 on infrastructure and Day 2 on execution):

#### Day 1 — Foundation & Context (Setup Day)

| Time | Activity | Owner | Deliverable |
|------|----------|-------|-------------|
| **Morning (1h)** | Kick-off: walk through the SDD PLAYBOOK.md end-to-end | Champion | Team understands the 6 phases and 4 gates |
| **Morning (1h)** | Setup: everyone installs prerequisites, runs `init.sh` | Everyone | Scripts executable, agents visible in VS Code |
| **Morning (1h)** | Create a test feature: `new-feature.sh "team-experiment"` | Champion | Feature directory with templates ready |
| **Morning (1h)** | Constitution creation: team uses `@constitution` together | Team | `.specify/memory/constitution.md` filled with real project values |
| **Afternoon (2h)** | Phase 1 practice: each pair runs `@requirement-analyst` on a familiar user story | Pairs | `business-context.md` and `spec.md` with real content |
| **Afternoon (1h)** | Gate validation: run `validate-gate.sh` and interpret results | Team | Everyone understands how gates work |
| **Afternoon (1h)** | Q&A and debrief | Team | Questions resolved, comfort level assessed |

**Day 1 exit criteria:**
- [ ] All team members have agents working in VS Code
- [ ] Constitution reflects the team's actual tech stack and quality standards
- [ ] Everyone has passed Gate 1 at least once
- [ ] Everyone understands the template → agent → artifact → gate flow

#### Day 2 — Full Pipeline Execution

| Time | Activity | Owner | Deliverable |
|------|----------|-------|-------------|
| **Morning (1h)** | Select a real feature (small, well-understood, 2–3 user stories) | Team | Feature chosen, scope agreed |
| **Morning (1h)** | Phase 1: `@requirement-analyst` + `@clarification` → Gate 1 | Pair A | `business-context.md`, `spec.md`, `clarifications.md` + Gate 1 PASSED |
| **Morning (2h)** | Phase 2: `@architect` + `@api-champion` → Gate 2 | Pair B | `plan.md`, contracts + Gate 2 PASSED |
| **Afternoon (1.5h)** | Phase 3: `@test-explorer` + `@software-engineer` (PLANNING) + `@analysis` → Gate 3 | Pair A | `test-cases.md`, `tasks.md`, `analysis-report.md` + Gate 3 PASSED |
| **Afternoon (1.5h)** | Phase 4: `@test-engineer` (Red) + `@software-engineer` (Green) | Pair B | Tests + Implementation |
| **Afternoon (0.5h)** | Phase 5: `@review` → Gate 4 | Team | `ship-checklist.md` + Gate 4 PASSED |
| **Afternoon (0.5h)** | Retrospective | Team | Adoption decision + action items |

**Day 2 exit criteria:**
- [ ] One feature went through all 6 phases and passed all 4 gates
- [ ] Team has hands-on experience with at least 10 of the 20 agents
- [ ] Retrospective produced concrete go/no-go decision

### Alternative format: 2-week embedded trial

For teams that can't dedicate 2 full days:

| Week | Focus | Activities |
|------|-------|-----------|
| **Week 1** | Learn Phases 0–2 | Each developer creates a constitution, writes requirements for one story, designs one feature. Daily 15-min standup to share learnings. Validate Gates 1 and 2. |
| **Week 2** | Learn Phases 3–5 | Each developer creates test cases, implements one task with TDD, runs the review. End-of-week retrospective. Validate Gates 3 and 4. |

**Key rule**: assign a **champion** — one person who has already completed the PLAYBOOK.md end-to-end. The champion pairs with others, not lectures at them.

### What NOT to do

- **Don't skip the constitution.** The constitution is the foundation — every agent reads it. Without it, agents produce generic output.
- **Don't skip Gate validation.** Gates are the SDD differentiator. If you skip them, you're just using agents without process discipline.
- **Don't pick a 10-story epic for the experiment.** Pick 2–3 simple, well-understood user stories. The goal is to experience the process, not deliver a major feature.
- **Don't let one person drive while others watch.** Everyone must type `@agent-name` themselves. Observation doesn't build muscle memory.

---

## What to Measure

### Quantitative metrics

Collect these **before** and **after** the experiment:

| Metric | How to measure | What it tells you |
|--------|---------------|-------------------|
| **Gate pass rate (first attempt)** | % of gates passed on first validation | Whether agents produce complete artifacts — lower rates mean agents need more guidance or instructions |
| **Time per phase** | Clock time from phase start to gate passed | Where the bottlenecks are — requirements? Design? Tests? |
| **Specification completeness** | Count of items flagged by `@analysis` or `analyze-consistency.sh` (fewer = better) | Whether the pipeline catches gaps before implementation |
| **Traceability coverage** | % of US→AC→TC chain complete (from analysis report) | Whether spec-driven development produces traceable artifacts |
| **Rework after Gate 4** | Bug count or change requests after ship review | Whether the gated pipeline reduces post-ship issues |
| **Time to production-ready** | Clock time from feature creation to Gate 4 passed | Overall pipeline throughput |

### Qualitative metrics (anonymous survey)

Administer at the **end of the experiment**. Use a 1–5 scale + free text:

| Question | Scale |
|----------|-------|
| "The spec-driven approach helped me think through the feature more thoroughly" | 1 (strongly disagree) – 5 (strongly agree) |
| "The quality gates caught issues that would have reached production" | 1–5 |
| "I feel more productive using the SDD workflow" | 1–5 |
| "I trust the AI-generated specifications for correctness" | 1–5 |
| "I trust the AI-generated code for security" | 1–5 |
| "The constitution accurately reflects our team's standards" | 1–5 |
| "The agents asked useful clarifying questions" | 1–5 |
| "I would want to continue using this workflow" | 1–5 |
| "I feel more or less tired at the end of the day compared to before" | Much more tired – Much less tired |
| "Which agents were most useful?" | Free text |
| "Which agents were least useful or frustrating?" | Free text |
| "What would you change about the workflow?" | Free text |
| "What Phase was most valuable? Least valuable?" | Free text |

> **Reference benchmarks** (Mollie survey, 12 engineers): 100% wanted to continue, 67% felt less tired, security trust was 2.4/5 (weakest), unit test generation was rated most useful (92%).

### Success criteria

Define these **before** the experiment:

| Criterion | Threshold | Rationale |
|-----------|-----------|-----------|
| Willingness to continue | ≥ 70% score ≥ 4 on "would continue" | Below this, adoption will require mandating |
| Gate pass rate | ≥ 60% on first attempt by end of experiment | If gates fail constantly, agents need better instructions |
| Traceability coverage | ≥ 80% US→AC→TC chain | Below this, the pipeline isn't producing its core value |
| Specification quality | Fewer items flagged by Analysis agent vs. pre-SDD baseline | Validates the gated approach catches issues early |
| Fatigue | No increase in "more tired" responses | If the process increases cognitive load, it needs simplification |

---

## Handling Resistance

### Common objections and responses

| Objection | Root cause | Response |
|-----------|-----------|----------|
| "This is too much process / too many phases" | Sees overhead before value | "Gate checks are typically fast, and the real effort is in design clarity and traceability. Try it on one feature before judging." |
| "We already have a process that works" | Status quo bias | "SDD doesn't replace your process — it adds quality gates and AI amplification. Your existing knowledge goes into the constitution and instruction files." |
| "AI code lacks quality / taste" | Legitimate concern | "That's why we have Phase 5 (Review) and the ship-checklist. AI writes the first draft; humans ensure quality. The constitution and instructions encode your team's taste." |
| "I don't trust AI for security" | Legitimate concern (Mollie: 2.4/5) | "Neither does SDD — that's why the ship-checklist has a dedicated security section. AI generates; humans verify. The gates enforce that verification happened." |
| "Gates will slow us down" | Sees gates as bureaucracy | "Gates don't add work — they verify work already done. They catch missing test cases and spec gaps before they become production bugs. The alternative is finding these issues in QA or production." |
| "20 agents is overwhelming" | Information overload | "You'll only use 5–7 regularly. Phase 1 uses 3 agents. Phase 2 uses 1–3. The PLAYBOOK tells you exactly which agent to use when." |
| "This will replace developers" | Existential fear | "The workflow shifts effort toward analysis, architecture, and review. AI accelerates draft production; human judgment remains central for correctness, security, and trade-offs." |
| "I tried AI coding and it was terrible" | Bad past experience with generic AI | "Generic AI without context produces generic output. SDD provides constitution + instructions + traceability. The quality ceiling is set by the quality of context, not the AI model." |

### Strategies by resistance type

#### Skeptics (need evidence)
- **Show the Gate 4 output.** Run the experiment with a volunteer, then show the skeptic the complete artifact chain: constitution → business-context → spec → plan → test-cases → tasks → ship-checklist. The traceability is the argument.
- **Share the Witboost data.** A 4-person team rebuilt their process in 2 days and adopted SDD permanently. They weren't experimenting — they were validating their intuition.
- **Let them choose the feature.** Skeptics engage more when they pick the test case. "Choose any story from this sprint."

#### Perfectionists (the "AI code lacks taste" camp)
- **Make them the constitution author.** Their taste becomes the project's standards. `@constitution` encodes their quality principles.
- **Involve them in instruction file creation.** They define the patterns that every AI-generated artifact must follow.
- **Point to the ship-checklist.** 100+ verification items — more thorough than most manual review checklists.

#### Passives (won't resist but won't adopt)
- **Pair with a champion for the first 2–3 features.** Active pairing, not observation.
- **Set a minimum viable commitment.** "Run `@requirement-analyst` on your next story. Just that one agent."
- **Create quick-reference cards.** Phase 1: type `@requirement-analyst`, then `@clarification`, then run `validate-gate.sh 1`. That's it.

#### Seniors who feel threatened
- **Reframe as leverage.** "Your architectural knowledge becomes the constitution. Your patterns become instruction files. AI amplifies your expertise across the entire team."
- **Position them as reviewers.** Phase 5 (Review) is where senior judgment matters most. "The pipeline brings work to you in a consistent, reviewable format."

---

## Mandate vs. Recommend

### When to recommend

Recommend (don't mandate) when:

- [ ] The team is small (< 6 people) and peer influence works
- [ ] At least 1–2 people are genuinely curious and willing to champion
- [ ] You have time — no urgent deadline requiring immediate process improvement
- [ ] The team already has a functioning (if imperfect) development process
- [ ] Team culture values autonomy

**How to recommend:**
1. Run the 2-day experiment with volunteers
2. Share results (metrics + survey) with the full team
3. Make the framework available — set up the repo, configure the submodule
4. Let champions model successful usage on real features
5. Track adoption monthly: how many features went through gates?
6. After 2 months, if adoption is > 50%, consider formalizing

**Timeline**: expect 2–3 months for organic adoption in a team of 4–8 people.

### When to mandate

Mandate when:

- [ ] You have evidence it works (post-experiment data shows clear improvement)
- [ ] The team is large enough (> 6) that organic spread is too slow
- [ ] Consistency is critical — you need all features to have traceable specs, test cases, and design docs
- [ ] You're willing to invest in support (champion, training, ongoing feedback)
- [ ] The team has already had some exposure (they've seen it work, just haven't adopted individually)

**How to mandate (the Mollie model, adapted for SDD):**

1. **Run the experiment first** — never mandate blind. At least 2–3 people should have completed the PLAYBOOK.md end-to-end.

2. **Announce a 1-month mandatory trial** with clear expectations:
   - "Every new feature must go through Phases 1–3 and pass Gates 1–3"
   - "Phases 4–5 are encouraged but not required during the trial"
   - "Use the PLAYBOOK.md as your reference — it has step-by-step instructions"

3. **Assign a champion** available daily for questions and pair-programming.

4. **Commit to an anonymous survey at the end** — publish the survey questions on day 1 so people know they'll have a voice.

5. **Set minimum expectations, not maximum.**
   - "At least 3 agents per feature" (not "use all 20")
   - "Pass Gate 1 for every feature" (not "pass all 4 gates on day one")

6. **At the end of the month:**
   - Run the anonymous survey
   - Review quantitative metrics (gate pass rates, traceability coverage)
   - Hold a team retrospective
   - Decide together: continue, modify, or abandon

**Critical rule**: mandating without listening creates resentment. If you mandate, you must also commit to acting on feedback through anonymous surveys and visible process adjustments.

### Decision matrix

| Situation | Approach |
|-----------|----------|
| Small team, curious developers, no urgency | Recommend + champion |
| Small team, mixed interest, moderate urgency | 2-day experiment → recommend with peer influence |
| Large team, need specification consistency, evidence exists | Mandate Phases 1–3, recommend Phases 4–5 |
| Large team, no evidence yet | 2-day experiment with volunteers → mandate if results are positive |
| Anyone actively hostile | Do NOT include in mandate. Pair with champion, show results, revisit in 2 months. |
| Regulated industry requiring traceability | Mandate Phases 1–3 + Gate validation (the traceability chain is the compliance artifact) |

### Progressive mandate (recommended for SDD)

SDD's phased structure enables a **progressive mandate** — mandate one phase at a time:

| Month | Mandate | Optional | Gate required |
|-------|---------|----------|---------------|
| Month 1 | Phase 0 (Constitution) + Phase 1 (Requirements) | Everything else | Gate 1 |
| Month 2 | Add Phase 2 (Design) | Phases 3–5 | Gates 1–2 |
| Month 3 | Add Phase 3 (Preparation) | Phases 4–5 | Gates 1–3 |
| Month 4 | Full pipeline | Maintenance agents | Gate 4 for production releases |
| Month 5+ | Full pipeline + autonomy-guided mode | `autonomous-governed` for experienced teams | Gate 4 + autonomy policy enforcement |

This approach lets the team build competence incrementally. Each month adds one phase, corresponding to one new set of agents and one new gate. By month 4, the full pipeline is natural.

---

## Scaling Beyond the Experiment

### Month 1: Foundation

- [ ] Constitution reflects the team's actual tech stack, quality standards, and architecture principles
- [ ] All team members can run Phases 0–1 independently
- [ ] Gate 1 passes consistently on first attempt
- [ ] Champion is identified and active
- [ ] Shared channel (Slack/Teams) exists for tips, questions, and sharing prompts that work well

### Month 2: Design Discipline

- [ ] All features go through Phase 2 (Design) before implementation
- [ ] API/messaging contracts are produced for relevant features
- [ ] Traceability (US → Plan) is verified by Gate 2
- [ ] Run second anonymous survey — compare with the first
- [ ] Identify instruction files that should be created with `@instruction-builder`

### Month 3: Full Pipeline

- [ ] Phase 3 (test cases + task breakdown + consistency analysis) is standard practice
- [ ] Gate pass rate on first attempt > 80%
- [ ] TDD workflow (test-engineer → software-engineer) is being used for new features
- [ ] Review agent and ship-checklist are part of the release process
- [ ] Meta agents are being used to extend the framework (new agents, instructions)

### Continuous

- **Sprint retrospective item**: "SDD: what worked, what didn't?" — 5 minutes per retro
- **Constitution reviews**: quarterly, or when the tech stack changes
- **Instruction file updates**: when new patterns emerge or existing ones evolve
- **Champion rotation**: every 2 months to prevent single-point-of-failure
- **Gate metrics dashboard**: track gate pass rates over time — declining rates indicate stale instructions or evolving code patterns
- **Cross-team sharing**: if multiple teams adopt SDD, share constitutions and instruction files as templates

---

## Wave 11 Adoption Update

> Added April 11, 2026. See [MIGRATION-GUIDE.md](MIGRATION-GUIDE.md) for the full migration walkthrough.

### What's New for Teams

Wave 11 adds four opt-in capability layers. **Your existing workflow is unchanged** — all new features are additive.

| Capability | Default | Opt-In | Documentation |
|-----------|:-------:|:------:|---------------|
| Memory-first layer (`sdd memory status/sync/doctor`) | Available | Use when you want freshness tracking | PLAYBOOK.md §Quick-Start Workflow Map |
| Curated command prompts (`/challenge`, `/plan-implementation`, etc.) | Available | Use via prompt picker or `sdd spell` | PLAYBOOK.md §17 Prompt Library |
| Execution modes (`autonomous-guided`, `autonomous-governed`) | Off | Set in `.feature-meta.json` | PLAYBOOK.md §29 Execution Modes |
| Frontend tailored packs (Stratos, search, dual-agent review) | Not installed | Install via `sdd extension validate` | PLAYBOOK.md §28 Frontend Tailored Packs |

### Recommended Rollout for Wave 11

| Week | Action | Effort |
|------|--------|--------|
| 1 | Update to Wave 11; run `sdd status` to verify | 10 min |
| 1 | Try `sdd memory status` on one feature | 5 min |
| 2 | Use `/challenge` prompt on a design review | 15 min |
| 3 | Try `autonomous-guided` on one low-risk bounded task | 30 min |
| 4 | Evaluate: is it useful? Collect feedback | Survey |

### Module Catalog

For recommended module + extension pack bundles based on your project type, see [`.sdd-modules/README.md`](.sdd-modules/README.md).

---

## Waves 12–14 Adoption Update

> Added April 17, 2026. See [MIGRATION-GUIDE.md](MIGRATION-GUIDE.md) for the full migration walkthrough.

### What’s New for Teams (Waves 12–14)

Waves 12–14 expanded the framework with deeper automation, reusable skills, hardened tooling, and self-evolution capabilities. **Everything remains opt-in** — existing workflows continue unchanged.

| Capability | Default | Opt-In | Documentation |
|-----------|:-------:|:------:|---------------|
| Skills layer (`sdd skill list/validate/run`) | Available | Register in SKILL-INDEX.md | PLAYBOOK.md §20 Skills |
| User modules (`sdd module install/remove`) | Available | Install domain modules | `.sdd-modules/README.md` |
| Autonomy policy (`.specify/autonomy-policy.json`) | Off | Configure per-feature autonomy | PLAYBOOK.md §29 Execution Modes |
| CLI expansion (23 commands: `spell`, `route`, `ship`, `retrospect`, etc.) | Available | Use as needed | `sdd --help` |
| MCP server hardening (HTTP timeouts, CQL sanitization) | Active | Transparent — no action needed | REQUIREMENTS.md §2.1 |
| Multi-IDE adapters (Cursor, Claude Code, Windsurf, Codex) | Available | Run `sdd adapters generate` | PLAYBOOK.md §14 Multi-IDE |

### Recommended Rollout for Waves 12–14

| Week | Action | Effort |
|------|--------|--------|
| 1 | Run `sdd skill list` to see available skills | 5 min |
| 1 | Try `sdd spell challenge` on a recent design decision | 10 min |
| 2 | Install a domain module: `sdd module install core-be` | 15 min |
| 3 | Try `sdd retrospect` after completing a feature | 15 min |
| 4 | Evaluate skills + modules adoption — collect feedback | Survey |

### Cross-Functional Team Guidance

For teams spanning backend, frontend, and infrastructure:

| Role | Recommended Modules | Key Commands |
|------|--------------------|--------------|
| Backend | `core-be` | `sdd gate`, `sdd analyze`, `sdd ship` |
| Frontend | `core-be` + `std-fe` + Stratos extension | `sdd gate`, `sdd extension validate` |
| QA/Test | Core only | `sdd gate`, `sdd status --graph`, `sdd skill run sdd-spec-review` |
| Tech Lead | Core + autonomy policy | `sdd autonomy status`, `sdd retrospect`, `sdd report` |

---

## Organizational Adoption

> Added April 27, 2026 (Wave 21).

Three artifacts support larger-scale organizational adoption:

### Context Debt Audit

Run `/context-debt-audit` to scan all instruction, agent, skill, and template files for sizing violations, stale references, and misclassified knowledge. The audit produces `.specify/reports/CONTEXT-DEBT.md` with prioritized findings.

Use this quarterly or after major waves to keep context files healthy.

### Adoption Timeline Template

Generate a phased adoption plan with `sdd report` (select `adoption-timeline-template.md`). The template provides:

- **Phase 1 (Weeks 1–2):** Foundation — constitution + Phase 1
- **Phase 2 (Weeks 3–4):** Pipeline expansion — Phases 2–3 + Gates 1–3
- **Phase 3 (Weeks 5–8):** Full pipeline + survey + decision

Each phase includes rollback criteria and a kill criterion for abandoning adoption.

### Adoption Business Case

Run `/adoption-business-case` to build a data-driven TCO + ROI analysis. The 5-step workflow collects baseline metrics, calculates adoption costs, projects benefits, estimates payback period, and produces `.specify/reports/ADOPTION-BUSINESS-CASE.md`.
