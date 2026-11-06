import json
from alembic import command
from alembic.config import Config
from backend.app.schema import CURRENT_REVISION


def main():
    try:
        command.upgrade(Config("backend/alembic.ini"), "head")
    except Exception as exc:
        print(json.dumps({"event": "migration_failed", "code": "migration_failed", "error_type": type(exc).__name__}), flush=True)
        raise SystemExit(1)
    print(json.dumps({"event": "migration_completed", "revision": CURRENT_REVISION}), flush=True)


if __name__ == "__main__":
    main()
