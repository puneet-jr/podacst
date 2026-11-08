import os
from pathlib import Path
from urllib.parse import urlsplit
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator
from sqlalchemy import URL


class Settings(BaseModel):
    model_config = ConfigDict(hide_input_in_errors=True)
    db_host: str = "db"
    db_port: int = Field(default=5432, ge=1, le=65535)
    db_name: str = "lenny"
    db_user: str = "lenny"
    db_password: SecretStr
    ollama_url: str = "http://host.docker.internal:11434"
    generation_model: str = "qwen3:0.6b"
    essay_model: str = "qwen3:1.7b"
    embedding_model: str = "nomic-embed-text:latest"
    embedding_dimensions: int = 768
    local_user_id: UUID = UUID("00000000-0000-4000-8000-000000000001")
    pi_path: str = "/app/agent/node_modules/.bin/pi"
    default_provider: str = "ollama"
    anthropic_api_key: SecretStr = SecretStr("")

    openrouter_api_key: SecretStr = SecretStr("")
    openrouter_model: str = "google/gemini-2.5-flash-lite"
    private_rpc_traces: bool = False
    cloud_model: str = "claude-haiku-4-5-20251001"

    @field_validator("ollama_url")
    @classmethod
    def local_url(cls, value):
        parsed = urlsplit(value)
        if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "host.docker.internal"} or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in ("", "/"):
            raise ValueError("Use an approved local Ollama HTTP endpoint")
        return value.rstrip("/")

    @field_validator("default_provider")
    @classmethod
    def supported_provider(cls, value):
        if value not in {"ollama", "anthropic", "openrouter"}:
            raise ValueError("Select ollama, anthropic or openrouter explicitly")
        return value

    @field_validator('generation_model','essay_model','cloud_model','openrouter_model','embedding_model')
    @classmethod
    def bounded_model(cls,value):
        if not __import__('re').fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:/-]{0,119}',value):
            raise ValueError('Use a bounded model identifier')
        return value

    @property
    def provider_id(self):return {'ollama':'ollama-local','anthropic':'anthropic-cloud','openrouter':'openrouter'}[self.default_provider]

    @property
    def model_base_url(self):return {'ollama':self.ollama_url+'/v1','anthropic':'https://api.anthropic.com','openrouter':'https://openrouter.ai/api/v1'}[self.default_provider]

    @property
    def provider_api(self):return 'anthropic-messages' if self.default_provider=='anthropic' else 'openai-completions'

    @property
    def selected_key(self):return self.openrouter_api_key if self.default_provider=='openrouter' else self.anthropic_api_key if self.default_provider=='anthropic' else SecretStr('')

    def selected_model(self,essay=False):
        return self.openrouter_model if self.default_provider=='openrouter' else self.cloud_model if self.default_provider=='anthropic' else self.essay_model if essay else self.generation_model

    def require_provider(self):
        if self.default_provider!='ollama' and not self.selected_key.get_secret_value().strip():
            raise ValueError('cloud_key_missing')

    @property
    def database_url(self):
        return URL.create("postgresql+psycopg", username=self.db_user, password=self.db_password.get_secret_value(), host=self.db_host, port=self.db_port, database=self.db_name)


def load_settings():
    mapping = {"db_host": "DB_HOST", "db_port": "DB_PORT", "db_name": "POSTGRES_DB", "db_user": "POSTGRES_USER", "db_password": "POSTGRES_PASSWORD", "ollama_url": "OLLAMA_URL", "generation_model": "GENERATION_MODEL", "essay_model": "ESSAY_MODEL", "embedding_model": "EMBEDDING_MODEL", "pi_path": "PI_PATH", "default_provider": "DEFAULT_PROVIDER", "anthropic_api_key": "ANTHROPIC_API_KEY", "cloud_model": "CLOUD_MODEL", "private_rpc_traces": "PRIVATE_RPC_TRACES", "openrouter_api_key": "OPENROUTER_API_KEY", "openrouter_model": "OPENROUTER_MODEL"}
    return Settings(**{key: os.environ[name] for key, name in mapping.items() if name in os.environ})
