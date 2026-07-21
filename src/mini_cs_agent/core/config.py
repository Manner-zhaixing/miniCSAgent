from pathlib import Path
from dataclasses import dataclass

from dotenv import dotenv_values


@dataclass
class Config:
    """读取项目根目录 .env 文件，只从文件读取，不读环境变量。"""
    DEEPSEEK_API_KEY: str
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    MODEL_NAME: str = "deepseek-chat"


def load_config() -> Config:
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
    )
