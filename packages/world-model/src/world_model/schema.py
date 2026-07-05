"""Pydantic models for the world model."""

from pydantic import BaseModel, Field


class Service(BaseModel):
    """A single service or library in the organization."""

    name: str
    type: str  # "service" | "library"
    language: str
    owner: str
    risk_level: str  # "low" | "medium" | "high" | "critical"
    dependencies: list[str] = Field(default_factory=list)
    commands: dict[str, str] = Field(default_factory=dict)
    entrypoints: list[str] = Field(default_factory=list)
    policies: list[str] = Field(default_factory=list)


class DependencyEdge(BaseModel):
    """A directed edge in the dependency graph."""

    from_service: str
    to_service: str
    edge_type: str = "runtime_dependency"


class OrgGraph(BaseModel):
    """The complete organization model."""

    services: list[Service] = Field(default_factory=list)
    edges: list[DependencyEdge] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)

    def get_service(self, name: str) -> Service | None:
        """Find a service by name."""
        for s in self.services:
            if s.name == name:
                return s
        return None

    def get_dependencies(self, name: str) -> list[str]:
        """Get all direct dependencies of a service."""
        return [e.to_service for e in self.edges if e.from_service == name]

    def get_dependents(self, name: str) -> list[str]:
        """Get all services that depend on this service."""
        return [e.from_service for e in self.edges if e.to_service == name]

    def summary(self) -> str:
        """Return a human-readable summary."""
        return (
            f"OrgGraph({len(self.services)} services, "
            f"{len(self.edges)} edges, "
            f"{len(self.metadata)} metadata keys)"
        )
