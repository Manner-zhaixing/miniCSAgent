from fastapi import APIRouter

from mini_cs_agent.api.schemas import ChatRequest, ChatResponse
from mini_cs_agent.core.agent import Agent

router = APIRouter(prefix="/api/v1")

# 由 main.py 中的 create_app() 注入
_agent: Agent | None = None


def init_router(agent: Agent) -> APIRouter:
    global _agent
    _agent = agent
    return router


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    reply = await _agent.run(request.message)
    return ChatResponse(reply=reply)
