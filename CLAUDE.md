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

# 打开前端界面
open http://localhost:8000

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

这是一个基于 LangChain `create_agent` + FastAPI 的多模型 ReAct Agent 项目，集成 Exa AI 联网搜索。

入口是 [src/mini_cs_agent/main.py](src/mini_cs_agent/main.py) 中的 `create_app()` —— 一个应用工厂函数，负责将配置、Agent 和路由组装在一起。

### 请求流程

1. FastAPI 接收 `POST /api/v1/chat`，请求体为 `{"message": "..."}`。
2. [routes.py](src/mini_cs_agent/api/routes.py) 根据 `?stream=` 参数选择模式：
   - 流式（默认）：调用 `Agent.stream()`，通过 SSE 逐 token 推送回复
   - 非流式（`?stream=false`）：调用 `Agent.run()`，返回完整 JSON
3. [model_factory.py](src/mini_cs_agent/core/model_factory.py) 根据配置创建 `ChatDeepSeek`、`ChatOpenAI` 或 `ChatAnthropic`。
4. [agent.py](src/mini_cs_agent/core/agent.py) 使用 `langchain.agents.create_agent()` 创建 ReAct Agent。Agent 基于 system_prompt 和工具列表自主决定是否需要调用工具。
5. 工具执行结果返回 LLM 综合后，回复通过路由返回给客户端。

### 配置加载

[config.py](src/mini_cs_agent/core/config.py) 在应用启动时从项目根目录的 `config.yaml` 读取并校验全部配置。`active_model` 必须对应 `models` 中的一项，且当前模型必须填写 API Key。未选中的模型允许保留空 Key。`config.yaml` 不提交，配置模板为 `config.yaml.example`。

配置只加载一次，由 `create_app()` 将模型配置交给模型工厂、将搜索配置交给工具。业务模块不得自行重新调用 `load_config()`。

### 工具

- `web_search` ([tools/web_search.py](src/mini_cs_agent/core/tools/web_search.py)) —— Exa AI 搜索工具，支持 auto 模式搜索和 highlights 摘要提取。

新工具添加到 [tools/__init__.py](src/mini_cs_agent/core/tools/__init__.py) 的 `ALL_TOOLS` 列表中即可注册。

### 系统提示词

系统提示词独立存放在 [prompts/](src/mini_cs_agent/core/prompts/) 目录中，当前包含 `agent_system.py`。

### 路由中的 Agent 注入

路由使用模块级全局变量 `_agent`，由 `init_router()` 设置。此函数在 `create_app()` 启动时调用。健康检查接口（`GET /api/v1/health`）不依赖 Agent。

### 前端界面

启动服务后访问 `http://localhost:8000` 即可使用前端对话界面。前端是纯 HTML/CSS/JS 单文件，位于 [front/index.html](front/index.html)，无需构建。功能：

- SSE 流式消息实时渲染（`fetch` + `ReadableStream`）
- 深度思考内容可折叠展示（`reasoning` 事件）
- 工具调用状态标记（`tool_start` / `tool_end` 事件）
- `GET /` 返回 `front/index.html`，`StaticFiles` 挂载在 `/static`

### 包结构

- 仓库根目录的 `main.py` —— 便捷脚本，调用 `create_app()` 并通过代码启动 uvicorn。
- `src/mini_cs_agent/` —— 可安装的 Python 包（构建后端：hatchling）。
  - `main.py` —— 应用工厂。
  - `api/` —— FastAPI 路由和 Pydantic 数据模型。
  - `core/` —— 配置、Agent、工具和提示词。

## 文档同步规则

- **修改代码时**，必须同步更新 `CLAUDE.md`，确保架构说明、命令、配置等与代码一致。
- **修改配置结构时**，必须同步更新 `config.yaml.example`；真实 `config.yaml` 不得提交。
- **修改代码或配置后**，检查 `README.md` 是否需要同步更新（如新增/删除接口、启动方式变化等）。
- **README.md 必须使用中文**书写。
