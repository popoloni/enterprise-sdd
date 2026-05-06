"""`sdd analyze <feature-id>` — run consistency analysis."""

from __future__ import annotations

import argparse
import subprocess

from sdd.utils.config import find_repo_root, script_command, get_env
from sdd.utils import output


def add_analyze_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "analyze",
        help="analyze spec consistency",
        description="Run analyze-consistency.sh to check cross-artifact consistency.",
    )
    p.add_argument(
        "feature_id",
        metavar="<feature-id>",
        nargs="?",
        default=None,
        help="feature identifier (optional — falls back to --feature, $SDD_FEATURE, feature.lock.json, branch-name heuristic)",
    )
    p.add_argument(
        "--feature",
        dest="feature_flag",
        metavar="ID",
        default=None,
        help="feature identifier (alternative to the positional argument)",
    )
    p.add_argument(
        "--gaps",
        action="store_true",
        default=False,
        help="run only gap-closure analysis (reverse traceability) instead of full gate validation",
    )
    p.add_argument(
        "--hotspots",
        action="store_true",
        default=False,
        help="compute composite-risk hotspots (LoC × churn × complexity) for files in the diff and emit HOTSPOTS.md",
    )
    p.add_argument(
        "--since",
        metavar="RANGE",
        default=None,
        help="git history window for hotspot churn (default: HEAD~100..HEAD); only used with --hotspots",
    )


def run_analyze(args: argparse.Namespace) -> int:
    try:
        repo_root = find_repo_root()
    except FileNotFoundError as exc:
        output.error(str(exc))
        return 2

    from sdd.utils.feature_resolver import resolve_feature_id
    explicit = args.feature_id or getattr(args, "feature_flag", None)
    feature_id = resolve_feature_id(repo_root, explicit)
    if not feature_id:
        output.error(
            "Could not resolve feature id. Provide it positionally, with --feature, set "
            "SDD_FEATURE, or run from inside a feature workspace with feature.lock.json."
        )
        return 2

    cmd = script_command("analyze-consistency", repo_root) + [feature_id]
    if getattr(args, "gaps", False):
        cmd.append("--gaps")
    if getattr(args, "hotspots", False):
        cmd.append("--hotspots")
        if getattr(args, "since", None):
            cmd += ["--since", str(args.since)]
    try:
        result = subprocess.run(cmd, env=get_env(repo_root), cwd=repo_root)
        return result.returncode if result.returncode in (0, 1) else 2
    except Exception as exc:
        output.error(str(exc))
        return 2
