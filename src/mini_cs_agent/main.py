from contextlib import asynccontextmanager

from fastapi import FastAPI

from mini_cs_agent.core.config import load_config
from mini_cs_agent.core.agent import Agent
from mini_cs_agent.api.routes import init_router


def create_app() -> FastAPI:
    config = load_config()
    agent = Agent(config)

    app = FastAPI(
        title="Mini CS Agent",
        description="A minimal LangGraph + FastAPI agent demo powered by DeepSeek",
        version="0.1.0",
    )

    router = init_router(agent)
    app.include_router(router)

    return app
