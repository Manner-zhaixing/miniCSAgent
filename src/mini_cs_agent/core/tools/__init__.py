"""工具注册中心 —— 集中管理所有 Agent 工具。"""

from mini_cs_agent.core.tools.web_search import web_search
from mini_cs_agent.core.tools.time import get_current_time

ALL_TOOLS = [web_search, get_current_time]

__all__ = ["ALL_TOOLS", "web_search", "get_current_time"]
