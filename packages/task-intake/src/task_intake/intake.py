"""TaskIntake — converts NL engineering requests to structured Task objects."""

import os
import re
import uuid

from task_intake.schema import RiskHint, TargetCapability, Task, TaskIntent

# ---------------------------------------------------------------------------
# System prompt for LLM-based classification
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an engineering task classifier for an autonomous coding agent control plane.
Your job is to analyze a natural-language engineering request and extract structured metadata.

Classify the task into exactly one of these intents:
- bug_fix: Fixing a defect or incorrect behavior
- feature_change: Adding or modifying functionality
- refactor: Restructuring code without changing behavior
- test_update: Adding or updating tests only
- cross_service_change: A change that spans multiple services
- unknown: Cannot determine from the description

Assess risk:
- low: Cosmetic changes, typo fixes, test updates
- medium: Feature changes, API modifications, validation changes
- high: Billing, payments, authentication, security-sensitive areas
- critical: Data deletion, credential changes, auth bypass

Identify target capabilities from:
- api_change, validation, tests, data_model, config, infra

Identify candidate services from the toy organization:
- signup-api (user registration)
- billing-api (payments, invoices — HIGH RISK)
- notification-worker (background notifications)
- validation (shared validation library)

Rules:
- Vague requests like "improve X" or "make it better" without specifics → requires_human_clarification = true
- Any mention of billing, payment, invoice, subscription → risk_hint = high or critical
- Multi-service changes → intent = cross_service_change
- Security keywords (disable verification, bypass auth, remove check) → risk_hint = high or critical

