"""ReAct agent backed by any configured LangChain chat model."""

from collections.abc import AsyncIterator, Iterator
from typing import Any

from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel

from mini_cs_agent.core.prompts.agent_system import AGENT_SYSTEM_PROMPT
from mini_cs_agent.core.tools import ALL_TOOLS


def _content_events(content: Any) -> Iterator[dict[str, str]]:
    """Normalize provider-specific content into the public SSE event format."""
    if isinstance(content, str):
        if content:
            yield {"type": "token", "content": content}
        return

    if not isinstance(content, list):
        return

    for block in content:
        if isinstance(block, str):
            if block:
                yield {"type": "token", "content": block}
            continue
        if not isinstance(block, dict):
            continue

        block_type = block.get("type", "")
        if block_type in {"thinking", "reasoning"}:
            reasoning = block.get("thinking") or block.get("reasoning") or block.get("text")
            if reasoning:
                yield {"type": "reasoning", "content": str(reasoning)}
        elif block_type in {"text", "output_text"}:
            text = block.get("text")
            if text:
                yield {"type": "token", "content": str(text)}


def _message_text(message: Any) -> str:
    """Extract plain response text from a LangChain message."""
    text = getattr(message, "text", None)
    if isinstance(text, str) and text:
        return text

    parts = [
        event["content"]
        for event in _content_events(getattr(message, "content", ""))
        if event["type"] == "token"
    ]
    return "".join(parts)


class Agent:
    """A provider-independent LangChain ReAct agent."""

    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.agent = create_agent(
            model=self.llm,
            tools=ALL_TOOLS,
            system_prompt=AGENT_SYSTEM_PROMPT,
        )

    async def run(self, message: str) -> str:
        """Send one message and return the complete assistant response."""
        result = await self.agent.ainvoke({"messages": [("user", message)]})
        messages = result.get("messages", [])
        for response_message in reversed(messages):
            if getattr(response_message, "type", "") == "ai":
                content = _message_text(response_message)
                if content:
                    return content
        return ""

    async def stream(self, message: str) -> AsyncIterator[dict]:
        """Stream normalized model and tool events."""
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
                if reasoning:
                    yield {"type": "reasoning", "content": reasoning}

                for content_event in _content_events(getattr(chunk, "content", "")):
                    yield content_event

            elif kind == "on_tool_start":
                name = event.get("name", "unknown")
                run_id = event.get("run_id", "")
                tool_input = event.get("data", {}).get("input", {})
                try:
                    safe_input = json.loads(json.dumps(tool_input, default=str))
                except Exception:
                    safe_input = str(tool_input)
                yield {
                    "type": "tool_start",
                    "name": name,
                    "input": safe_input,
                    "run_id": run_id,
                }

            elif kind == "on_tool_end":
                name = event.get("name", "unknown")
                run_id = event.get("run_id", "")
                output = event.get("data", {}).get("output", "")
                output_str = str(output.content) if hasattr(output, "content") else str(output or "")
                yield {
                    "type": "tool_end",
                    "name": name,
                    "output": output_str,
                    "run_id": run_id,
                }

        yield {"type": "done"}
