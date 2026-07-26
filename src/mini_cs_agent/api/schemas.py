"""请求 / 响应数据模型。"""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., description="用户输入的消息")


class ChatResponse(BaseModel):
    reply: str = Field(..., description="AI 的回复")


# SSE 流结束标记
SSE_DONE = '{"done": true}'
