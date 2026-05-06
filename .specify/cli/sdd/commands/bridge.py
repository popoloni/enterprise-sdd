"""`sdd bridge <feature-id> [phase]` — generate a context bridge."""

from __future__ import annotations

import argparse
import subprocess

from sdd.utils.config import find_repo_root, script_command, get_env
from sdd.utils import output


def add_bridge_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "bridge",
        help="generate a context bridge for a feature",
        description="Run context-bridge.sh to compress prior-phase context into a bridge file.",
    )
    p.add_argument("feature_id", metavar="<feature-id>", help="feature identifier")
    p.add_argument(
        "phase",
        metavar="[phase]",
        nargs="?",
        default=None,
        help="optional target phase (e.g. 2.1, 3.1)",
    )


def run_bridge(args: argparse.Namespace) -> int:
    try:
        repo_root = find_repo_root()
    except FileNotFoundError as exc:
        output.error(str(exc))
        return 2

    cmd = script_command("context-bridge", repo_root) + [args.feature_id]
    if args.phase:
        cmd.append(args.phase)

    try:
        result = subprocess.run(cmd, env=get_env(repo_root), cwd=repo_root)
        return result.returncode if result.returncode in (0, 1) else 2
    except Exception as exc:
        output.error(str(exc))
        return 2
