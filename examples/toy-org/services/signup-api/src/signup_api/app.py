"""Signup API — FastAPI application."""

import uuid
from datetime import datetime, UTC

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

from signup_api.validators import validate_email, validate_name, validate_password

app = FastAPI(title="signup-api", version="0.1.0")


class SignupRequest(BaseModel):
    email: str
    password: str
    name: str

    @field_validator("email")
    @classmethod
    def _check_email(cls, v: str) -> str:
        if not validate_email(v):
            raise ValueError("Invalid email format")
        return v

    @field_validator("password")
    @classmethod
    def _check_password(cls, v: str) -> str:
        if not validate_password(v):
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("name")
    @classmethod
    def _check_name(cls, v: str) -> str:
        if not validate_name(v):
            raise ValueError("Name must not be empty and max 100 characters")
        return v


class SignupResponse(BaseModel):
    status: str
    user_id: str
    created_at: str


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = exc.errors()
    msg = errors[0]["msg"] if errors else "Validation error"
    return JSONResponse(status_code=400, content={"error": msg})


@app.get("/health")
async def health() -> dict:
    return {"status": "healthy"}


@app.post("/signup")
async def signup(request: SignupRequest) -> dict:
    user_id = str(uuid.uuid4())
    created_at = datetime.now(UTC).isoformat()
    return {"status": "ok", "user_id": user_id, "created_at": created_at}
