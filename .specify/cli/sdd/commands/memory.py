"""`sdd memory status|sync|doctor <feature-id>` — memory lifecycle operations."""

from __future__ import annotations

import argparse
import subprocess

from sdd.utils.config import find_repo_root, script_command, get_env
from sdd.utils import output


_SCRIPT_MAP: dict[str, str] = {
    "status": "memory-status",
    "sync": "memory-sync",
    "doctor": "memory-doctor",
}


def add_memory_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "memory",
        help="manage structured memory lifecycle",
        description="Inspect, sync, and diagnose feature memory freshness and consistency.",
    )
    ms = p.add_subparsers(dest="memory_action", metavar="<action>")
    ms.required = True

    for action, help_text in (
        ("status", "show memory freshness and conflict indicators"),
        ("sync", "synchronize memory artifacts for a feature"),
        ("doctor", "run memory diagnostics and fail on issues"),
    ):
        sp = ms.add_parser(action, help=help_text)
        sp.add_argument("feature_id", metavar="<feature-id>", help="feature identifier")


def run_memory(args: argparse.Namespace) -> int:
    action: str = args.memory_action
    script_name = _SCRIPT_MAP.get(action)
    if script_name is None:
        output.error(f"Unknown memory action: {action}")
        return 2

    try:
        repo_root = find_repo_root()
    except FileNotFoundError as exc:
        output.error(str(exc))
        return 2

    cmd = script_command(script_name, repo_root) + [args.feature_id]
    try:
        result = subprocess.run(cmd, env=get_env(repo_root), cwd=repo_root)
        return result.returncode if result.returncode in (0, 1) else 2
    except Exception as exc:
        output.error(str(exc))
        return 2
