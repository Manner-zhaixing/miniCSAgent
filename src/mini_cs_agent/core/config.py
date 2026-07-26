from pathlib import Path
from dataclasses import dataclass

from dotenv import dotenv_values


@dataclass
class Config:
    """读取项目根目录 .env 文件配置。"""
    DEEPSEEK_API_KEY: str
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    MODEL_NAME: str = "deepseek-chat"
    EXA_API_KEY: str = ""
    ENABLE_THINKING: bool = True  # 启用 DeepSeek 深度思考（reasoning_content）


def load_config() -> Config:
    """从项目根目录 .env 文件加载配置。"""
    # src/mini_cs_agent/core/config.py -> 往上 4 层到项目根
    root = Path(__file__).resolve().parent.parent.parent.parent
    env_file = root / ".env"

    if not env_file.exists():
        raise FileNotFoundError(
            f".env file not found at {env_file}. "
            f"Copy .env.example to .env and fill in your DEEPSEEK_API_KEY."
        )

    values = dotenv_values(env_file)

    api_key = values.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY is required in .env file")

    return Config(
        DEEPSEEK_API_KEY=api_key,
        DEEPSEEK_BASE_URL=values.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        MODEL_NAME=values.get("MODEL_NAME", "deepseek-chat"),
        EXA_API_KEY=values.get("EXA_API_KEY", ""),
        ENABLE_THINKING=values.get("ENABLE_THINKING", "true").lower() not in ("false", "0", "no"),
    )
