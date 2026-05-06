---
description: Implement a feature from existing specification artifacts
mode: agent
---

**Implement the feature** defined in the specification artifacts.

## Steps

1. Read the spec artifacts to understand feature requirements:
   - `spec.md` — user stories and acceptance criteria
   - `plan.md` — architecture and design decisions
   - `data-model.md` — domain model
   - `test-cases.md` — test strategy
   - `tasks.md` — task breakdown

2. Follow TDD:
   - Invoke `@test-engineer` to write failing tests first (Red phase)
   - Invoke `@software-engineer` to implement code that passes tests (Green phase)

3. Verify traceability:
   - Every test references TC-XXX, US-XXX, AC-XXX
   - Every source file references TXXX
   - Code comments include traceability markers

4. Run `@review` when implementation is complete.