Respond ONLY with valid JSON matching the Task schema (without task_id or source fields)."""


# ---------------------------------------------------------------------------
# Fallback keyword rules
# ---------------------------------------------------------------------------

_INTENT_RULES: list[tuple[list[str], TaskIntent]] = [
    (["refactor", "clean", "restructure", "reorganize"], TaskIntent.REFACTOR),
    (["fix", "bug", "crash", "error", "broken", "incorrect"], TaskIntent.BUG_FIX),
    (["test", "coverage", "mock"], TaskIntent.TEST_UPDATE),
    (["add", "implement", "create", "build", "feature", "support"], TaskIntent.FEATURE_CHANGE),
]

_RISK_KEYWORDS: dict[RiskHint, list[str]] = {
    RiskHint.CRITICAL: ["disable verification", "bypass auth", "remove auth", "skip security",
                         "delete all", "drop table"],
    RiskHint.HIGH: ["billing", "payment", "invoice", "subscription", "charge", "refund",
                     "adyen", "stripe", "credentials", "secret", "password", "token"],
    RiskHint.MEDIUM: ["signup", "register", "validation", "api", "endpoint", "notification"],
    RiskHint.LOW: ["typo", "spelling", "log message", "comment", "readme", "docs",
                    "template", "branding", "color", "logo"],
}

_CAPABILITY_KEYWORDS: list[tuple[TargetCapability, list[str]]] = [
    (TargetCapability.VALIDATION, ["validat", "email", "sanitize", "check", "verify"]),
    (TargetCapability.TESTS, ["test", "coverage", "assert", "mock"]),
    (TargetCapability.API_CHANGE, ["api", "endpoint", "route", "handler", "controller"]),
    (TargetCapability.DATA_MODEL, ["model", "schema", "database", "migration", "field"]),
    (TargetCapability.CONFIG, ["config", "env", "setting", "environment"]),
    (TargetCapability.INFRA, ["docker", "deploy", "ci", "pipeline", "infra"]),
]

_SERVICE_KEYWORDS: list[tuple[str, list[str]]] = [
    ("billing-api", ["billing", "payment", "invoice", "subscription", "charge"]),
    ("signup-api", ["signup", "register", "registration", "user"]),
    ("notification-worker", ["notification", "notify", "email template", "worker"]),
    ("validation", ["validat", "email check", "sanitize"]),
]


class TaskIntake:
    """Classify natural-language engineering tasks into structured Task objects.

    Uses an LLM (OpenAI-compatible API) with structured output when available,
    falling back to keyword-based matching otherwise.
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def classify(self, title: str, description: str, task_id: str | None = None) -> Task:
        """Classify a task from its title and description.

        Args:
            title: Short task title.
            description: Full task description.
            task_id: Optional task ID. Auto-generated if not provided.

        Returns:
            A structured Task object.
        """
        task_id = task_id or f"task_{uuid.uuid4().hex[:8]}"

        # Try LLM first
        if self._llm_available():
            try:
                return self._classify_llm(title, description, task_id)
            except Exception:
                pass  # Fall through to fallback

        return self._classify_fallback(title, description, task_id)

    # ------------------------------------------------------------------
    # LLM path
    # ------------------------------------------------------------------

    @staticmethod
    def _llm_available() -> bool:
        return bool(os.environ.get("OPENAI_API_KEY"))

    def _classify_llm(self, title: str, description: str, task_id: str) -> Task:
        import json

        from openai import OpenAI

        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Title: {title}\n\nDescription: {description}"},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=500,
        )

        raw = response.choices[0].message.content or "{}"
        data = json.loads(raw)

        return Task(
            task_id=task_id,
            title=title,
            description=description,
            intent=TaskIntent(data.get("intent", "unknown")),
            risk_hint=RiskHint(data.get("risk_hint", "medium")),
            target_capabilities=[
                TargetCapability(c) for c in data.get("target_capabilities", [])
                if c in TargetCapability.__members__
            ],
            candidate_services=data.get("candidate_services", []),
            requires_human_clarification=data.get("requires_human_clarification", False),
            clarification_questions=data.get("clarification_questions", []),
            source="llm",
        )

    # ------------------------------------------------------------------
    # Fallback (keyword) path
    # ------------------------------------------------------------------

    def _classify_fallback(self, title: str, description: str, task_id: str) -> Task:
        combined = f"{title} {description}".lower()

        intent = self._match_intent(combined)
        risk_hint = self._match_risk(combined)
        capabilities = self._match_capabilities(combined)
        services = self._match_services(combined)
        needs_clarification = self._detect_vagueness(combined)

        return Task(
            task_id=task_id,
            title=title,
            description=description,
            intent=intent,
            risk_hint=risk_hint,
            target_capabilities=capabilities,
            candidate_services=services,
            requires_human_clarification=needs_clarification,
            clarification_questions=["Please provide more specific details about what needs to be done."]
            if needs_clarification
            else [],
            source="fallback",
        )

    @staticmethod
    def _match_intent(text: str) -> TaskIntent:
        for keywords, intent in _INTENT_RULES:
            if any(kw in text for kw in keywords):
                return intent
        return TaskIntent.UNKNOWN

    @staticmethod
    def _match_risk(text: str) -> RiskHint:
        for level in [RiskHint.CRITICAL, RiskHint.HIGH, RiskHint.LOW, RiskHint.MEDIUM]:
            if any(kw in text for kw in _RISK_KEYWORDS[level]):
                return level
        return RiskHint.MEDIUM  # default

    @staticmethod
    def _match_capabilities(text: str) -> list[TargetCapability]:
        caps: list[TargetCapability] = []
        for cap, keywords in _CAPABILITY_KEYWORDS:
            if any(kw in text for kw in keywords):
                caps.append(cap)
        return caps or [TargetCapability.API_CHANGE]  # default

    @staticmethod
    def _match_services(text: str) -> list[str]:
        svcs: list[str] = []
        for svc, keywords in _SERVICE_KEYWORDS:
            if any(kw in text for kw in keywords):
                svcs.append(svc)
        return svcs

    @staticmethod
    def _detect_vagueness(text: str) -> bool:
        """Detect overly vague requests."""
        # Very short descriptions are suspicious
        words = text.split()
        if len(words) < 4:
            return True
        # Generic improvement requests without specifics
        vague_phrases = [
            "make it better", "improve", "fix it", "something",
            "do the thing", "clean up", "make faster",
        ]
        if any(p in text for p in vague_phrases):
            return True
        return False
