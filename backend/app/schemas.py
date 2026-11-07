from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class SessionCreate(Input):
    title: str = Field(default="New research", min_length=1, max_length=160)


class MessageCreate(Input):
    content: str = Field(min_length=1, max_length=8000)
    client_message_id: UUID


class SessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: UUID
    title: str
    created_at: datetime
    updated_at: datetime


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    session_id: UUID
    client_message_id: UUID
    role: Literal["user", "assistant"]
    content: str
    status: Literal["completed", "failed", "cancelled"]
    created_at: datetime
    run: dict | None = None
    citations: list[dict] = []


class UserOut(BaseModel):
    id: UUID
    display_name: str
    metadata: dict
    created_at: datetime


class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: str
    retryable: bool


class ErrorOut(BaseModel):
    error: ErrorDetail


class LiveOut(BaseModel):
    status: Literal["alive"]


class DatabaseCheck(BaseModel):
    ready: bool
    schema_revision: str | None = None
    pgvector_version: str | None = None
    code: str | None = None


class CorpusCheck(BaseModel):
    ready: bool
    status: Literal["empty", "partial", "available", "unknown"]
    active_chunks: int | None = None
    active_episodes: int | None = None
    discovered: int | None = None


class AgentCheck(BaseModel):
    ready: bool
    version: str | None = None
    code: str | None = None


class OllamaCheck(BaseModel):
    ready: bool
    reachable_from_api: bool
    version: str | None = None
    generation_model_available: bool | None = None
    essay_model_available: bool | None = None
    embedding_model_available: bool | None = None
    embedding_dimensions_compatible: bool | None = None
    index_identity_compatible: bool | None = None
    note: str | None = None
    code: str | None = None


class ReadyChecks(BaseModel):
    database: DatabaseCheck
    corpus: CorpusCheck
    agent: AgentCheck
    ollama: OllamaCheck


class ReadyOut(BaseModel):
    status: Literal["ready", "not_ready"]
    scope: Literal["phase_5_conversation"]
    product_ready: bool
    checks: ReadyChecks


class ProviderOption(BaseModel):
    id: str
    implemented: bool
    configured: bool | None = None
    scope: str | None = None
    credentials_present: bool | None = None
    enabled: bool | None = None
    reason: str | None = None


class ProvidersOut(BaseModel):
    essay_model: str
    selected: Literal["ollama"]
    model: str
    automatic_fallback: Literal[False]
    providers: list[ProviderOption]


class IngestionRunOut(BaseModel):
    id: UUID
    corpus_revision: str
    status: str
    discovered: int
    selected: int
    loaded: int
    skipped: int
    failed: int
    deleted: int
    embedding_model: str
    embedding_digest: str | None = None
    source_kind: str
    created_at: datetime
    completed_at: datetime | None = None
    heartbeat_at: datetime
    last_error_code: str | None = None


class IngestionStatusOut(BaseModel):
    active_episodes: int
    active_chunks: int
    latest: IngestionRunOut | None
    pending_items: int
    recent_errors: list[dict[str, str]]


class AnswerCreate(Input):
    content: str = Field(min_length=1,max_length=1000)
    client_message_id: UUID
    retrieval_mode: Literal['hybrid'] = 'hybrid'
    source_path: str | None = Field(default=None,pattern=r'^episodes/[a-z0-9-]+/transcript\.md$',max_length=240)
    retry: bool = False
    timeout_seconds: float = Field(default=75,ge=.1,le=90)


class AnswerRunOut(BaseModel):
    id: UUID
    session_id: UUID
    user_message_id: UUID
    assistant_message_id: UUID | None
    status: Literal['running','completed','failed','cancelled']
    attempt: int
    retrieval_mode: Literal['hybrid']
    resolved_query: str
    context_message_ids: list[str]
    error_code: str | None
    started_at: datetime
    completed_at: datetime | None
    metadata: dict
    output: dict | None


class SourceOut(BaseModel):
    source_label: str
    chunk_id: UUID
    original_text: str
    metadata: dict
    quote_spans: list[dict]
    source_url: str | None
    video_url: str | None


class ChatEvent(BaseModel):
    type: Literal['started','retrieving','evidence_ready','generating','completed','failed','cancelled']
    run_id: UUID
    retrieval_mode: Literal['hybrid'] = 'hybrid'
    data: dict = {}
