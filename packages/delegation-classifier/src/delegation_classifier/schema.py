"""Pydantic models for delegation decisions and policy configuration."""

from enum import StrEnum

from pydantic import BaseModel, Field


class DelegationLabel(StrEnum):
    AUTO_DELEGATE = "auto_delegate"
    HUMAN_DECOMPOSE_FIRST = "human_decompose_first"
    HUMAN_REVIEW_REQUIRED = "human_review_required"
    REJECT_UNSAFE = "reject_unsafe"
    INSUFFICIENT_CONTEXT = "insufficient_context"


class DelegationDecision(BaseModel):
    """The result of classifying a task for delegation."""

    task_id: str
    decision: DelegationLabel
    confidence: float = Field(ge=0.0, le=1.0)
    reasons: list[str] = Field(default_factory=list)
    required_checks: list[str] = Field(default_factory=list)
    human_review_required: bool = True
    reasoning_summary: str = ""


class PolicyConfig(BaseModel):
    """Configurable delegation policies."""

    max_autofix_attempts: int = 3
    require_human_review: bool = True
    allow_auto_merge: bool = False
    blocked_files: list[str] = Field(default_factory=lambda: ["**/.env", "**/secrets/**"])
    restricted_services: list[str] = Field(default_factory=lambda: ["billing-api"])
    required_checks: list[str] = Field(default_factory=lambda: ["tests", "lint", "typecheck"])
    risk_thresholds: dict[str, str] = Field(
        default_factory=lambda: {
            "auto_delegate_max_risk": "medium",
            "human_review_risk": "high",
            "reject_risk": "critical",
        }
    )
