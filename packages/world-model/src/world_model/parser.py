"""YAML parser for service.yaml files."""

from pathlib import Path

import yaml

from world_model.schema import Service


class ServiceParser:
    """Parse service.yaml files into Service models."""

    @staticmethod
    def parse_file(path: Path) -> Service:
        """Parse a single service.yaml file.

        Args:
            path: Path to a service.yaml file.

        Returns:
            Service model.

        Raises:
            FileNotFoundError: If file doesn't exist.
            ValueError: If YAML is invalid or missing required fields.
        """
        if not path.exists():
            raise FileNotFoundError(f"service.yaml not found: {path}")

        with open(path) as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ValueError(f"Invalid YAML in {path}: expected a mapping")

        required = ["name", "type", "language", "owner"]
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required field '{field}' in {path}")

        return Service(
            name=data["name"],
            type=data["type"],
            language=data["language"],
            owner=data["owner"],
            risk_level=data.get("risk_level", "medium"),
            dependencies=data.get("dependencies", []),
            commands=data.get("commands", {}),
            entrypoints=data.get("entrypoints", []),
            policies=data.get("policies", []),
        )

    @staticmethod
    def discover_service_dirs(org_root: Path) -> list[Path]:
        """Find all directories containing a service.yaml file.

        Walks org_root/services/*/ and org_root/libs/*/ looking for service.yaml.

        Args:
            org_root: Root of the toy organization.

        Returns:
            List of directories that contain service.yaml files.
        """
        dirs: list[Path] = []
        for subdir in ["services", "libs"]:
            candidate = org_root / subdir
            if not candidate.is_dir():
                continue
            for child in sorted(candidate.iterdir()):
                if child.is_dir() and (child / "service.yaml").exists():
                    dirs.append(child)
        return dirs
