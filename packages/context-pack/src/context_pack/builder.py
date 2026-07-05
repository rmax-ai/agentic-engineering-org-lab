"""ContextPack builder — assembles bounded, structured context for coding agents."""

import json
from dataclasses import dataclass, field
from pathlib import Path

from task_intake.schema import Task
from world_model.schema import Service


@dataclass
class ContextPack:
    """A bounded context package for a coding agent.

    Contains only the information relevant to the current task — not a
    random dump of the entire repository.
    """

    task: dict
    affected_services: list[dict] = field(default_factory=list)
    relevant_files: list[str] = field(default_factory=list)
    agents_md: str = ""
    architecture_extract: str = ""
    policies: dict = field(default_factory=dict)
    commands: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "task": self.task,
            "affected_services": self.affected_services,
            "relevant_files": self.relevant_files,
            "agents_md": self.agents_md,
            "architecture_extract": self.architecture_extract,
            "policies": self.policies,
            "commands": self.commands,
        }

    def to_json(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        return path

    def summary(self) -> str:
        return (
            f"ContextPack({len(self.affected_services)} services, "
            f"{len(self.relevant_files)} files, "
            f"{len(self.commands)} commands)"
        )


class ContextPackBuilder:
    """Assemble bounded context for a coding agent."""

    def build(self, task: Task, services: list[Service],
              org_root: str | Path) -> ContextPack:
        """Build a context pack from a task and affected services.

        Args:
            task: The structured task.
            services: List of affected Service objects from the world model.
            org_root: Root of the toy organization.

        Returns:
            A ContextPack with bounded, structured context.
        """
        org_root = Path(org_root)

        # Collect relevant files from affected services
        relevant_files: list[str] = []
        commands: dict[str, str] = {}
        agents_md_parts: list[str] = []

        for svc in services:
            if svc.entrypoints:
                relevant_files.extend(
                    str(org_root / "services" / svc.name / ep)
                    for ep in svc.entrypoints
                    if (org_root / "services" / svc.name / ep).exists()
                )
            commands.update(svc.commands)
            agents_md_path = org_root / "services" / svc.name / "AGENTS.md"
            if agents_md_path.exists():
                agents_md_parts.append(agents_md_path.read_text())

        # Root AGENTS.md
        root_agents = org_root / "AGENTS.md"
        if root_agents.exists():
            agents_md_parts.insert(0, root_agents.read_text())

        return ContextPack(
            task=task.model_dump(),
            affected_services=[s.model_dump() for s in services],
            relevant_files=relevant_files,
            agents_md="\n\n---\n\n".join(agents_md_parts),
            commands=commands,
            policies={"human_review_required": True},
        )
