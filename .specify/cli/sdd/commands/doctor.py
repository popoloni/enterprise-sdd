"""`sdd doctor` — validate framework installation integrity."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from sdd.utils.config import find_repo_root
from sdd.utils import output


INSTRUCTION_MAX_LINES = 50


def add_doctor_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    subparsers.add_parser(
        "doctor",
        help="validate SDD framework installation integrity",
        description=(
            "Check that all expected agent files, instructions, skills, templates, "
            "and modules exist and are well-formed. Outputs PASS/WARN/FAIL per category."
        ),
    )


def run_doctor(args: argparse.Namespace) -> int:
    try:
        repo_root = find_repo_root()
    except FileNotFoundError as exc:
        output.error(str(exc))
        return 2

    github = repo_root / ".github"
    specify = repo_root / ".specify"
    results: list[tuple[str, str, str]] = []  # (category, status, detail)

    # 1. Agent check
    agents_dir = github / "agents"
    if agents_dir.exists():
        agents = list(agents_dir.glob("*.agent.md"))
        if agents:
            results.append(("Agents", "PASS", f"{len(agents)} agent files found"))
        else:
            results.append(("Agents", "WARN", "Agents directory exists but no .agent.md files found"))
    else:
        results.append(("Agents", "FAIL", f"Missing directory: {agents_dir.relative_to(repo_root)}"))

    # 2. Instruction check
    instructions_dir = github / "instructions"
    if instructions_dir.exists():
        instructions = list(instructions_dir.glob("*.instructions.md"))
        if instructions:
            results.append(("Instructions", "PASS", f"{len(instructions)} instruction files found"))
            oversized: list[tuple[str, int]] = []
            for instruction in instructions:
                try:
                    line_count = len(instruction.read_text(encoding="utf-8").splitlines())
                except OSError:
                    continue
                if line_count > INSTRUCTION_MAX_LINES:
                    oversized.append((instruction.name, line_count))

            if oversized:
                oversized_sorted = sorted(oversized, key=lambda x: x[0])
                preview = ", ".join(f"{name} ({count})" for name, count in oversized_sorted[:5])
                extra = "" if len(oversized_sorted) <= 5 else f" +{len(oversized_sorted) - 5} more"
                results.append((
                    "Instruction Size",
                    "WARN",
                    f"{len(oversized_sorted)} instruction files exceed {INSTRUCTION_MAX_LINES} lines: {preview}{extra}",
                ))
            else:
                results.append((
                    "Instruction Size",
                    "PASS",
                    f"All instruction files are <= {INSTRUCTION_MAX_LINES} lines",
                ))
        else:
            results.append(("Instructions", "WARN", "Instructions directory exists but no files found"))
    else:
        results.append(("Instructions", "FAIL", f"Missing directory: {instructions_dir.relative_to(repo_root)}"))

    # 3. Skill check
    skills_github = github / "skills"
    skills_specify = specify / "skills"
    skill_count = 0
    if skills_github.exists():
        skill_count += sum(1 for d in skills_github.iterdir() if d.is_dir() and (d / "SKILL.md").exists())
    if skills_specify.exists():
        skill_count += sum(1 for d in skills_specify.iterdir() if d.is_dir() and (d / "SKILL.md").exists())
    if skill_count > 0:
        results.append(("Skills", "PASS", f"{skill_count} skills with SKILL.md found"))
    elif skills_github.exists() or skills_specify.exists():
        results.append(("Skills", "WARN", "Skills directory exists but no SKILL.md files found"))
    else:
        results.append(("Skills", "WARN", "No skills directory found"))

    # 4. Template check
    template_dir = specify / "templates"
    if template_dir.exists():
        templates = list(template_dir.glob("*.md"))
        if templates:
            results.append(("Templates", "PASS", f"{len(templates)} template files found"))
        else:
            results.append(("Templates", "WARN", "Templates directory exists but no .md files found"))
    else:
        results.append(("Templates", "FAIL", f"Missing directory: {template_dir.relative_to(repo_root)}"))

    # 5. CLI version check
    pyproject = repo_root / "pyproject.toml"
    if pyproject.exists():
        results.append(("CLI Version", "PASS", f"pyproject.toml found"))
    else:
        results.append(("CLI Version", "WARN", "pyproject.toml not found — CLI may not be installed"))

    # 6. Module check
    modules_dir = repo_root / ".sdd-modules" / "modules"
    if modules_dir.exists():
        modules = [d for d in modules_dir.iterdir() if d.is_dir()]
        if modules:
            results.append(("Modules", "PASS", f"{len(modules)} modules found"))
        else:
            results.append(("Modules", "WARN", "Modules directory exists but no modules found"))
    else:
        results.append(("Modules", "WARN", "No modules directory found"))

    # 6b. Module integrity (Wave 20 §20.C.6) — hash drift check on installed modules.
    try:
        from sdd.utils import module_integrity

        verify_results = module_integrity.verify_all(repo_root)
        drift_rows: list[tuple[str, str, str]] = []
        clean = 0
        skipped = 0
        for vr in verify_results:
            if not vr.has_baseline:
                skipped += 1
                continue
            if vr.is_clean:
                clean += 1
                continue
            for d in vr.file_drifts:
                if d.actual is None:
                    drift_rows.append(("Module Integrity", "WARN",
                                       f"{vr.module}: file missing {d.path}"))
                else:
                    drift_rows.append(("Module Integrity", "WARN",
                                       f"{vr.module}: drift {d.path} ({d.expected[:8]} → {d.actual[:8]})"))
            if (vr.expected_manifest_sha256 and vr.actual_manifest_sha256
                    and vr.expected_manifest_sha256 != vr.actual_manifest_sha256
                    and not vr.file_drifts):
                drift_rows.append(("Module Integrity", "WARN",
                                   f"{vr.module}: manifest sha256 drift"))
        if verify_results:
            if drift_rows:
                results.extend(drift_rows)
            elif clean > 0:
                results.append(("Module Integrity", "PASS",
                                f"{clean} module(s) hash-clean ({skipped} without baseline)"))
            elif skipped > 0:
                results.append(("Module Integrity", "WARN",
                                f"No modules have a hash baseline yet ({skipped} module(s))"))
    except Exception as exc:  # noqa: BLE001 — doctor must never crash
        results.append(("Module Integrity", "WARN", f"check skipped: {exc}"))

    # 6c. Deprecated CLI flags (Wave 20 §20.C.10) — scan config + scripts.
    try:
        from sdd.utils import deprecation

        deprecated_hits = deprecation.scan_repo_for_deprecated_usage(repo_root)
        if deprecated_hits:
            for hit in deprecated_hits:
                results.append((
                    "CLI Deprecations",
                    "WARN",
                    f"{hit.flag} used in {hit.path}:{hit.line_no} (replacement: {hit.replacement})",
                ))
        else:
            results.append(("CLI Deprecations", "PASS",
                            "No deprecated CLI flags detected in committed scripts/config"))
    except Exception as exc:  # noqa: BLE001
        results.append(("CLI Deprecations", "WARN", f"check skipped: {exc}"))

    # 7. Schema check
    schema_dir = specify / "schemas"
    if schema_dir.exists():
        schemas = list(schema_dir.glob("*.json"))
        valid = 0
        invalid = 0
        for s in schemas:
            try:
                json.loads(s.read_text(encoding="utf-8"))
                valid += 1
            except (json.JSONDecodeError, OSError):
                invalid += 1
                results.append(("Schemas", "FAIL", f"Invalid JSON: {s.name}"))
        if invalid == 0 and valid > 0:
            results.append(("Schemas", "PASS", f"{valid} valid JSON schemas"))
    else:
        results.append(("Schemas", "WARN", "No schemas directory found"))

    # Print results
    print("\nSDD Doctor — Framework Health Check\n")
    has_fail = False
    for category, status, detail in results:
        marker = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}.get(status, "?")
        print(f"  {marker} {status:<4}  {category:<15} {detail}")
        if status == "FAIL":
            has_fail = True

    print()
    if has_fail:
        output.error("Framework health check found FAIL conditions — see above")
        return 1
    else:
        output.success("Framework health check passed")
        return 0
