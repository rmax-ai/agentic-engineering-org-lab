"""Mock agent adapter — deterministic fake agent for testing and demos."""

from agent_adapters.protocol import AgentAdapter, AgentRunInput, AgentRunResult


class MockAgentAdapter(AgentAdapter):
    """A deterministic fake agent that produces predictable output.

    Useful for:
    - Testing the control plane pipeline without a real LLM
    - Evaluation benchmarks that need repeatable results
    - Demo scenarios with known outcomes
    """

    def __init__(self, *, should_fail: bool = False, fail_on_attempt: int = 999,
                 patch_content: str = ""):
        """
        Args:
            should_fail: If True, always returns a failure.
            fail_on_attempt: Fail on this specific attempt number (for autofix testing).
            patch_content: Pre-set diff to return as the agent's output.
        """
        self.should_fail = should_fail
        self.fail_on_attempt = fail_on_attempt
        self.patch_content = patch_content
        self._attempt = 0

    @property
    def name(self) -> str:
        return "mock-agent"

    async def run(self, input: AgentRunInput) -> AgentRunResult:
        self._attempt += 1

        if self.should_fail or self._attempt == self.fail_on_attempt:
            return AgentRunResult(
                status="failed",
                summary="Mock agent simulated failure",
                logs="mock agent error: intentional failure",
            )

        return AgentRunResult(
            status="completed",
            summary="Mock agent completed successfully",
            modified_files=["src/app.py", "tests/test_app.py"],
            diff=self.patch_content or "mock diff content",
            logs="mock agent: ran 2 commands, modified 2 files",
            commands_run=["pytest", "ruff check"],
        )
