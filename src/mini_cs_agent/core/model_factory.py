"""Create LangChain chat models from validated configuration."""

from langchain_core.language_models import BaseChatModel

from mini_cs_agent.core.config import ModelConfig


def create_llm(config: ModelConfig) -> BaseChatModel:
    """Build the configured LangChain model integration."""
    api_key = config.api_key.get_secret_value()
    common = {
        "model": config.model,
        "api_key": api_key,
        "streaming": config.streaming,
        **config.options,
    }

    if config.provider == "deepseek":
        from langchain_deepseek import ChatDeepSeek

        if config.base_url:
            common["api_base"] = config.base_url
        return ChatDeepSeek(**common)

    if config.provider == "openai":
        from langchain_openai import ChatOpenAI

        if config.base_url:
            common["base_url"] = config.base_url
        return ChatOpenAI(**common)

    if config.provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        if config.base_url:
            common["base_url"] = config.base_url
        return ChatAnthropic(**common)

    raise ValueError(f"Unsupported model provider: {config.provider}")
