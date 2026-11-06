import os
from pathlib import Path
from urllib.parse import urlsplit
from uuid import UUID

from pydantic import BaseModel, Field, SecretStr, field_validator
from sqlalchemy import URL


class Settings(BaseModel):
    db_host: str = "db"
    db_port: int = Field(default=5432, ge=1, le=65535)
    db_name: str = "lenny"
    db_user: str = "lenny"
    db_password: SecretStr
    ollama_url: str = "http://host.docker.internal:11434"
    generation_model: str = "qwen3:0.6b"
    embedding_model: str = "nomic-embed-text:latest"
    embedding_dimensions: int = 768
    local_user_id: UUID = UUID("00000000-0000-4000-8000-000000000001")
    pi_path: str = "/app/agent/node_modules/.bin/pi"
    default_provider: str = "ollama"
    anthropic_api_key: SecretStr = SecretStr("")

    @field_validator("ollama_url")
    @classmethod
    def local_url(cls, value):
        parsed = urlsplit(value)
        if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "host.docker.internal"} or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in ("", "/"):
            raise ValueError("Use an approved local Ollama HTTP endpoint")
        return value.rstrip("/")

    @field_validator("default_provider")
    @classmethod
    def local_only(cls, value):
        if value != "ollama":
            raise ValueError("Only Ollama is implemented in Phase 2")
        return value

    @property
    def database_url(self):
        return URL.create("postgresql+psycopg", username=self.db_user, password=self.db_password.get_secret_value(), host=self.db_host, port=self.db_port, database=self.db_name)


def load_settings():
    mapping = {"db_host": "DB_HOST", "db_port": "DB_PORT", "db_name": "POSTGRES_DB", "db_user": "POSTGRES_USER", "db_password": "POSTGRES_PASSWORD", "ollama_url": "OLLAMA_URL", "generation_model": "GENERATION_MODEL", "embedding_model": "EMBEDDING_MODEL", "pi_path": "PI_PATH", "default_provider": "DEFAULT_PROVIDER", "anthropic_api_key": "ANTHROPIC_API_KEY"}
    return Settings(**{key: os.environ[name] for key, name in mapping.items() if name in os.environ})
