"""工具注册中心 —— 集中管理所有 Agent 工具。"""

from mini_cs_agent.core.tools.web_search import web_search

ALL_TOOLS = [web_search]

__all__ = ["ALL_TOOLS", "web_search"]
