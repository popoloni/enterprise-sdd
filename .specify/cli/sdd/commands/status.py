"""`sdd status [feature-id]` — show workflow status."""

from __future__ import annotations

import argparse
import subprocess

from sdd.utils.config import find_repo_root, script_command, get_env, ps_arg
from sdd.utils import output


def add_status_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "status",
        help="show workflow status",
        description="Display the current status of a feature or all features.",
    )
    p.add_argument(
        "feature_id",
        metavar="[feature-id]",
        nargs="?",
        default=None,
        help="optional feature identifier; omit to show all",
    )
    p.add_argument(
        "--autonomy",
        action="store_true",
        default=False,
        help="include autonomy evidence summary (best with a specific feature-id)",
    )
    p.add_argument(
        "--escalations",
        action="store_true",
        default=False,
        help="list pending escalation artifacts across active features",
    )
    p.add_argument(
        "--phase-ledger",
        action="store_true",
        default=False,
        help="render a phase execution ledger from existing gate artifacts (read-only; does not modify .specify/ artifacts)",
    )


def run_status(args: argparse.Namespace) -> int:
    try:
        repo_root = find_repo_root()
    except FileNotFoundError as exc:
        output.error(str(exc))
        return 2

    cmd = script_command("status", repo_root)
    if args.feature_id:
        cmd.append(args.feature_id)
    if args.autonomy:
        cmd.append(ps_arg("--autonomy"))
    if getattr(args, "escalations", False):
        cmd.append(ps_arg("--escalations"))
    if getattr(args, "phase_ledger", False):
        cmd.append(ps_arg("--phase-ledger"))

    try:
        result = subprocess.run(cmd, env=get_env(repo_root), cwd=repo_root)
        return result.returncode if result.returncode in (0, 1) else 2
    except Exception as exc:
        output.error(str(exc))
        return 2
