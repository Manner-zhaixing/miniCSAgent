import sys
from pathlib import Path

import uvicorn

from mini_cs_agent.main import create_app

if __name__ == "__main__":
    config_path = Path(__file__).resolve().parent / "config.yaml"
    print(f"[mini-cs-agent] Loading config from: {config_path}")
    print(f"[mini-cs-agent] config.yaml exists: {config_path.exists()}")

    try:
        app = create_app()
    except FileNotFoundError as e:
        print(f"[mini-cs-agent] ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"[mini-cs-agent] ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    config = app.state.config
    host = config.server.host
    port = config.server.port
    display_host = "127.0.0.1" if host == "0.0.0.0" else host
    print(f"[mini-cs-agent] Active model: {config.active_model}")
    print(f"[mini-cs-agent] Starting server on http://{display_host}:{port}")
    print(f"[mini-cs-agent] API docs: http://{display_host}:{port}/docs")
    uvicorn.run(app, host=host, port=port)
