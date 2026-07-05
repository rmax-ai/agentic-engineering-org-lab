"""Agent adapter protocol and implementations."""

from agent_adapters.protocol import AgentAdapter, AgentRunInput, AgentRunResult
from agent_adapters.mock import MockAgentAdapter
from agent_adapters.patch_only import PatchOnlyAdapter

__all__ = ["AgentAdapter", "AgentRunInput", "AgentRunResult", "MockAgentAdapter", "PatchOnlyAdapter"]
__version__ = "0.1.0"
