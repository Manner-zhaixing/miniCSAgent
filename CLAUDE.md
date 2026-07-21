# CLAUDE.md

此文件为 Claude Code（claude.ai/code）在此仓库中工作时提供指导。

## 常用命令

```bash
# 安装依赖
uv sync

# 启动服务（修改代码后自动重载）
uv run uvicorn mini_cs_agent.main:create_app --factory --reload --port 8000

# 通过便捷入口脚本启动
uv run python main.py

# 健康检查
curl http://localhost:8000/api/v1/health

# 发送消息
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

目前尚未配置测试和 lint 工具。

## 架构

这是一个极简的 LangGraph + FastAPI Agent 示例项目。入口是 [src/mini_cs_agent/main.py](src/mini_cs_agent/main.py) 中的 `create_app()` —— 一个应用工厂函数，负责将配置、LangGraph Agent 和路由组装在一起。

### 请求流程

1. FastAPI 接收 `POST /api/v1/chat`，请求体为 `{"message": "..."}`。
2. [routes.py](src/mini_cs_agent/api/routes.py) 将消息传递给 `Agent.run()`。
3. [agent.py](src/mini_cs_agent/core/agent.py) 构建了一个单节点的 LangGraph `StateGraph`：`call_model` 节点调用 LLM（DeepSeek，通过 `langchain-openai` 的 `ChatOpenAI`），返回回复。
4. 回复被包装为 `ChatResponse` 返回。

### 配置加载

[config.py](src/mini_cs_agent/core/config.py) **仅**从项目根目录的 `.env` 文件读取配置（不读系统环境变量）。必填字段：`DEEPSEEK_API_KEY`。可选字段：`DEEPSEEK_BASE_URL`（默认 `https://api.deepseek.com`）、`MODEL_NAME`（默认 `deepseek-chat`）。配置 dataclass 传入 `Agent`，用于初始化 `ChatOpenAI`。

### 路由中的 Agent 注入

路由使用模块级全局变量 `_agent`，由 `init_router()` 设置。此函数在 `create_app()` 启动时调用。健康检查接口（`GET /api/v1/health`）不依赖 Agent。

### 包结构

- 仓库根目录的 `main.py` —— 便捷脚本，调用 `create_app()` 并通过代码启动 uvicorn。
- `src/mini_cs_agent/` —— 可安装的 Python 包（构建后端：hatchling）。
  - `main.py` —— 应用工厂。
  - `api/` —— FastAPI 路由和 Pydantic 数据模型。
  - `core/` —— 配置加载和 LangGraph Agent。

## 文档同步规则

- **修改代码时**，必须同步更新 `CLAUDE.md`，确保架构说明、命令、配置等与代码一致。
- **修改 `.env` 时**，必须同时更新 `.env` 和 `.env.example`，保持两者结构同步（`.env.example` 不含真实密钥值）。
- **修改代码或配置后**，检查 `README.md` 是否需要同步更新（如新增/删除接口、启动方式变化等）。
- **README.md 必须使用中文**书写。
