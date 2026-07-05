# PYTHON_DEVELOPMENT.md — Day-to-Day Engineering for Agentic Engineering Org Lab

## Project Structure

Every Python package follows the `src/` layout:

```
packages/task-intake/
  pyproject.toml
  src/
    task_intake/
      __init__.py
      intake.py
      schema.py
      classifier.py
  tests/
    test_intake.py
    test_schema.py
```

## Language Version

- **Python 3.12+** — use modern features: `str | None` over `Optional[str]`,
  `list[Task]` over `List[Task]`, `datetime.now(UTC)` over `datetime.utcnow()`

## Schema Definition (Pydantic v2)

All data models use Pydantic v2. Follow these patterns:

```python
from datetime import datetime, UTC
from enum import StrEnum
from pydantic import BaseModel, Field

class TaskStatus(StrEnum):
    PENDING = "pending"
    CLASSIFIED = "classified"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class Task(BaseModel):
    id: str = Field(default_factory=lambda: f"task_{_ulid()}")
    title: str
    description: str
    requester: str
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

# Legacy enums with lowercase values — use StrEnum for auto-serialization.
# If using regular Enum, add @field_validator for case normalization.
```

**Gotchas:**
- `model_config` is a Pydantic v2 reserved attribute name. Never use it as a field.
- Cross-module forward references: use string annotations + `model_rebuild()`.
- Enum fields in SQLModel: use `.value` for storage, not the enum object directly.

## Async Patterns

FastAPI handlers are async. Database calls use SQLAlchemy async:

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

engine = create_async_engine("sqlite+aiosqlite:///trace.db")
async_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
```

**Rule:** Use `aiosqlite` for SQLite async. Don't use synchronous SQLite in async
contexts — it blocks the event loop.

## Error Handling

```python
class ControlPlaneError(Exception):
    """Base exception for all control plane errors."""

class TaskClassificationError(ControlPlaneError):
    """Failed to classify a task."""

class SandboxExecutionError(ControlPlaneError):
    """Sandbox execution failed."""

class AutofixExhaustedError(ControlPlaneError):
    """Autofix loop exceeded max attempts."""

# Always log with structlog
import structlog
logger = structlog.get_logger()

try:
    result = await classify_task(task)
except TaskClassificationError as e:
    logger.error("classification_failed", task_id=task.id, error=str(e))
    raise
```

## Logging

Use `structlog` for all logging:

```python
import structlog

logger = structlog.get_logger()

# Key-value pairs, not f-strings
logger.info("task_classified", task_id=task.id, decision=decision.decision)
logger.error("sandbox_timeout", sandbox_id=sandbox.id, duration_sec=timeout)
```

Configure structlog in `apps/api-server/src/api_server/logging.py`:
- JSON format for production
- Console (colored) for development
- Always include `task_id` and `module` in bound context

## Testing

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture
def toy_org_path():
    return Path(__file__).parent.parent / "examples" / "toy-org"

@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_sessionmaker(engine)() as session:
        yield session

@pytest.mark.asyncio
async def test_classify_safe_task(db_session):
    task = Task(title="Add email validation", description="...")
    result = await classify_task(task, db_session)
    assert result.decision == "auto_delegate"

# Mock Docker for sandbox tests
@pytest.fixture
def mock_docker():
    with patch("docker.from_env") as mock:
        mock.return_value.containers.run.return_value = MagicMock()
        yield mock
```

**Rules:**
- Use `pytest-asyncio` for async tests
- Mock Docker, not real containers, in unit tests
- Mock LLM calls with deterministic responses
- Integration tests in `evals/` test the full pipeline

## Type Checking

`ty` (not mypy) for type checking:

```toml
# pyproject.toml
[tool.ty]
packages = ["src/task_intake"]
```

Run: `uv run ty check`

Common suppression patterns:
```python
from typing import Any, cast

# For dynamic dispatch
handler: Any = get_handler(task_type)
result = cast(TaskResult, await handler(task))

# For SQLAlchemy columns
created_at: Mapped[datetime] = mapped_column(default=func.now())  # type: ignore[valid-type]
```

## Dependency Management

```toml
# pyproject.toml
[project]
name = "task-intake"
requires-python = ">=3.12"
dependencies = [
    "pydantic>=2.0",
    "openai>=1.0",
    "structlog>=24.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "ruff>=0.6",
]
```

Use `uv` for all Python operations:
```bash
uv sync                    # install deps
uv sync --extra dev        # install deps + dev deps
uv run pytest              # run tests
uv run ty check            # type check
uv run ruff format --check # format check
```

## Docker Integration

Use the Docker SDK for Python:

```python
import docker

client = docker.from_env()

container = client.containers.run(
    "agentic-org-lab-sandbox:latest",
    command=["/bin/sleep", "infinity"],
    volumes={workspace_path: {"bind": "/workspace", "mode": "rw"}},
    network_mode="none",
    mem_limit="512m",
    cpu_period=100000,
    cpu_quota=50000,
    detach=True,
)

# Execute commands
exit_code, output = container.exec_run("cd /workspace && npm test")
```

## LLM Integration

```python
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def classify_task(task: Task) -> ClassificationResult:
    response = await client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
            {"role": "user", "content": f"Classify this task:\n{task.description}"},
        ],
        response_format=ClassificationResult,
    )
    return response.choices[0].message.parsed
```

**Rules:**
- Always use structured output (`response_format`) with a Pydantic model
- Never parse JSON from raw text responses
- Handle rate limits with exponential backoff
- Log token usage per classification call

## Repository Structure Conventions

```
packages/<name>/
  pyproject.toml         # Package metadata + deps
  src/<name>/
    __init__.py           # Public API surface
    <module>.py           # Implementation
    schema.py             # Pydantic models
    service.py            # Business logic
  tests/
    test_<module>.py
  README.md               # Module documentation
```

Each package exposes its public API through `__init__.py`:
```python
# packages/task-intake/src/task_intake/__init__.py
from task_intake.schema import Task, ClassificationResult
from task_intake.intake import TaskIntake

__all__ = ["Task", "ClassificationResult", "TaskIntake"]
```

## Cross-Package Imports

```python
# Always use absolute imports from the package name
from shared.schema import Task, DelegationDecision
from world_model.graph import OrgGraph
from trace_store.events import TraceEvent, EventType
```

Install sibling packages as editable:
```toml
# In each package's pyproject.toml
[tool.uv.sources]
shared = { path = "../shared", editable = true }
world-model = { path = "../world-model", editable = true }
```
