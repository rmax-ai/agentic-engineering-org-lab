"""Tests for service.yaml parser."""

import tempfile
from pathlib import Path

import pytest

from world_model.parser import ServiceParser


def test_parse_valid_service_yaml():
    yaml_content = """\
name: test-service
type: service
language: python
owner: team-growth
risk_level: medium
dependencies:
  - validation
commands:
  test: pytest
  lint: ruff check
entrypoints:
  - src/app.py
policies:
  - validate_input
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        svc_yaml = Path(tmpdir) / "service.yaml"
        svc_yaml.write_text(yaml_content)

        service = ServiceParser.parse_file(svc_yaml)

        assert service.name == "test-service"
        assert service.type == "service"
        assert service.language == "python"
        assert service.owner == "team-growth"
        assert service.risk_level == "medium"
        assert service.dependencies == ["validation"]
        assert service.commands == {"test": "pytest", "lint": "ruff check"}
        assert service.entrypoints == ["src/app.py"]
        assert service.policies == ["validate_input"]


def test_parse_minimal_service_yaml():
    yaml_content = """\
name: minimal-svc
type: library
language: python
owner: team-platform
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        svc_yaml = Path(tmpdir) / "service.yaml"
        svc_yaml.write_text(yaml_content)

        service = ServiceParser.parse_file(svc_yaml)

        assert service.name == "minimal-svc"
        assert service.risk_level == "medium"  # default
        assert service.dependencies == []  # default
        assert service.commands == {}  # default


def test_parse_missing_required_field():
    yaml_content = "name: broken-svc\n"
    with tempfile.TemporaryDirectory() as tmpdir:
        svc_yaml = Path(tmpdir) / "service.yaml"
        svc_yaml.write_text(yaml_content)

        with pytest.raises(ValueError, match="Missing required field"):
            ServiceParser.parse_file(svc_yaml)


def test_parse_file_not_found():
    with pytest.raises(FileNotFoundError):
        ServiceParser.parse_file(Path("/nonexistent/service.yaml"))


def test_discover_service_dirs(tmp_path: Path):
    # Create a realistic structure
    svc_a = tmp_path / "services" / "api-a"
    svc_b = tmp_path / "services" / "api-b"
    lib_v = tmp_path / "libs" / "validation"

    for d in [svc_a, svc_b, lib_v]:
        d.mkdir(parents=True)
        (d / "service.yaml").write_text("name: test\ntype: service\nlanguage: python\nowner: team\n")

    # Create a dir without service.yaml
    (tmp_path / "services" / "no-yaml").mkdir(parents=True)

    dirs = ServiceParser.discover_service_dirs(tmp_path)
    names = sorted(d.name for d in dirs)

    assert names == ["api-a", "api-b", "validation"]
