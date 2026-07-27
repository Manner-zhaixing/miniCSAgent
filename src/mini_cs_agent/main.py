from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

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

    # 托管 front/ 静态目录（src/mini_cs_agent/main.py → 往上 2 层到项目根）
    front_dir = Path(__file__).resolve().parent.parent.parent / "front"
    app.mount("/static", StaticFiles(directory=str(front_dir)), name="static")

    @app.get("/")
    async def index():
        return FileResponse(front_dir / "index.html")

    return app
