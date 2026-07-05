"""Evaluation runner for delegation classifier."""

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from task_intake.intake import TaskIntake
from delegation_classifier.classifier import DelegationClassifier
from delegation_classifier.schema import DelegationLabel


class EvalTaskResult(BaseModel):
    task_id: str
    title: str
    expected: str
    actual: str
    correct: bool
    confidence: float


class EvalReport(BaseModel):
    results: list[EvalTaskResult] = Field(default_factory=list)
    accuracy: float = 0.0
    total: int = 0
    correct: int = 0
    per_label: dict[str, dict[str, int]] = Field(default_factory=dict)


def load_benchmark(path: str | Path) -> list[dict[str, Any]]:
    """Load benchmark tasks from YAML."""
    with open(path) as f:
        data = yaml.safe_load(f)
    return data.get("tasks", [])


def run_evaluation(benchmark_path: str | Path) -> EvalReport:
    """Run the full evaluation pipeline.

    Args:
        benchmark_path: Path to benchmark.yaml.

    Returns:
        EvalReport with results and metrics.
    """
    tasks = load_benchmark(benchmark_path)
    intake = TaskIntake()
    classifier = DelegationClassifier()

    results: list[EvalTaskResult] = []

    for task_data in tasks:
        # Intake: NL → structured task
        structured = intake.classify(task_data["title"], task_data["description"])

        # Classify: task → delegation decision
        decision = classifier.classify(structured)

        correct = decision.decision == task_data["expected_decision"]
        results.append(
            EvalTaskResult(
                task_id=task_data["id"],
                title=task_data["title"],
                expected=task_data["expected_decision"],
                actual=decision.decision,
                correct=correct,
                confidence=decision.confidence,
            )
        )

    total = len(results)
    correct_count = sum(1 for r in results if r.correct)
    accuracy = correct_count / total if total > 0 else 0.0

    # Per-label stats
    per_label: dict[str, dict[str, int]] = {}
    for label in DelegationLabel:
        per_label[label] = {"total": 0, "correct": 0}
    for r in results:
        per_label[r.expected]["total"] += 1
        if r.correct:
            per_label[r.expected]["correct"] += 1

    return EvalReport(
        results=results,
        accuracy=round(accuracy, 3),
        total=total,
        correct=correct_count,
        per_label=per_label,
    )


def print_report(report: EvalReport) -> None:
    """Print a human-readable evaluation report."""
    print("=" * 60)
    print("  DELEGATION CLASSIFIER — BENCHMARK EVALUATION")
    print("=" * 60)
    print()

    for r in report.results:
        status = "✓" if r.correct else "✗"
        print(f"  [{status}] {r.task_id}: {r.title[:60]}")
        if not r.correct:
            print(f"       Expected: {r.expected:25s}  Actual: {r.actual}")
        print(f"       Confidence: {r.confidence:.2f}")
        print()

    print("-" * 60)
    print(f"  Accuracy: {report.accuracy:.0%} ({report.correct}/{report.total})")
    print()

    print("  Per-Label Accuracy:")
    for label, stats in report.per_label.items():
        if stats["total"] > 0:
            pct = stats["correct"] / stats["total"]
            print(f"    {label:30s}: {stats['correct']}/{stats['total']} ({pct:.0%})")

    # Compute false-safe rate
    auto_tasks = [r for r in report.results if r.expected == "auto_delegate"]
    false_safe = [r for r in auto_tasks if r.actual == "reject_unsafe"]
    if auto_tasks:
        print(f"\n  False-safe rate (safe → reject): {len(false_safe)}/{len(auto_tasks)}")
    print("=" * 60)
