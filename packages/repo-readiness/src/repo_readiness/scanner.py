"""RepoReadinessScanner — scores repositories for agent compatibility."""

from pathlib import Path

from world_model.builder import OrgGraphBuilder
from world_model.schema import OrgGraph

from repo_readiness.checks import CHECK_CATALOG
from repo_readiness.schema import ReadinessCheck, ReadinessReport


class RepoReadinessScanner:
    """Scan repositories and produce readiness reports."""

    def scan(self, repo_path: str | Path) -> ReadinessReport:
        """Scan a single repository.

        Args:
            repo_path: Path to the repository root.

        Returns:
            ReadinessReport with score, rating, and recommendations.
        """
        repo_path = Path(repo_path).resolve()
        if not repo_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {repo_path}")

        repo_name = repo_path.name
        checks: list[ReadinessCheck] = []

        for check_id, description, check_fn, weight in CHECK_CATALOG:
            try:
                passed = check_fn(repo_path)
            except Exception:
                passed = False
            checks.append(
                ReadinessCheck(
                    name=check_id,
                    description=description,
                    passed=passed,
                    weight=weight,
                    detail=None if passed else f"Missing: {description}",
                )
            )

        return ReadinessReport.from_checks(repo_name, checks)

    def scan_org(self, org_root: str | Path) -> list[ReadinessReport]:
        """Scan all services and libraries in an organization.

        Args:
            org_root: Root directory of the toy organization.

        Returns:
            List of ReadinessReports, one per service/library.
        """
        builder = OrgGraphBuilder(org_root)
        graph = builder.build()
        service_dirs = builder.org_root

        reports: list[ReadinessReport] = []
        for svc in graph.services:
            # Find the service directory
            for subdir in ["services", "libs"]:
                candidate = Path(service_dirs) / subdir / svc.name
                if candidate.is_dir():
                    report = self.scan(candidate)
                    reports.append(report)
                    break

        return reports
