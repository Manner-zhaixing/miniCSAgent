# Mini CS Agent

一个基于 LangChain ReAct Agent + FastAPI 的多模型 AI Agent 项目，集成 Exa AI 联网搜索，支持 SSE 流式输出。

## 支持的模型接入

| 配置中的 `provider` | LangChain 集成 | 适用服务 |
|---|---|---|
| `deepseek` | `ChatDeepSeek` | DeepSeek |
| `openai` | `ChatOpenAI` | OpenAI 及千问、Kimi、GLM 等 OpenAI-compatible 服务 |
| `anthropic` | `ChatAnthropic` | Claude |

模型由 `config.yaml` 中的 `active_model` 选择，Agent、工具和 API 不需要随模型切换而修改。

## 项目结构

```text
src/mini_cs_agent/
├── main.py                  # FastAPI 应用工厂
├── api/
│   ├── routes.py           # 聊天与健康检查接口
│   └── schemas.py          # 请求和响应模型
└── core/
    ├── agent.py            # 与模型服务无关的 LangChain Agent
    ├── config.py           # 读取并校验 config.yaml
    ├── model_factory.py    # 根据配置创建 LangChain 模型
    ├── prompts/
    │   └── agent_system.py
    └── tools/
        ├── __init__.py
        ├── time.py
        └── web_search.py
```

## 本地运行

### 前置条件

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)
- 至少一个模型服务的 API Key
- Exa API Key（仅在启用联网搜索时需要）

### 安装与配置

```bash
uv sync
cp config.yaml.example config.yaml
```

编辑 `config.yaml`：

1. 在 `active_model` 中选择模型配置名称。
2. 为该模型填写 `api_key`、`model` 和正确的 `base_url`。
3. 如需联网搜索，将 `web_search.enabled` 改为 `true` 并填写 Exa API Key。

`config.yaml` 已被 Git 和 Docker 构建上下文忽略，不会提交或打进镜像；`config.yaml.example` 只包含模板，可以提交。

### 启动

```bash
uv run uvicorn mini_cs_agent.main:create_app --factory --reload --host 0.0.0.0 --port 8000
```

也可以使用便捷入口，它会读取 `config.yaml` 中的 `server` 配置：

```bash
uv run python main.py
```

启动后打开 <http://127.0.0.1:8000/>。

## Docker 运行

构建镜像：

```bash
docker build -t mini-cs-agent:local .
```

启动时将本地配置只读挂载到容器：

```bash
docker run --rm \
  --name mini-cs-agent \
  -p 8000:8000 \
  -v "$(pwd)/config.yaml:/app/config.yaml:ro" \
  mini-cs-agent:local
```

修改 `config.yaml` 后重启容器即可生效。不要把真实配置复制进 Dockerfile。

## 配置说明

模型配置示例：

```yaml
active_model: deepseek

models:
  deepseek:
    provider: deepseek
    model: deepseek-v4-pro
    api_key: "填写 API Key"
    base_url: https://api.deepseek.com
    streaming: true
    options:
      extra_body:
        thinking:
          type: enabled
```

`options` 会传给对应的 LangChain 模型类，可用于配置 `temperature`、`max_tokens`、`extra_body` 等模型专属参数。不能在 `options` 中覆盖 `model`、`api_key`、`base_url` 或 `streaming`。

切换模型只需修改：

```yaml
active_model: qwen
```

未被选中的模型允许暂时不填写 API Key；启动时只强制校验当前模型。API Key 使用 Pydantic `SecretStr` 保存，配置对象被日志输出时不会显示明文。

## API 使用

```bash
# 健康检查
curl http://127.0.0.1:8000/api/v1/health

# 非流式聊天
curl -X POST 'http://127.0.0.1:8000/api/v1/chat?stream=false' \
  -H "Content-Type: application/json" \
  -d '{"message": "你好，介绍一下你自己"}'

# SSE 流式聊天
curl -N -X POST http://127.0.0.1:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "搜索今天最新的 AI 新闻"}'
```

API 文档：

- Swagger UI：<http://127.0.0.1:8000/docs>
- ReDoc：<http://127.0.0.1:8000/redoc>

## 配置安全检查

```bash
git check-ignore -v config.yaml
git ls-files config.yaml
chmod 600 config.yaml
```

第二个命令应当没有输出。如果真实密钥曾经提交到 Git，应立即撤销并重新生成密钥。
