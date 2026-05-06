"""`sdd new <name>` — create a new feature spec scaffold."""

from __future__ import annotations

import argparse
import subprocess

from sdd.utils.config import find_repo_root, script_command, get_env, ps_arg
from sdd.utils import output


def add_new_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "new",
        help="create a new feature spec",
        description="Scaffold a new feature specification under .specify/specs/.",
    )
    p.add_argument("name", metavar="<name>", help="short kebab-case feature name")
    p.add_argument(
        "-l",
        "--level",
        metavar="LEVEL",
        default=None,
        help="ceremony level (1=minimal … 4=enterprise)",
    )
    p.add_argument(
        "--template",
        metavar="TEMPLATE",
        default=None,
        help="optional scaffold template name (e.g., standard, full)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="show what would be created without writing files",
    )
    p.add_argument(
        "--worktree",
        action="store_true",
        default=False,
        help="create an isolated git worktree for this feature",
    )
    p.add_argument(
        "--execution-mode",
        metavar="MODE",
        default=None,
        choices=("standard", "autonomous-guided", "autonomous-governed"),
        help="execution mode for the new feature",
    )
    p.add_argument(
        "--autonomy-budget",
        metavar="N",
        type=int,
        default=None,
        help="maximum autonomous cycles (used with non-standard execution modes)",
    )
    p.add_argument(
        "--progressive",
        action="store_true",
        default=False,
        help="enable progressive planning (sketch-then-refine) for multi-phase features",
    )
    p.add_argument(
        "--with-reasoning",
        action="store_true",
        default=False,
        help="activate the RTC reasoning protocol (Restate → Ideate → Reflect → Score → Respond) for spec/architect agents on this feature",
    )
    p.add_argument(
        "--on-branch",
        action="store_true",
        default=False,
        help="create the feature workspace without asserting any specific branch-name pattern; pins feature.lock.json to the current branch (works on release/*, hotfix/*, free-form names)",
    )


def run_new(args: argparse.Namespace) -> int:
    try:
        repo_root = find_repo_root()
    except FileNotFoundError as exc:
        output.error(str(exc))
        return 2

    cmd = script_command("new-feature", repo_root) + [args.name]
    if args.level is not None:
        cmd += ["-l", str(args.level)]
    if args.template is not None:
        cmd += [ps_arg("--template"), str(args.template)]
    if getattr(args, "dry_run", False):
        cmd += [ps_arg("--dry-run")]
    if getattr(args, "worktree", False):
        cmd += [ps_arg("--worktree")]
    if getattr(args, "execution_mode", None) is not None:
        cmd += [ps_arg("--execution-mode"), str(args.execution_mode)]
    if getattr(args, "autonomy_budget", None) is not None:
        cmd += [ps_arg("--autonomy-budget"), str(args.autonomy_budget)]
    if getattr(args, "progressive", False):
        cmd += [ps_arg("--progressive")]
    if getattr(args, "with_reasoning", False):
        cmd += [ps_arg("--with-reasoning")]
    if getattr(args, "on_branch", False):
        cmd += [ps_arg("--on-branch")]

    try:
        result = subprocess.run(cmd, env=get_env(repo_root), cwd=repo_root)
        return result.returncode if result.returncode in (0, 1) else 2
    except Exception as exc:
        output.error(str(exc))
        return 2
