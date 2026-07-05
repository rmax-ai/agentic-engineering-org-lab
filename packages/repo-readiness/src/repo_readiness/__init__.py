"""Repo Readiness Scanner — scores repositories for agent compatibility."""

from repo_readiness.schema import ReadinessCheck, ReadinessReport
from repo_readiness.scanner import RepoReadinessScanner

__all__ = ["ReadinessCheck", "ReadinessReport", "RepoReadinessScanner"]
__version__ = "0.1.0"
