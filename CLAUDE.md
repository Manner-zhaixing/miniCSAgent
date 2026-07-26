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

# 非流式消息（JSON 返回）
curl -X POST 'http://localhost:8000/api/v1/chat?stream=false' \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'

# 流式消息（SSE，默认模式）
curl -N -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "搜索最新的 AI 新闻"}'
```

目前尚未配置测试和 lint 工具。

## 架构

这是一个基于 LangChain `create_agent` + FastAPI 的 ReAct Agent 项目，由 DeepSeek 驱动，集成 Exa AI 联网搜索。

入口是 [src/mini_cs_agent/main.py](src/mini_cs_agent/main.py) 中的 `create_app()` —— 一个应用工厂函数，负责将配置、Agent 和路由组装在一起。

### 请求流程

1. FastAPI 接收 `POST /api/v1/chat`，请求体为 `{"message": "..."}`。
2. [routes.py](src/mini_cs_agent/api/routes.py) 根据 `?stream=` 参数选择模式：
   - 流式（默认）：调用 `Agent.stream()`，通过 SSE 逐 token 推送回复
   - 非流式（`?stream=false`）：调用 `Agent.run()`，返回完整 JSON
3. [agent.py](src/mini_cs_agent/core/agent.py) 使用 `langchain.agents.create_agent()` 创建 ReAct Agent。Agent 基于 system_prompt 和工具列表自主决定是否需要调用工具。
4. 工具执行结果返回 LLM 综合后，回复通过路由返回给客户端。

### 配置加载

[config.py](src/mini_cs_agent/core/config.py) **仅**从项目根目录的 `.env` 文件读取配置（不读系统环境变量）。必填字段：`DEEPSEEK_API_KEY`。可选字段：`DEEPSEEK_BASE_URL`（默认 `https://api.deepseek.com`）、`MODEL_NAME`（默认 `deepseek-chat`）、`EXA_API_KEY`（Exa 搜索 API Key，获取地址：https://dashboard.exa.ai）。

### 工具

- `web_search` ([tools/web_search.py](src/mini_cs_agent/core/tools/web_search.py)) —— Exa AI 搜索工具，支持 auto 模式搜索和 highlights 摘要提取。

新工具添加到 [tools/__init__.py](src/mini_cs_agent/core/tools/__init__.py) 的 `ALL_TOOLS` 列表中即可注册。

### 系统提示词

系统提示词独立存放在 [prompts/](src/mini_cs_agent/core/prompts/) 目录中，当前包含 `agent_system.py`。

### 路由中的 Agent 注入

路由使用模块级全局变量 `_agent`，由 `init_router()` 设置。此函数在 `create_app()` 启动时调用。健康检查接口（`GET /api/v1/health`）不依赖 Agent。

### 包结构

- 仓库根目录的 `main.py` —— 便捷脚本，调用 `create_app()` 并通过代码启动 uvicorn。
- `src/mini_cs_agent/` —— 可安装的 Python 包（构建后端：hatchling）。
  - `main.py` —— 应用工厂。
  - `api/` —— FastAPI 路由和 Pydantic 数据模型。
  - `core/` —— 配置、Agent、工具和提示词。

## 文档同步规则

- **修改代码时**，必须同步更新 `CLAUDE.md`，确保架构说明、命令、配置等与代码一致。
- **修改 `.env` 时**，必须同时更新 `.env` 和 `.env.example`，保持两者结构同步（`.env.example` 不含真实密钥值）。
- **修改代码或配置后**，检查 `README.md` 是否需要同步更新（如新增/删除接口、启动方式变化等）。
- **README.md 必须使用中文**书写。
