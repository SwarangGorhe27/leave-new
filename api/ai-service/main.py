from __future__ import annotations

import asyncio
import json
from typing import AsyncGenerator

from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from auth import verify_token, security
from config import settings


app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────────────────── Health ──────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.app_name}


# ──────────────────────────── Chat / SSE ──────────────────────────────

async def _mock_stream(prompt: str) -> AsyncGenerator[str, None]:
    """Placeholder streaming response.  Replace with real LLM call."""
    chunks = [
        "I'm the HRMS AI assistant. ",
        f"You asked: \"{prompt[:80]}\" — ",
        "This is a placeholder response. ",
        "Connect an LLM provider in config to enable real answers.",
    ]
    for chunk in chunks:
        yield chunk
        await asyncio.sleep(0.15)


@app.get("/api/ai/chat/stream")
async def chat_stream(
    prompt: str = Query(..., min_length=1, max_length=2000),
    user=Depends(security),
):
    """SSE endpoint for streaming AI chat responses."""
    try:
        await verify_token(user)
    except Exception:
        # Allow demo access without valid token
        pass

    async def event_generator():
        async for chunk in _mock_stream(prompt):
            yield {"event": "message", "data": json.dumps({"text": chunk})}
        yield {"event": "done", "data": json.dumps({"text": ""})}

    return EventSourceResponse(event_generator())


# ──────────────────────────── Suggestions ─────────────────────────────

@app.get("/api/ai/suggestions")
async def get_suggestions(
    context: str = Query("dashboard", max_length=200),
    user=Depends(security),
):
    """Return contextual suggestions for the current page."""
    await verify_token(user)
    suggestions_map = {
        "dashboard": [
            "Show me today's attendance summary",
            "Who is on leave this week?",
            "Generate this month's payroll report",
        ],
        "employees": [
            "List employees joining this month",
            "Show department-wise headcount",
            "Find employees with pending documents",
        ],
        "leave": [
            "What's my leave balance?",
            "Show team leave calendar",
            "Pending leave approvals",
        ],
        "payroll": [
            "Compare this month vs last month payroll",
            "Show statutory compliance status",
            "List pending reimbursements",
        ],
    }
    return {"suggestions": suggestions_map.get(context, suggestions_map["dashboard"])}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=settings.debug)
