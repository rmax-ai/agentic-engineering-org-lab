"""World Model Builder — machine-readable org topology."""

from world_model.schema import DependencyEdge, OrgGraph, Service
from world_model.builder import OrgGraphBuilder

__all__ = ["OrgGraph", "Service", "DependencyEdge", "OrgGraphBuilder"]
__version__ = "0.1.0"
