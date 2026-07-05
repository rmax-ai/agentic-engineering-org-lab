"""Patch-only adapter — receives a structured prompt and returns a patch.

Useful for evaluation and research — the prompt defines exactly what the agent
should produce, making output predictable and measurable.
"""

from agent_adapters.protocol import AgentAdapter, AgentRunInput, AgentRunResult


class PatchOnlyAdapter(AgentAdapter):
    """An adapter that produces a pre-defined patch without running a real agent.

    The patch is provided in the context pack as a file called 'expected.patch'.
    This adapter reads it and returns it as the agent's output.
    """

    def __init__(self, patch: str = ""):
        self.patch = patch

    @property
    def name(self) -> str:
        return "patch-only"

    async def run(self, input: AgentRunInput) -> AgentRunResult:
        # In a real implementation, this would read from context_pack_path
        if not self.patch:
            return AgentRunResult(
                status="failed",
                summary="No patch provided to PatchOnlyAdapter",
            )

        files = _infer_modified_files(self.patch)

        return AgentRunResult(
            status="completed",
            summary="Patch-only adapter applied provided patch",
            modified_files=files,
            diff=self.patch,
            logs="patch-only: 1 patch applied",
        )


def _infer_modified_files(diff: str) -> list[str]:
    """Extract file paths from a unified diff."""
    files: list[str] = []
    for line in diff.splitlines():
        if line.startswith("--- ") or line.startswith("+++ "):
            path = line[4:].strip()
            if path != "/dev/null":
                files.append(path)
    return list(dict.fromkeys(files))  # dedupe, preserve order
