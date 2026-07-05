"""Pydantic models for repo readiness reports."""

from pydantic import BaseModel, Field


class ReadinessCheck(BaseModel):
    """A single readiness check result."""

    name: str
    description: str
    passed: bool
    weight: int = Field(ge=1, le=10)
    detail: str | None = None


class ReadinessReport(BaseModel):
    """Complete readiness report for a repository."""

    repo: str
    score: int = Field(ge=0, le=100)
    rating: str  # "not_ready" | "partially_ready" | "ready_with_caution" | "agent_ready"
    checks: list[ReadinessCheck] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)

    @classmethod
    def from_checks(cls, repo: str, checks: list[ReadinessCheck]) -> "ReadinessReport":
        """Build a report from check results, computing score and rating."""
        if not checks:
            return cls(repo=repo, score=0, rating="not_ready")

        total_weight = sum(c.weight for c in checks)
        passed_weight = sum(c.weight for c in checks if c.passed)
        score = round((passed_weight / total_weight) * 100) if total_weight > 0 else 0

        if score < 40:
            rating = "not_ready"
        elif score < 70:
            rating = "partially_ready"
        elif score < 90:
            rating = "ready_with_caution"
        else:
            rating = "agent_ready"

        missing = [c.name for c in checks if not c.passed]
        recommendations = [
            f"Add {c.name}: {c.description}" for c in checks if not c.passed
        ]

        return cls(
            repo=repo,
            score=score,
            rating=rating,
            checks=checks,
            missing=missing,
            recommendations=recommendations,
        )
