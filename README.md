# Mini CS Agent

A minimal LangGraph + FastAPI agent demo powered by DeepSeek.

## Project Structure

```
src/mini_cs_agent/
├── main.py          # FastAPI app factory
├── api/
│   ├── routes.py    # POST /api/v1/chat, GET /api/v1/health
│   └── schemas.py   # ChatRequest, ChatResponse
└── core/
    ├── agent.py     # LangGraph agent (StateGraph)
    └── config.py    # Read .env config
```

## Quick Start

### Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)
- DeepSeek API key

### Setup

```bash
# 1. Install dependencies
uv sync

# 2. Configure your API key
cp .env.example .env
# Edit .env and fill in your DEEPSEEK_API_KEY

# 3. Start the server
uv run uvicorn mini_cs_agent.main:create_app --factory --reload --port 8000
```

### Usage

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Send a message
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'
```

### API Docs

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
