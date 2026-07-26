# Mini CS Agent

一个基于 LangChain ReAct Agent + FastAPI 的 AI Agent 项目，由 DeepSeek 驱动，集成 Exa AI 联网搜索，支持 SSE 流式输出。

## 项目结构

```text
src/mini_cs_agent/
├── main.py              # FastAPI 应用工厂
├── api/
│   ├── routes.py         # POST /api/v1/chat (SSE 流式), GET /api/v1/health
│   └── schemas.py        # ChatRequest, ChatResponse
└── core/
    ├── agent.py           # LangChain create_agent ReAct Agent
    ├── config.py          # 读取 .env 配置
    ├── prompts/
    │   └── agent_system.py    # 系统提示词
    └── tools/
        ├── __init__.py    # 工具注册 (ALL_TOOLS)
        └── web_search.py  # Exa AI 搜索工具
```

## 快速开始

### 前置条件

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)
- DeepSeek API Key
- Exa AI API Key（联网搜索需要，可选）

### 安装

```bash
# 1. 安装依赖
uv sync

# 2. 配置 API Key
cp .env.example .env
# 编辑 .env，填入你的 DEEPSEEK_API_KEY 和 EXA_API_KEY

# 3. 启动服务
uv run uvicorn mini_cs_agent.main:create_app --factory --reload --port 8000
```

### 配置说明

`.env` 文件中的字段：

| 字段 | 必填 | 说明 |
|------|------|------|
| `DEEPSEEK_API_KEY` | 是 | DeepSeek API 密钥 |
| `DEEPSEEK_BASE_URL` | 否 | API 地址，默认 `https://api.deepseek.com` |
| `MODEL_NAME` | 否 | 模型名称，默认 `deepseek-chat` |
| `EXA_API_KEY` | 否 | Exa 搜索 API 密钥（不填则搜索功能不可用） |

Exa API Key 获取：<https://dashboard.exa.ai>（每月 1,000 次免费请求）

### 使用

```bash
# 健康检查
curl http://localhost:8000/api/v1/health

# 非流式聊天（返回 JSON）
curl -X POST 'http://localhost:8000/api/v1/chat?stream=false' \
  -H "Content-Type: application/json" \
  -d '{"message": "你好，介绍一下你自己"}'

# 流式聊天（SSE，默认模式）
curl -N -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "搜索今天最新的 AI 新闻"}'
```

### SSE 流式响应格式

```text
event: token
data: {"token": "今天"}

event: token
data: {"token": "的"}

...

event: message
data: {"done": true}
```

### API 文档

启动服务后访问：

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>
