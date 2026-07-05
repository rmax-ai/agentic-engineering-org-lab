"""CLI entry point for the World Model Builder."""

import argparse
import sys
from pathlib import Path

from world_model.builder import OrgGraphBuilder


def _cmd_build(args: argparse.Namespace) -> int:
    """Build the world model from an org directory."""
    builder = OrgGraphBuilder(args.org_root)
    graph = builder.build()
    output = builder.save(graph, args.output)
    print(f"World model saved to {output}")
    print(graph.summary())

    if args.verbose:
        print()
        for svc in graph.services:
            deps = graph.get_dependencies(svc.name)
            dep_str = ", ".join(deps) if deps else "none"
            print(f"  {svc.name} ({svc.type}, risk={svc.risk_level}) → depends on: {dep_str}")

    return 0


def _cmd_graph(args: argparse.Namespace) -> int:
    """Print an ASCII dependency graph."""
    builder = OrgGraphBuilder(args.org_root)
    graph = builder.build()

    print(graph.summary())
    print()

    for svc in sorted(graph.services, key=lambda s: s.name):
        deps = graph.get_dependencies(svc.name)
        deps_str = " → ".join(deps) if deps else "(none)"
        print(f"  [{svc.risk_level:>6}] {svc.name:25s} → {deps_str}")

    return 0


def _cmd_services(args: argparse.Namespace) -> int:
    """List all services."""
    builder = OrgGraphBuilder(args.org_root)
    graph = builder.build()

    for svc in sorted(graph.services, key=lambda s: s.name):
        print(f"{svc.name:25s} {svc.type:8s} {svc.risk_level:8s} {svc.owner}")

    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="world-model",
        description="Build a machine-readable model of a toy engineering organization.",
    )
    sub = parser.add_subparsers(dest="command")

    # build
    p_build = sub.add_parser("build", help="Build and save the world model as JSON")
    p_build.add_argument("org_root", help="Path to toy org root directory")
    p_build.add_argument("-o", "--output", help="Output JSON path (default: world_model.json)")
    p_build.add_argument("-v", "--verbose", action="store_true", help="Show per-service details")

    # graph
    p_graph = sub.add_parser("graph", help="Print ASCII dependency graph")
    p_graph.add_argument("org_root", help="Path to toy org root directory")

    # services
    p_svc = sub.add_parser("services", help="List all services")
    p_svc.add_argument("org_root", help="Path to toy org root directory")

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(1)

    handlers = {
        "build": _cmd_build,
        "graph": _cmd_graph,
        "services": _cmd_services,
    }

    sys.exit(handlers[args.command](args))


if __name__ == "__main__":
    main()
