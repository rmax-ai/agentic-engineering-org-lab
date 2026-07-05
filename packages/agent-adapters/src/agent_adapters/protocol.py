"""Agent adapter protocol — the interface all agent adapters must implement."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class AgentRunInput:
    """Input to an agent adapter run."""

    task_id: str
    workspace_path: str
    context_pack_path: str
    allowed_commands: list[str] = field(default_factory=list)
    timeout_seconds: int = 600


@dataclass
class AgentRunResult:
    """Result from an agent adapter run."""

    status: str  # "completed" | "failed" | "timeout"
    summary: str
    modified_files: list[str] = field(default_factory=list)
    diff: str = ""
    logs: str = ""
    commands_run: list[str] = field(default_factory=list)


class AgentAdapter(ABC):
    """Abstract base for agent adapters.

    Implementations wrap different coding agents (Claude Code, Codex CLI, Aider)
    behind a uniform interface so the control plane can swap agents without
    changing the pipeline.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable adapter name."""
        ...

    @abstractmethod
    async def run(self, input: AgentRunInput) -> AgentRunResult:
        """Execute the agent with the given input.

        Args:
            input: The AgentRunInput with task, workspace, context, and constraints.

        Returns:
            AgentRunResult with status, modified files, diff, and logs.
        """
        ...
