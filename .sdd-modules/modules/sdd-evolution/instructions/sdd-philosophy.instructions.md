---
description: "Use when: proposing improvements to Enterprise SDD, evolution planning, implementation planning, feature harvest, evaluating features for SDD adoption, checking SDD design boundaries. Contains the inviolable philosophy constraints and rejected feature patterns that govern all Enterprise SDD evolution."
applyTo: "**/sdd-evolution/**"
---

# Enterprise SDD Philosophy & Design Boundaries

## Inviolable Constraints

Before proposing or planning ANY improvement to Enterprise SDD, these principles are non-negotiable:

1. **Constitution supremacy** — Every new feature must respect the project constitution. No feature may bypass or weaken constitution governance.
2. **Gate integrity** — Quality gates (Gate 1–4) remain mandatory. New features may ADD gates but never remove or weaken existing ones.
3. **Traceability chain** — US→AC→TC→Task→Code traceability must never be broken.
4. **Template discipline** — Agent outputs use templates. Free-form output is not acceptable for primary artifacts.
5. **Boundary rules** — Every agent has Always Do / Ask First / Never Do rules. New agents must define these before shipping.
6. **Additive evolution** — Each improvement adds capabilities without removing existing ones. Breaking changes require explicit migration guides.
7. **Team-oriented** — Enterprise SDD targets teams, not solo developers. Team collaboration, shared state, review gates are features.
8. **Tech-agnostic** — Domain knowledge belongs in constitution or `.instructions.md` files, NOT hardcoded in agents.
9. **Human-readable agent files** — The agent-based model is SDD's differentiator. Never propose replacing agents with programmatic state machines.

## Design Boundaries — What NOT to Adopt

| Rejected Pattern | Source | Reason |
|-----------------|--------|--------|
| Programmatic state machine | GSD-2 | Breaks agent-based model; sacrifices human-readable agent files |
| Agent-less CLI model | Spec Kit | Removes SDD's differentiating specialized agents with handoff guidance |
| Solo-only execution model | GSD v1/v2 | SDD targets teams; shared state and review gates are features |
| No-governance autonomous mode | GSD-2 | Quality gates are SDD's philosophical foundation; bypass contradicts spec-driven premise |
| Discussion/Writer agent pairs | AI Framework | Single-agent-per-phase with templates is proven superior |
| Hardcoded domain knowledge | AI Framework | Breaks tech-agnosticism; domain knowledge belongs in constitution or instructions |

## Feature Evaluation Criteria

When evaluating features from public frameworks for Enterprise SDD adoption:

**Accept features that:**
- ✅ Add capability WITHOUT breaking any of the 9 constraints above
- ✅ Fill a documented gap in Enterprise SDD
- ✅ Are compatible with agent-based + gate-driven model
- ✅ Can be implemented as new agents, instructions, skills, templates, or CLI commands
- ✅ Improve developer experience, quality, or team collaboration

**Reject features that:**
- ❌ Violate any of the 9 inviolable constraints
- ❌ Match a pattern in the Design Boundaries table
- ❌ Were already adopted in previous waves (check evolution doc)
- ❌ Are too narrow/niche for enterprise adoption

## Plan Task Conventions

When creating implementation plans for Enterprise SDD improvements:
- Priority: 🔴 High (blocks others), 🟡 Medium (important), 🟢 Low (nice to have)
- Effort: Low (< 1 hour), Medium (1-4 hours), High (> 4 hours)
- Status: ⬜ Not started, 🟡 In Progress, ✅ Complete
- Task numbering: `{Phase}.{Sequence}` (e.g., A.1, A.2, B.1)
- Every task must have acceptance criteria
- Dependencies must form a DAG (no circular dependencies)
