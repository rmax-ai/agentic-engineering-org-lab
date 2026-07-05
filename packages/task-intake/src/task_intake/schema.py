"""Task data models."""

from enum import StrEnum

from pydantic import BaseModel, Field


class TaskIntent(StrEnum):
    BUG_FIX = "bug_fix"
    FEATURE_CHANGE = "feature_change"
    REFACTOR = "refactor"
    TEST_UPDATE = "test_update"
    CROSS_SERVICE_CHANGE = "cross_service_change"
    UNKNOWN = "unknown"


class RiskHint(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TargetCapability(StrEnum):
    API_CHANGE = "api_change"
    VALIDATION = "validation"
    TESTS = "tests"
    DATA_MODEL = "data_model"
    CONFIG = "config"
    INFRA = "infra"


class Task(BaseModel):
    """A structured engineering task ingested by the control plane."""

    task_id: str
    title: str
    description: str
    requester: str = "api"
    priority: str = "medium"
    intent: TaskIntent
    risk_hint: RiskHint
    target_capabilities: list[TargetCapability] = Field(default_factory=list)
    candidate_services: list[str] = Field(default_factory=list)
    requires_human_clarification: bool = False
    clarification_questions: list[str] = Field(default_factory=list)
    source: str = "unknown"  # "llm" or "fallback"
