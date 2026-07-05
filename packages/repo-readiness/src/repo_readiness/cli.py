"""CLI entry point for the Repo Readiness Scanner."""

import argparse
import sys
from pathlib import Path

from repo_readiness.scanner import RepoReadinessScanner


def _cmd_scan(args: argparse.Namespace) -> int:
    """Scan one or all repositories."""
    scanner = RepoReadinessScanner()

    if args.all:
        reports = scanner.scan_org(Path(args.org_root))
    else:
        reports = [scanner.scan(Path(args.repo_path))]

    for report in reports:
        print(f"  {report.repo}")
        print(f"  Score:  {report.score}/100  ({report.rating})")
        for check in report.checks:
            status = "✓" if check.passed else "✗"
            print(f"    [{status}] {check.name} (weight={check.weight})")
        if report.missing:
            print(f"  Missing: {', '.join(report.missing)}")
        if report.recommendations:
            print(f"  Recommendations:")
            for rec in report.recommendations:
                print(f"    - {rec}")
        print()

    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="repo-readiness",
        description="Score repositories for autonomous agent readiness.",
    )
    sub = parser.add_subparsers(dest="command")

    p_scan = sub.add_parser("scan", help="Scan repository readiness")
    p_scan.add_argument(
        "repo_path", nargs="?", help="Path to a single repository to scan"
    )
    p_scan.add_argument(
        "--all", action="store_true", help="Scan all services in an org"
    )
    p_scan.add_argument(
        "--org-root", default=".", help="Root of toy org (with --all)"
    )

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(1)

    if args.command == "scan":
        if not args.all and not args.repo_path:
            parser.error("scan requires repo_path or --all")
        sys.exit(_cmd_scan(args))


if __name__ == "__main__":
    main()
