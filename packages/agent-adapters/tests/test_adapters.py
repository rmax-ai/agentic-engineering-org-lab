"""Tests for agent adapters."""

import pytest

from agent_adapters.protocol import AgentRunInput
from agent_adapters.mock import MockAgentAdapter
from agent_adapters.patch_only import PatchOnlyAdapter


@pytest.mark.asyncio
async def test_mock_adapter_success():
    adapter = MockAgentAdapter()
    result = await adapter.run(AgentRunInput(
        task_id="test", workspace_path="/tmp", context_pack_path="/tmp",
    ))
    assert result.status == "completed"
    assert len(result.modified_files) == 2


@pytest.mark.asyncio
async def test_mock_adapter_failure():
    adapter = MockAgentAdapter(should_fail=True)
    result = await adapter.run(AgentRunInput(
        task_id="test", workspace_path="/tmp", context_pack_path="/tmp",
    ))
    assert result.status == "failed"


@pytest.mark.asyncio
async def test_mock_adapter_fail_on_attempt():
    adapter = MockAgentAdapter(fail_on_attempt=2)
    result1 = await adapter.run(AgentRunInput(task_id="test", workspace_path="/tmp", context_pack_path="/tmp"))
    assert result1.status == "completed"
    result2 = await adapter.run(AgentRunInput(task_id="test", workspace_path="/tmp", context_pack_path="/tmp"))
    assert result2.status == "failed"


@pytest.mark.asyncio
async def test_patch_only_adapter():
    patch = "--- a/file.py\n+++ b/file.py\n@@ -1 +1 @@\n-old\n+new\n"
    adapter = PatchOnlyAdapter(patch=patch)
    result = await adapter.run(AgentRunInput(
        task_id="test", workspace_path="/tmp", context_pack_path="/tmp",
    ))
    assert result.status == "completed"
    assert "a/file.py" in result.modified_files or "file.py" in result.modified_files


@pytest.mark.asyncio
async def test_patch_only_no_patch():
    adapter = PatchOnlyAdapter()
    result = await adapter.run(AgentRunInput(
        task_id="test", workspace_path="/tmp", context_pack_path="/tmp",
    ))
    assert result.status == "failed"
