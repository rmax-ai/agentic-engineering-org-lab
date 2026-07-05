"""Delegation Classifier — decides if a task can be delegated to an agent."""

from delegation_classifier.schema import DelegationDecision, DelegationLabel, PolicyConfig
from delegation_classifier.classifier import DelegationClassifier

__all__ = ["DelegationClassifier", "DelegationDecision", "DelegationLabel", "PolicyConfig"]
__version__ = "0.1.0"
