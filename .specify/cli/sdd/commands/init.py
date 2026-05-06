"""`sdd init` — initialise a new SDD workspace in the current directory."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from sdd.utils.config import find_repo_root, script_command, get_env
from sdd.utils import output


def add_init_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "init",
        help="initialise a new SDD workspace",
        description="Run the SDD initialisation script to scaffold .specify/ structure.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="print what would be done without making changes",
    )


def run_init(args: argparse.Namespace) -> int:
    try:
        repo_root = find_repo_root()
    except FileNotFoundError:
        repo_root = Path.cwd()

    cmd = script_command("init", repo_root)
    if getattr(args, "dry_run", False):
        output.info(f"Would run: {' '.join(cmd)}")
        return 0

    try:
        result = subprocess.run(cmd, env=get_env(repo_root), cwd=repo_root)
        return result.returncode if result.returncode in (0, 1) else 2
    except Exception as exc:
        output.error(str(exc))
        return 2
