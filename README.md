# Mini CS Agent

一个基于 LangGraph + FastAPI 的极简 AI Agent 示例，由 DeepSeek 驱动。

## 项目结构

```text
src/mini_cs_agent/
├── main.py          # FastAPI 应用工厂
├── api/
│   ├── routes.py    # POST /api/v1/chat, GET /api/v1/health
│   └── schemas.py   # ChatRequest, ChatResponse
└── core/
    ├── agent.py     # LangGraph Agent (StateGraph)
    └── config.py    # 读取 .env 配置
```

## 快速开始

### 前置条件

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)
- DeepSeek API Key

### 安装

```bash
# 1. 安装依赖
uv sync

# 2. 配置 API Key
cp .env.example .env
# 编辑 .env，填入你的 DEEPSEEK_API_KEY

# 3. 启动服务
uv run uvicorn mini_cs_agent.main:create_app --factory --reload --port 8000
```

### 使用

```bash
# 健康检查
curl http://localhost:8000/api/v1/health

# 发送消息
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好，最近怎么样？"}'
```

### API 文档

启动服务后访问：

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>
