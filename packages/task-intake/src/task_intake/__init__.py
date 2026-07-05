"""Task Intake — structured task objects for engineering requests."""

from task_intake.schema import RiskHint, TargetCapability, Task, TaskIntent
from task_intake.intake import TaskIntake

__all__ = ["TaskIntake", "Task", "TaskIntent", "RiskHint", "TargetCapability"]
__version__ = "0.1.0"
