"""Autofix Loop — bounded retry with structured failure evidence."""

from dataclasses import dataclass, field
from typing import Any

from agent_adapters.protocol import AgentAdapter, AgentRunInput, AgentRunResult
from verification_harness.harness import VerificationHarness, VerificationReport


@dataclass
class FailurePacket:
    """Structured failure evidence sent back to the agent for retry."""

    failed_checks: list[dict[str, str]] = field(default_factory=list)
    review_findings: list[dict[str, str]] = field(default_factory=list)
    allowed_scope: list[str] = field(default_factory=list)
    attempt: int = 0
    max_attempts: int = 3


@dataclass
class AutofixResult:
    task_id: str
    success: bool
    attempts: int
    final_verification: VerificationReport | None = None
    failure_packets: list[FailurePacket] = field(default_factory=list)
    summary: str = ""


class AutofixLoop:
    """Bounded retry loop for agent-generated patches.

    When verification or review fails, the loop sends structured failure
    evidence back to the agent and allows up to max_attempts retries.
    """

    def __init__(self, adapter: AgentAdapter, max_attempts: int = 3):
        self.adapter = adapter
        self.max_attempts = max_attempts
        self.verifier = VerificationHarness()

    async def run(self, task_id: str, modified_files: list[str],
                  required_checks: list[str] | None = None,
                  allowed_scope: list[str] | None = None) -> AutofixResult:
        """Run the autofix loop.

        Returns when checks pass or max_attempts is exhausted.
        """
        packets: list[FailurePacket] = []

        for attempt in range(1, self.max_attempts + 1):
            ver_result = self.verifier.verify(task_id, modified_files, required_checks)

            if ver_result.passed:
                return AutofixResult(
                    task_id=task_id,
                    success=True,
                    attempts=attempt,
                    final_verification=ver_result,
                    failure_packets=packets,
                    summary=f"All checks passed on attempt {attempt}",
                )

            # Build failure packet
            packet = FailurePacket(
                failed_checks=[
                    {"name": c.name, "summary": c.error_summary}
                    for c in ver_result.failed_checks
                ],
                allowed_scope=allowed_scope or [],
                attempt=attempt,
                max_attempts=self.max_attempts,
            )
            packets.append(packet)

            # Agent retry (mock adapter handles this)
            await self.adapter.run(AgentRunInput(
                task_id=task_id,
                workspace_path="/tmp",
                context_pack_path="/tmp",
            ))

        return AutofixResult(
            task_id=task_id,
            success=False,
            attempts=self.max_attempts,
            failure_packets=packets,
            summary=f"Autofix exhausted after {self.max_attempts} attempts",
        )
