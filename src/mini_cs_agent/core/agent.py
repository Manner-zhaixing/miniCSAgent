"""ReAct Agent —— 基于 LangChain create_agent 的智能体，由 DeepSeek 驱动。

支持：
- 非流式调用：agent.run(message) → 完整回复
- 流式调用：agent.stream(message) → 逐事件 yield（含深度思考过程）
"""

from collections.abc import AsyncIterator

from langchain.agents import create_agent
from langchain_deepseek import ChatDeepSeek

from mini_cs_agent.core.config import Config
from mini_cs_agent.core.prompts.agent_system import AGENT_SYSTEM_PROMPT
from mini_cs_agent.core.tools import ALL_TOOLS
from mini_cs_agent.core.tools.web_search import init_search


class Agent:
    """ReAct Agent —— 可以调用工具来完成任务。"""

    def __init__(self, config: Config):
        init_search(config)

        # 启用 DeepSeek 深度思考（reasoning_content）
        extra_body = {}
        if config.ENABLE_THINKING:
            extra_body = {"thinking": {"type": "enabled"}}

        self.llm = ChatDeepSeek(
            model=config.MODEL_NAME,
            api_key=config.DEEPSEEK_API_KEY,
            api_base=config.DEEPSEEK_BASE_URL,
            streaming=True,
            extra_body=extra_body,
        )

        self.agent = create_agent(
            model=self.llm,
            tools=ALL_TOOLS,
            system_prompt=AGENT_SYSTEM_PROMPT,
        )

    async def run(self, message: str) -> str:
        """非流式调用：发送消息，返回完整回复文本。"""
        result = await self.agent.ainvoke(
            {"messages": [("user", message)]}
        )
        messages = result.get("messages", [])
        for msg in reversed(messages):
            content = getattr(msg, "content", "")
            if content and getattr(msg, "type", "") == "ai":
                return content
        return ""

    async def stream(self, message: str) -> AsyncIterator[dict]:
        """流式调用：逐事件 yield，不做过滤，直接透传。

        yield 的事件格式：
          {"type": "reasoning",  "content": "..."}         — 模型深度思考（CoT）
          {"type": "token",      "content": "..."}         — 回复文本 token
          {"type": "tool_start", "name": "...", "input": {...}}  — 工具开始
          {"type": "tool_end",   "name": "...", "output": "..."} — 工具结束
          {"type": "done"}

        注意：深度思考模式下，工具调用前可能出现冗余正文（CoT 的复述），
        由前端根据后续是否出现 tool_start 来决定是否丢弃。
        """
        import json

        async for event in self.agent.astream_events(
            {"messages": [("user", message)]},
            version="v2",
        ):
            kind = event.get("event", "")

            if kind == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk")
                if chunk is None:
                    continue
                reasoning = chunk.additional_kwargs.get("reasoning_content", "")
                content = getattr(chunk, "content", "")
                if reasoning:
                    yield {"type": "reasoning", "content": reasoning}
                elif content:
                    yield {"type": "token", "content": content}

            elif kind == "on_tool_start":
                name = event.get("name", "unknown")
                tool_input = event.get("data", {}).get("input", {})
                try:
                    safe_input = json.loads(json.dumps(tool_input, default=str))
                except Exception:
                    safe_input = str(tool_input)
                yield {"type": "tool_start", "name": name, "input": safe_input}

            elif kind == "on_tool_end":
                name = event.get("name", "unknown")
                output = event.get("data", {}).get("output", "")
                if hasattr(output, "content"):
                    output_str = str(output.content)
                else:
                    output_str = str(output) if output else ""
                yield {"type": "tool_end", "name": name, "output": output_str}

        yield {"type": "done"}
