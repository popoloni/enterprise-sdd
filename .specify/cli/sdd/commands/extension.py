"""`sdd extension validate|doctor <path>` — tailored extension diagnostics."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from sdd.utils.config import find_repo_root, script_command, get_env, ps_arg
from sdd.utils import output


_ACTION_TO_SCRIPT: dict[str, str] = {
    "validate": "extension-validate",
    "doctor": "extension-doctor",
}


def add_extension_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "extension",
        help="validate and diagnose SDD extensions",
        description="Validate extension manifests and detect extension conflicts.",
    )
    es = p.add_subparsers(dest="extension_action", metavar="<action>")
    es.required = True

    validate_p = es.add_parser("validate", help="validate an extension manifest")
    validate_p.add_argument("path", metavar="<path>", help="path to extension directory")
    validate_p.add_argument(
        "--format",
        default="generic",
        choices=["generic", "tailored"],
        help="schema profile to enforce",
    )

    doctor_p = es.add_parser("doctor", help="diagnose extension conflicts")
    doctor_p.add_argument("path", metavar="<path>", help="path to extension directory")


def run_extension(args: argparse.Namespace) -> int:
    action: str = args.extension_action
    script_name = _ACTION_TO_SCRIPT.get(action)
    if script_name is None:
        output.error(f"Unknown extension action: {action}")
        return 2

    try:
        repo_root = find_repo_root()
    except FileNotFoundError as exc:
        output.error(str(exc))
        return 2

    target = Path(args.path)
    cmd = script_command(script_name, repo_root) + [str(target)]
    if action == "validate":
        cmd += [ps_arg("--format"), str(getattr(args, "format", "generic"))]

    try:
        result = subprocess.run(cmd, env=get_env(repo_root), cwd=repo_root)
        return result.returncode if result.returncode in (0, 1) else 2
    except Exception as exc:
        output.error(str(exc))
        return 2
