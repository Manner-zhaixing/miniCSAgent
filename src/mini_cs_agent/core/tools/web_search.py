"""Exa AI 联网搜索工具。

Exa 是专为 AI Agent 设计的搜索引擎：
- 多种搜索模式：auto / instant(~250ms) / fast / deep-lite / deep / deep-reasoning
- Token 高效的高亮摘要提取
- 结构化 JSON 输出

获取 API Key: https://dashboard.exa.ai
API 文档: https://docs.exa.ai/reference/search
"""

from langchain_core.tools import tool

from mini_cs_agent.core.config import WebSearchConfig

# 延迟初始化，仅在模型实际调用搜索工具时创建客户端
_exa_client = None
_config: WebSearchConfig | None = None


def init_search(config: WebSearchConfig) -> None:
    """注入应用启动时已经加载并校验过的搜索配置。"""
    global _config, _exa_client
    _config = config
    _exa_client = None


def _get_exa_client():
    """获取或创建 Exa client（单例，延迟初始化）。"""
    global _exa_client
    if _exa_client is None:
        if _config is None or not _config.enabled:
            raise ValueError(
                "Web search is disabled in config.yaml. "
                "Get a free API key (1,000 requests/month) at https://dashboard.exa.ai"
            )

        api_key = _config.api_key.get_secret_value()
        from exa_py import Exa

        _exa_client = Exa(api_key=api_key)
    return _exa_client


def _parse_results(response, query: str) -> str:
    """将 Exa 搜索结果格式化为 LLM 友好的文本。"""
    results = getattr(response, "results", [])
    if not results:
        return f'No results found for "{query}".'

    lines = [f'Search results for "{query}":\n']
    for i, r in enumerate(results, 1):
        title = getattr(r, "title", "Untitled")
        url = getattr(r, "url", "")
        highlights = getattr(r, "highlights", [])

        lines.append(f"{i}. {title}")
        if url:
            lines.append(f"   URL: {url}")
        if highlights:
            lines.append(f"   Highlights: {' | '.join(highlights[:3])}")
        lines.append("")

    return "\n".join(lines).strip()


@tool
def web_search(query: str, count: int = 5) -> str:
    """搜索互联网获取最新信息。

    当你需要查询实时信息、新闻、文档或不确定的事实时使用此工具。
    返回每条结果的标题、URL 和高亮摘要。

    Args:
        query: 搜索关键词
        count: 返回结果数量（默认 5，最大 20）
    """
    count = max(1, min(count, 20))

    try:
        exa = _get_exa_client()
        response = exa.search(
            query,
            num_results=count,
            type="auto",
            contents={"highlights": True},
        )
    except ValueError as e:
        return f"Error: {e}"
    except Exception as e:
        error_msg = str(e)
        # 识别常见错误
        if "401" in error_msg or "unauthorized" in error_msg.lower():
            return (
                "Error: Exa API key is invalid. "
                "Check config.yaml, get a valid key at https://dashboard.exa.ai"
            )
        if "402" in error_msg or "quota" in error_msg.lower() or "limit" in error_msg.lower():
            return (
                "Error: Exa API quota exceeded. "
                "Upgrade at https://exa.ai/pricing or wait for monthly quota reset."
            )
        if "429" in error_msg or "rate" in error_msg.lower():
            return "Error: Rate limit hit. Please wait a moment and try again."
        return f"Error: Search failed — {error_msg}"

    return _parse_results(response, query)
