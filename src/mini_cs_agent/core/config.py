"""Application configuration loaded once from config.yaml at startup."""

from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, SecretStr, model_validator


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config.yaml"


class ModelConfig(BaseModel):
    """Configuration for one selectable LangChain chat model."""

    model_config = ConfigDict(extra="forbid")

    provider: Literal["deepseek", "openai", "anthropic"]
    model: str = Field(min_length=1)
    api_key: SecretStr = SecretStr("")
    base_url: str | None = None
    streaming: bool = True
    options: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_options(self) -> "ModelConfig":
        reserved = {"model", "api_key", "base_url", "api_base", "streaming"}
        conflicts = reserved.intersection(self.options)
        if conflicts:
            names = ", ".join(sorted(conflicts))
            raise ValueError(f"options cannot override reserved fields: {names}")
        return self


class WebSearchConfig(BaseModel):
    """Configuration for the optional Exa web search tool."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool = False
    provider: Literal["exa"] = "exa"
    api_key: SecretStr = SecretStr("")

    @model_validator(mode="after")
    def validate_api_key(self) -> "WebSearchConfig":
        if self.enabled and not self.api_key.get_secret_value():
            raise ValueError("web_search.api_key is required when web search is enabled")
        return self


class ServerConfig(BaseModel):
    """Local server settings used by the convenience main.py entry point."""

    model_config = ConfigDict(extra="forbid")

    host: str = "127.0.0.1"
    port: int = Field(default=8000, ge=1, le=65535)


class AppConfig(BaseModel):
    """Validated application configuration."""

    model_config = ConfigDict(extra="forbid")

    active_model: str = Field(min_length=1)
    models: dict[str, ModelConfig]
    web_search: WebSearchConfig = Field(default_factory=WebSearchConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)

    @model_validator(mode="after")
    def validate_active_model(self) -> "AppConfig":
        if self.active_model not in self.models:
            available = ", ".join(sorted(self.models)) or "(none)"
            raise ValueError(
                f"active_model '{self.active_model}' does not exist; "
                f"available models: {available}"
            )

        selected = self.models[self.active_model]
        if not selected.api_key.get_secret_value():
            raise ValueError(
                f"models.{self.active_model}.api_key is required for the active model"
            )
        return self

    @property
    def selected_model(self) -> ModelConfig:
        return self.models[self.active_model]


def load_config(path: Path | None = None) -> AppConfig:
    """Read and validate a YAML configuration file."""
    config_path = path or DEFAULT_CONFIG_PATH

    if not config_path.is_file():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}. "
            "Copy config.yaml.example to config.yaml and fill in the API keys."
        )

    try:
        with config_path.open("r", encoding="utf-8") as file:
            raw_config = yaml.safe_load(file)
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML in {config_path}: {exc}") from exc

    if not isinstance(raw_config, dict):
        raise ValueError(f"Configuration root must be a YAML object: {config_path}")

    return AppConfig.model_validate(raw_config)
