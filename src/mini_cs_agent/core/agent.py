from typing import Annotated, TypedDict

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from mini_cs_agent.core.config import Config


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


class Agent:
    """最简单的 LangGraph agent：单轮调用 LLM 返回回复。"""

    def __init__(self, config: Config):
        self.llm = ChatOpenAI(
            base_url=config.DEEPSEEK_BASE_URL,
            api_key=config.DEEPSEEK_API_KEY,
            model=config.MODEL_NAME,
        )
        self.graph = self._build_graph()

    def _call_model(self, state: AgentState) -> dict:
        response = self.llm.invoke(state["messages"])
        return {"messages": [response]}

    def _build_graph(self):
        builder = StateGraph(AgentState)
        builder.add_node("call_model", self._call_model)
        builder.add_edge(START, "call_model")
        builder.add_edge("call_model", END)
        return builder.compile()

    async def run(self, message: str) -> str:
        result = await self.graph.ainvoke({"messages": [("user", message)]})
        return result["messages"][-1].content
