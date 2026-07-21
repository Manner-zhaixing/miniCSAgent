import sys
from pathlib import Path

import uvicorn

from mini_cs_agent.main import create_app

if __name__ == "__main__":
    env_path = Path(__file__).resolve().parent / ".env"
    print(f"[mini-cs-agent] Loading config from: {env_path}")
    print(f"[mini-cs-agent] .env exists: {env_path.exists()}")

    try:
        app = create_app()
    except FileNotFoundError as e:
        print(f"[mini-cs-agent] ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"[mini-cs-agent] ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print("[mini-cs-agent] Starting server on http://127.0.0.1:8000")
    print("[mini-cs-agent] API docs: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)
