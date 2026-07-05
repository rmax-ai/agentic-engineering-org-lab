"""Verification Harness — runs deterministic checks against generated patches."""

from dataclasses import dataclass, field
from enum import StrEnum


class CheckStatus(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class CheckResult:
    name: str
    status: CheckStatus
    error_summary: str = ""


@dataclass
class VerificationReport:
    task_id: str
    status: CheckStatus = CheckStatus.PASSED
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.status == CheckStatus.PASSED

    @property
    def failed_checks(self) -> list[CheckResult]:
        return [c for c in self.checks if c.status == CheckStatus.FAILED]

    def summary(self) -> str:
        passed = sum(1 for c in self.checks if c.status == CheckStatus.PASSED)
        failed = sum(1 for c in self.checks if c.status == CheckStatus.FAILED)
        return f"VerificationReport({passed} passed, {failed} failed)"


class VerificationHarness:
    """Run deterministic checks against a generated patch.

    Checks include: unit tests, lint, typecheck, security rules,
    file boundary checks, and policy compliance.

    In this lab implementation, checks are simulated (no real subprocess execution).
    A real implementation would run actual test/lint/typecheck commands.
    """

    REQUIRED_CHECKS = ["unit_tests", "lint", "typecheck", "file_boundaries", "policy_check"]

    def verify(self, task_id: str, modified_files: list[str],
               required_checks: list[str] | None = None) -> VerificationReport:
        """Run verification checks.

        Args:
            task_id: The task being verified.
            modified_files: Files modified by the agent.
            required_checks: Which checks to run. Defaults to all.

        Returns:
            VerificationReport with per-check results.
        """
        checks_to_run = required_checks or self.REQUIRED_CHECKS
        results: list[CheckResult] = []

        for check_name in checks_to_run:
            handler = getattr(self, f"_check_{check_name}", None)
            if handler:
                result = handler(modified_files)
            else:
                result = CheckResult(name=check_name, status=CheckStatus.SKIPPED)
            results.append(result)

        overall = CheckStatus.FAILED if any(
            r.status == CheckStatus.FAILED for r in results
        ) else CheckStatus.PASSED

        return VerificationReport(task_id=task_id, status=overall, checks=results)

    # ── Individual checks ──────────────────────────────────────────────

    def _check_unit_tests(self, files: list[str]) -> CheckResult:
        if not any("test_" in f for f in files):
            return CheckResult(name="unit_tests", status=CheckStatus.FAILED,
                               error_summary="No test files were modified")
        return CheckResult(name="unit_tests", status=CheckStatus.PASSED)

    def _check_lint(self, files: list[str]) -> CheckResult:
        if not files:
            return CheckResult(name="lint", status=CheckStatus.FAILED,
                               error_summary="No files to lint")
        return CheckResult(name="lint", status=CheckStatus.PASSED)

    def _check_typecheck(self, files: list[str]) -> CheckResult:
        return CheckResult(name="typecheck", status=CheckStatus.PASSED)

    def _check_file_boundaries(self, files: list[str]) -> CheckResult:
        blocked = [f for f in files if ".env" in f or "secret" in f.lower()]
        if blocked:
            return CheckResult(name="file_boundaries", status=CheckStatus.FAILED,
                               error_summary=f"Blocked files modified: {blocked}")
        return CheckResult(name="file_boundaries", status=CheckStatus.PASSED)

    def _check_policy_check(self, files: list[str]) -> CheckResult:
        return CheckResult(name="policy_check", status=CheckStatus.PASSED)
