# PYTHON_API_DESIGN.md — FastAPI Conventions for Agentic Engineering Org Lab

## Base URL

All API routes are prefixed with `/api/v1/`.

## Response Format

### Success

```json
{
  "data": { ... },
  "meta": {
    "trace_id": "evt_abc123"
  }
}
```

### Error

```json
{
  "error": "Task not found",
  "detail": {
    "task_id": "task_001",
    "reason": "no_such_task"
  },
  "meta": {
    "trace_id": "evt_def456"
  }
}
```

## Route Naming

- **Collections:** `GET /api/v1/tasks` — list, `POST /api/v1/tasks` — create
- **Resources:** `GET /api/v1/tasks/{id}` — get, `POST /api/v1/tasks/{id}/classify` — action
- **Sub-resources:** `GET /api/v1/tasks/{id}/trace` — task's events
- **Reports:** `GET /api/v1/reports/{id}` — final report

## Pydantic Schema Patterns

### Request Models

```python
from pydantic import BaseModel, Field

class CreateTaskRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=5000)
    requester: str = Field(default="api", max_length=100)
    priority: str = Field(default="medium", pattern="^(low|medium|high|critical)$")

class ClassifyTaskRequest(BaseModel):
    pass  # No body needed — task is identified by URL param
```

### Response Models

```python
class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    requester: str
    status: str
    created_at: str  # ISO 8601

class ClassificationResponse(BaseModel):
    decision: str  # auto_delegate | human_decompose_first | etc.
    confidence: float
    reasons: list[str]
    required_checks: list[str]

class ApiResponse(BaseModel, Generic[T]):
    data: T
    meta: dict[str, str] = {}
```

### Enum Values in API

Use string enums, not integers:

```python
from enum import StrEnum

class TaskStatus(StrEnum):
    PENDING = "pending"
    CLASSIFIED = "classified"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class DelegationDecision(StrEnum):
    AUTO_DELEGATE = "auto_delegate"
    HUMAN_DECOMPOSE = "human_decompose_first"
    HUMAN_REVIEW = "human_review_required"
    REJECT_UNSAFE = "reject_unsafe"
    INSUFFICIENT_CONTEXT = "insufficient_context"
```

## FastAPI Router Patterns

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])

@router.post("", response_model=ApiResponse[TaskResponse], status_code=201)
async def create_task(
    request: CreateTaskRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[TaskResponse]:
    task = await task_service.create(request, db)
    return ApiResponse(data=TaskResponse.model_validate(task))

@router.get("/{task_id}", response_model=ApiResponse[TaskResponse])
async def get_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[TaskResponse]:
    task = await task_service.get(task_id, db)
    if not task:
        raise HTTPException(status_code=404, detail={"reason": "not_found"})
    return ApiResponse(data=TaskResponse.model_validate(task))

@router.post("/{task_id}/classify", response_model=ApiResponse[ClassificationResponse])
async def classify_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ClassificationResponse]:
    result = await classification_service.classify(task_id, db)
    return ApiResponse(data=ClassificationResponse.model_validate(result))
```

## Error Handling Middleware

```python
from fastapi import Request
from fastapi.responses import JSONResponse
import structlog

logger = structlog.get_logger()

async def error_handler(request: Request, call_next):
    try:
        return await call_next(request)
    except ControlPlaneError as e:
        logger.error("control_plane_error", error=str(e), path=str(request.url))
        return JSONResponse(
            status_code=400,
            content={"error": str(e), "detail": {"type": type(e).__name__}},
        )
    except Exception as e:
        logger.exception("unhandled_error", path=str(request.url))
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": {}},
        )
```

## Pagination

For list endpoints that could grow:

```python
from pydantic import BaseModel

class PaginationParams(BaseModel):
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)

class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    total: int
    offset: int
    limit: int

@router.get("", response_model=PaginatedResponse[TaskResponse])
async def list_tasks(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[TaskResponse]:
    tasks, total = await task_service.list(pagination.offset, pagination.limit, db)
    return PaginatedResponse(
        data=[TaskResponse.model_validate(t) for t in tasks],
        total=total,
        offset=pagination.offset,
        limit=pagination.limit,
    )
```

## Streaming (Future)

For long-running workflow execution:

```python
from fastapi.responses import StreamingResponse

@router.post("/{task_id}/run")
async def run_workflow(task_id: str):
    async def event_stream():
        async for event in workflow_service.run(task_id):
            yield f"data: {event.model_dump_json()}\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

Not implemented in MVP — workflow execution is synchronous in Phase 1-4.

## OpenAPI

FastAPI auto-generates OpenAPI docs at `/docs` and `/redoc`.

Add descriptions to routes and models:
```python
class CreateTaskRequest(BaseModel):
    """Request to create a new engineering task."""
    title: str = Field(description="Short task title (1-200 chars)")
    description: str = Field(description="Full task description with context")
```

## Versioning

- API version in URL path: `/api/v1/`
- No header-based versioning
- Breaking changes require a new major version (`/api/v2/`)
- v1 will remain stable through MVP
