"""OrgGraph builder — orchestrates parsing and builds the dependency graph."""

import json
from pathlib import Path

from world_model.parser import ServiceParser
from world_model.schema import DependencyEdge, OrgGraph, Service


class OrgGraphBuilder:
    """Build an OrgGraph from a toy organization directory."""

    def __init__(self, org_root: str | Path):
        self.org_root = Path(org_root).resolve()
        if not self.org_root.is_dir():
            raise NotADirectoryError(f"Not a directory: {self.org_root}")

    def build(self) -> OrgGraph:
        """Parse all service.yaml files and build the full organization graph.

        Returns:
            An OrgGraph containing all services and their dependency edges.
        """
        service_dirs = ServiceParser.discover_service_dirs(self.org_root)
        services: list[Service] = []
        edges: list[DependencyEdge] = []

        for svc_dir in service_dirs:
            svc_yaml = svc_dir / "service.yaml"
            service = ServiceParser.parse_file(svc_yaml)
            services.append(service)

            for dep_name in service.dependencies:
                edges.append(
                    DependencyEdge(
                        from_service=service.name,
                        to_service=dep_name,
                    )
                )

        # Validate: warn about dangling references but don't fail
        service_names = {s.name for s in services}
        for edge in edges:
            if edge.to_service not in service_names:
                import warnings
                warnings.warn(
                    f"Service '{edge.from_service}' depends on unknown service '{edge.to_service}'",
                )

        return OrgGraph(
            services=services,
            edges=edges,
            metadata={
                "org_root": str(self.org_root),
                "service_count": str(len(services)),
                "edge_count": str(len(edges)),
            },
        )

    def save(self, graph: OrgGraph, output_path: str | Path | None = None) -> Path:
        """Save the graph as JSON.

        Args:
            graph: The OrgGraph to save.
            output_path: Path to write JSON to. Defaults to org_root/world_model.json.

        Returns:
            Path where the file was saved.
        """
        if output_path is None:
            output_path = self.org_root / "world_model.json"
        else:
            output_path = Path(output_path)

        data = graph.model_dump(exclude={"metadata"})
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

        return output_path

    def load(self, path: str | Path | None = None) -> OrgGraph:
        """Load a previously saved OrgGraph from JSON.

        Args:
            path: Path to JSON file. Defaults to org_root/world_model.json.

        Returns:
            The loaded OrgGraph.
        """
        if path is None:
            path = self.org_root / "world_model.json"
        else:
            path = Path(path)

        with open(path) as f:
            data = json.load(f)

        return OrgGraph(
            services=[Service(**s) for s in data["services"]],
            edges=[DependencyEdge(**e) for e in data["edges"]],
        )
