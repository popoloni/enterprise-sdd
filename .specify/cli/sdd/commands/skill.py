"""`sdd skill` — local and curated skill operations."""

from __future__ import annotations

import argparse
import subprocess

from sdd.utils.config import find_repo_root, script_command, get_env, ps_arg
from sdd.utils import output


_SCRIPT_MAP: dict[str, str] = {
    "list": "skill-list",
    "validate": "skill-validate",
    "run": "skill-run",
    "validate-mapping": "validate-command-taxonomy",
}


def add_skill_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "skill",
        help="manage local SDD skills",
        description="List, validate, and run skills for the Enterprise SDD workflow.",
    )
    ss = p.add_subparsers(dest="skill_action", metavar="<action>")
    ss.required = True

    list_p = ss.add_parser("list", help="list available skills")
    list_p.add_argument(
        "--scope",
        dest="scope",
        metavar="<agent>",
        default=None,
        help="filter to skills visible to <agent> per .specify/skill-mapping.yaml (Wave 20 §20.C.3)",
    )

    validate_p = ss.add_parser("validate", help="validate one skill descriptor")
    validate_p.add_argument("name", metavar="<name>", help="skill name without .skill.md suffix")
    validate_p.add_argument(
        "--rationalizations",
        action="store_true",
        default=False,
        help="also verify that the skill contains a non-empty '## Common Rationalizations' section",
    )
    validate_p.add_argument(
        "--eval",
        dest="eval_mode",
        action="store_true",
        default=False,
        help="run the behavioral evaluation manifest (.sdd-eval.yaml) for this skill and write SKILL-EVAL-REPORT.md",
    )

    run_p = ss.add_parser("run", help="run one curated skill against a feature")
    run_p.add_argument("name", metavar="<name>", help="skill name (for example: sdd-auto-implement)")
    run_p.add_argument("feature_id", metavar="<feature-id>", help="feature identifier")
    run_p.add_argument("--dry-run", action="store_true", help="validate and print run plan without executing")

    ss.add_parser(
        "validate-mapping",
        help="validate command taxonomy mapping and curated prompt alignment",
    )


def run_skill(args: argparse.Namespace) -> int:
    action: str = args.skill_action
    script_name = _SCRIPT_MAP.get(action)
    if script_name is None:
        output.error(f"Unknown skill action: {action}")
        return 2

    try:
        repo_root = find_repo_root()
    except FileNotFoundError as exc:
        output.error(str(exc))
        return 2

    if action == "validate" and getattr(args, "eval_mode", False):
        return _run_skill_eval(args.name, repo_root)

    if action == "list" and getattr(args, "scope", None):
        return _run_skill_list_scoped(args.scope, repo_root)

    cmd = script_command(script_name, repo_root)
    if action == "validate":
        cmd.append(args.name)
        if getattr(args, "rationalizations", False):
            cmd.append("--rationalizations")
    elif action == "run":
        cmd.extend([args.name, args.feature_id])
        if args.dry_run:
            cmd.append(ps_arg("--dry-run"))

    try:
        result = subprocess.run(cmd, env=get_env(repo_root), cwd=repo_root)
        return result.returncode if result.returncode in (0, 1) else 2
    except Exception as exc:
        output.error(str(exc))
        return 2


def _run_skill_eval(skill_name: str, repo_root) -> int:
    """Execute `.sdd-eval.yaml` for a skill and emit SKILL-EVAL-REPORT.md."""
    from sdd.utils import skill_eval

    try:
        result = skill_eval.run_eval(skill_name, repo_root)
    except Exception as exc:
        output.error(f"Skill eval failed: {exc}")
        return 2
    if result is None:
        output.warn(
            f"No .sdd-eval.yaml manifest found for skill '{skill_name}' — skipping (not failing)."
        )
        return 0
    report_path = skill_eval.write_report([result], repo_root)
    output.info(f"Wrote {report_path.relative_to(repo_root)}")
    if not result.threshold_met:
        output.error(
            f"Skill '{skill_name}' eval pass-rate {result.pass_rate:.0%} below threshold "
            f"{result.pass_threshold:.0%}"
        )
        return 1
    output.success(f"Skill '{skill_name}' eval pass-rate {result.pass_rate:.0%} (threshold met)")
    return 0



def _run_skill_list_scoped(agent: str, repo_root) -> int:
    """List skills filtered by agent scope per .specify/skill-mapping.yaml."""
    from sdd.utils import skill_mapping

    entries = skill_mapping.load_mapping(repo_root)
    if not entries:
        output.warn(
            "No .specify/skill-mapping.yaml found — scope filter cannot be applied."
        )
        return 0

    visible = skill_mapping.filter_for_agent(entries, agent)
    print(f"Enterprise SDD — Skills visible to agent '{agent}'")
    print("=" * 60)
    print(f"{'NAME':<28} {'CATEGORY':<10} {'SCOPES':<28} PURPOSE")
    print(f"{'-' * 28:<28} {'-' * 10:<10} {'-' * 28:<28} -------")
    for e in visible:
        scopes_disp = ",".join(e.scopes) if e.scopes else "(global)"
        print(f"{e.id:<28} {e.category:<10} {scopes_disp:<28} {e.purpose}")
    print()
    print(f"{len(visible)} of {len(entries)} skills visible to '{agent}'")
    return 0
