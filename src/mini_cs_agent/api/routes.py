"""API 路由 —— FastAPI 端点定义。

- GET  /api/v1/health  — 健康检查
- POST /api/v1/chat    — SSE 流式聊天（?stream=false 可切换为非流式 JSON）
"""

import json

from fastapi import APIRouter, Query
from sse_starlette.sse import EventSourceResponse

from mini_cs_agent.api.schemas import ChatRequest, ChatResponse
from mini_cs_agent.core.agent import Agent

router = APIRouter(prefix="/api/v1")

# 由 main.py 中的 create_app() 注入
_agent: Agent | None = None


def init_router(agent: Agent) -> APIRouter:
    """注入 Agent 实例到路由模块。"""
    global _agent
    _agent = agent
    return router


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/chat")
async def chat(request: ChatRequest, stream: bool = Query(default=True)):
    """聊天端点 —— 默认 SSE 流式输出，stream=false 返回 JSON。"""
    if not stream:
        reply = await _agent.run(request.message)
        return ChatResponse(reply=reply)

    async def event_stream():
        async for event in _agent.stream(request.message):
            yield {
                "data": json.dumps(event, ensure_ascii=False),
            }

    return EventSourceResponse(event_stream())
