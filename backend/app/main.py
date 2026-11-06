import json
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import logging
from pathlib import Path
import subprocess
import tempfile
import time
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse
import httpx
from sqlalchemy import func, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from starlette.exceptions import HTTPException

from backend.app.config import load_settings
from backend.app.schema import CURRENT_REVISION
from backend.app.db import ChatSession, Message, User, make_engine
from backend.app.embedding import EmbeddingError
from backend.app.retrieval import RetrievalError, SearchRequest, SearchResult, search
from backend.app.conversation import ConversationError, ConversationService, prepare, load_run, source_links, json_value
from backend.app.essays import EssayService,prepare_essay,load_essay,read_essay_sources,review_essay
from backend.app.writing import EssayCreate,EssayRunOut,EssayReview,EssayError,EssayEvent
from backend.app.schemas import AnswerCreate, AnswerRunOut, SourceOut, ChatEvent
from backend.app.schemas import ErrorOut, LiveOut, ReadyOut, ProvidersOut, IngestionStatusOut, MessageCreate, MessageOut, SessionCreate, SessionOut, UserOut

settings = load_settings()
engine = make_engine(settings)
factory = sessionmaker(engine, expire_on_commit=False)
conversations = ConversationService(engine,settings)
essays = EssayService(engine,settings,conversations.lock)
@asynccontextmanager
async def lifespan(app):
    with engine.begin() as connection:
        connection.execute(text("UPDATE answer_runs SET status='failed',error_code='app_restarted',completed_at=now() WHERE status='running'"))
        connection.execute(text("UPDATE essay_runs SET status='failed',error_code='app_restarted',completed_at=now() WHERE status='running'"))
    yield
    await conversations.shutdown()
    await essays.shutdown()
    engine.dispose()


app = FastAPI(lifespan=lifespan, title="The Lenny Growth Assistant", version="0.2.0", responses={422: {"model": ErrorOut}, 404: {"model": ErrorOut}, 503: {"model": ErrorOut}})
logger = logging.getLogger("lenny")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(handler)
logger.propagate = False


def event(name, **fields):
    # Only explicitly chosen metadata is logged. Never prompts, content, keys, DSNs or exception text.
    logger.info(json.dumps({"timestamp": datetime.now(timezone.utc).isoformat(), "phase": "api", "event": name, **fields}, default=str))


class AppError(Exception):
    def __init__(self, code, message, status=400, retryable=False):
        self.code, self.message, self.status, self.retryable = code, message, status, retryable


def failure(request, code, message, status, retryable=False):
    return JSONResponse({"error": {"code": code, "message": message, "request_id": request.state.request_id, "retryable": retryable}}, status_code=status)


@app.middleware("http")
async def correlation(request: Request, call_next):
    request.state.request_id = uuid4().hex
    started = time.monotonic()
    try:
        response = await call_next(request)
    except Exception:
        response = failure(request, "internal_error", "The request could not be completed.", 500)
    response.headers["X-Request-ID"] = request.state.request_id
    route = request.scope.get("route")
    try:
        session_id = str(UUID(str(request.path_params.get("session_id"))))
    except ValueError:
        session_id = None
    event("http_request", request_id=request.state.request_id, session_id=session_id, method=request.method,
          route=getattr(route, "path", "unmatched"), duration_ms=round((time.monotonic() - started) * 1000, 2), status=response.status_code)
    return response


@app.exception_handler(AppError)
async def app_error(request: Request, exc):
    return failure(request, exc.code, exc.message, exc.status, exc.retryable)


@app.exception_handler(ConversationError)
async def conversation_error(request: Request, exc):
    return failure(request,exc.code,'The conversation operation could not complete. Check its saved status and retry.',exc.status,exc.status>=500)


@app.exception_handler(EssayError)
async def essay_error(request:Request,exc):
    return failure(request,exc.code,'The essay operation could not complete. Its saved draft and validation remain available.',exc.status,exc.status>=500)


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc):
    return failure(request, "validation_error", "Check the request fields, identifiers and limits.", 422)


@app.exception_handler(HTTPException)
async def http_error(request: Request, exc):
    return failure(request, "not_found" if exc.status_code == 404 else "http_error", "Resource not found." if exc.status_code == 404 else "Request not allowed.", exc.status_code)


@app.exception_handler(SQLAlchemyError)
async def database_error(request: Request, exc):
    event("database_failure", request_id=request.state.request_id, code="database_unavailable", error_type=type(exc).__name__)
    return failure(request, "database_unavailable", "The database is unavailable. Please retry.", 503, True)


def db():
    with factory() as connection:
        yield connection


def owned_session(connection, session_id, lock=False):
    query = select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == settings.local_user_id)
    if lock:
        query = query.with_for_update()
    result = connection.scalar(query)
    if result is None:
        raise AppError("session_not_found", "Session not found.", 404)
    return result


@app.get("/api/health/live", response_model=LiveOut)
def live():
    return {"status": "alive"}


@app.get("/api/health/ready", response_model=ReadyOut, response_model_exclude_none=True, responses={503: {"model": ReadyOut}})
def ready(request: Request):
    checks = {}
    index_profile = None
    try:
        with engine.connect() as connection:
            revision = connection.scalar(text("SELECT version_num FROM alembic_version"))
            extension = connection.scalar(text("SELECT extversion FROM pg_extension WHERE extname='vector'"))
            count = connection.scalar(text("SELECT count(*) FROM chunks WHERE active"))
            episodes = connection.scalar(text("SELECT count(*) FROM episodes WHERE deleted_at IS NULL AND current_version IS NOT NULL"))
            discovered = connection.scalar(text("SELECT discovered FROM ingestion_runs ORDER BY created_at DESC LIMIT 1")) or 0
            index_profile = connection.execute(text("SELECT * FROM knowledge_config WHERE singleton")).mappings().first()
        checks["database"] = {"ready": revision == CURRENT_REVISION and bool(extension), "schema_revision": revision, "pgvector_version": extension}
        checks["corpus"] = {"ready": count > 0, "active_chunks": count, "active_episodes": episodes, "discovered": discovered,
                            "status": "empty" if not count else "partial" if episodes < discovered else "available"}
    except SQLAlchemyError:
        checks["database"] = {"ready": False, "code": "database_unavailable"}
        checks["corpus"] = {"ready": False, "status": "unknown"}
    try:
        with tempfile.TemporaryDirectory(prefix="lenny-pi-check-") as config:
            from backend.app.agent import local_environment
            result = subprocess.run([settings.pi_path, "--version"], env=local_environment(config), capture_output=True, text=True, timeout=3)
        checks["agent"] = {"ready": result.returncode == 0 and result.stdout.strip() == "1.5.0", "version": result.stdout.strip() if result.returncode == 0 else None}
    except (OSError, subprocess.TimeoutExpired):
        checks["agent"] = {"ready": False, "code": "agent_unavailable"}
    try:
        with httpx.Client(timeout=2, trust_env=False) as client:
            response = client.get(settings.ollama_url + "/api/version"); response.raise_for_status()
            version = response.json()["version"]
            response = client.get(settings.ollama_url + "/api/tags"); response.raise_for_status()
            models = {m["name"]: m for m in response.json()["models"]}
            generation = models.get(settings.generation_model)
            embedding = models.get(settings.embedding_model)
            compatible = False
            if embedding:
                response = client.post(settings.ollama_url + "/api/show", json={"model": settings.embedding_model}); response.raise_for_status()
                info = response.json().get("model_info", {})
                dimension = next((value for key, value in info.items() if key.endswith(".embedding_length")), None)
                compatible = dimension == settings.embedding_dimensions
        identity_compatible = not index_profile or bool(embedding and index_profile['embedding_model'] == settings.embedding_model and index_profile['embedding_digest'] == embedding['digest'])
        checks["ollama"] = {"ready": bool(generation and embedding and compatible and identity_compatible), "reachable_from_api": True, "version": version,
                            "generation_model_available": bool(generation), "embedding_model_available": bool(embedding), "embedding_dimensions_compatible": compatible,
                            "index_identity_compatible": identity_compatible,
                            "note": "Transport and installed-model availability; does not prove answer or essay quality."}
    except (httpx.HTTPError, ValueError, KeyError, TypeError):
        checks["ollama"] = {"ready": False, "reachable_from_api": False, "code": "ollama_unavailable"}
    foundation = all(checks[k]["ready"] for k in ("database", "agent", "ollama"))
    event("readiness", request_id=request.state.request_id, outcome="ready" if foundation else "not_ready", database_ready=checks["database"]["ready"], agent_ready=checks["agent"]["ready"], model_ready=checks["ollama"]["ready"])
    payload = ReadyOut.model_validate({"status": "ready" if foundation else "not_ready", "scope": "phase_5_conversation", "product_ready": False, "checks": checks})
    return JSONResponse(payload.model_dump(mode="json", exclude_none=True), status_code=200 if foundation else 503)


@app.get("/api/providers", response_model=ProvidersOut, response_model_exclude_none=True)
def providers():
    return {"selected": "ollama", "model": settings.generation_model, "automatic_fallback": False,
            "providers": [{"id": "ollama", "implemented": True, "configured": True, "scope": "retrieval-first extractive conversation; hybrid; no autonomous/essay quality claim"},
                          {"id": "anthropic", "implemented": False, "credentials_present": bool(settings.anthropic_api_key.get_secret_value()), "enabled": False, "reason": "Cloud adapter is pending Phase 9; no implicit cloud inference."}]}


@app.get("/api/ingestion/status", response_model=IngestionStatusOut)
def ingestion_status(connection: Session = Depends(db)):
    latest = connection.execute(text('SELECT * FROM ingestion_runs ORDER BY created_at DESC LIMIT 1')).mappings().first()
    pending, errors = 0, []
    if latest:
        pending = connection.scalar(text("SELECT count(*) FROM ingestion_items WHERE run_id=:id AND status='pending'"), {'id':latest['id']})
        errors = [dict(row) for row in connection.execute(text("SELECT source_path,error_code FROM ingestion_items WHERE run_id=:id AND status='failed' ORDER BY source_path LIMIT 10"), {'id':latest['id']}).mappings()]
    return {'active_episodes':connection.scalar(text('SELECT count(*) FROM episodes WHERE deleted_at IS NULL AND current_version IS NOT NULL')),
            'active_chunks':connection.scalar(text('SELECT count(*) FROM chunks WHERE active')), 'latest':latest, 'pending_items':pending, 'recent_errors':errors}


@app.get("/api/me", response_model=UserOut)
def me(connection: Session = Depends(db)):
    user = connection.get(User, settings.local_user_id)
    if user is None:
        raise AppError("local_user_missing", "Local user setup is incomplete.", 503)
    return UserOut(id=user.id, display_name=user.display_name, metadata=user.user_metadata, created_at=user.created_at)


@app.post('/api/retrieval/search', response_model=SearchResult)
def retrieve(body: SearchRequest, request: Request):
    try:
        result = search(engine,settings,body)
    except (RetrievalError, EmbeddingError) as exc:
        event('retrieval_failure',request_id=request.state.request_id,code=str(exc),mode=body.mode)
        raise AppError(str(exc),'Local evidence search could not complete. Check the index and local model, then retry.',503,True) from exc
    event('retrieval_completed',request_id=request.state.request_id,mode=body.mode,status=result.status,
          passage_count=len(result.passages),estimated_tokens=result.estimated_tokens,duration_ms=round(result.timings_ms['total'],2))
    return result


@app.post("/api/sessions", response_model=SessionOut, status_code=201)
def create_session(body: SessionCreate, request: Request, connection: Session = Depends(db)):
    with connection.begin():
        item = ChatSession(user_id=settings.local_user_id, title=body.title)
        connection.add(item); connection.flush(); connection.refresh(item)
        result = SessionOut.model_validate(item)
    event("session_created", request_id=request.state.request_id, session_id=result.id)
    return result


@app.get("/api/sessions", response_model=list[SessionOut])
def list_sessions(limit: int = Query(default=25, ge=1, le=100), offset: int = Query(default=0, ge=0, le=100000), connection: Session = Depends(db)):
    return list(connection.scalars(select(ChatSession).where(ChatSession.user_id == settings.local_user_id).order_by(ChatSession.updated_at.desc(), ChatSession.id).limit(limit).offset(offset)))


@app.get("/api/sessions/{session_id}", response_model=SessionOut)
def read_session(session_id: UUID, connection: Session = Depends(db)):
    return owned_session(connection, session_id)


@app.get("/api/sessions/{session_id}/messages", response_model=list[MessageOut])
def read_messages(session_id: UUID, limit: int = Query(default=50, ge=1, le=200), offset: int = Query(default=0, ge=0, le=100000), connection: Session = Depends(db)):
    owned_session(connection, session_id)
    messages=list(connection.scalars(select(Message).where(Message.session_id == session_id).order_by(Message.created_at, Message.id).limit(limit).offset(offset)))
    runs=list(connection.execute(text('SELECT id,user_message_id,assistant_message_id,status,error_code,retrieval_mode,attempt,output FROM answer_runs WHERE session_id=:id ORDER BY started_at DESC LIMIT 200'),{'id':session_id}).mappings())
    result=[]
    for message in messages:
        item=MessageOut.model_validate(message)
        run=next((r for r in runs if message.id in (r['user_message_id'],r['assistant_message_id'])),None)
        if run:
            item.run={k:run[k] for k in ('id','status','error_code','retrieval_mode','attempt','output')}
        if message.role=='assistant':item.citations=[dict(r) for r in connection.execute(text('SELECT source_label,chunk_id FROM answer_sources WHERE message_id=:id ORDER BY source_label'),{'id':message.id}).mappings()]
        result.append(item)
    return result


@app.post('/api/sessions/{session_id}/answers',responses={200:{'content':{'application/x-ndjson':{}},'description':'Typed ChatEvent JSON lines; completed output only after evidence-ID validation'}})
async def answer(session_id: UUID, body: AnswerCreate, request: Request):
    run,created=await asyncio.to_thread(prepare,engine,settings,session_id,body)
    if not created:
        async def replay():yield json_value(ChatEvent(type=run['status'],run_id=run['id'],data={'run':run}).model_dump(mode='json'))+'\n'
        return StreamingResponse(replay(),media_type='application/x-ndjson',headers={'Cache-Control':'no-store','X-Accel-Buffering':'no'})
    return StreamingResponse(conversations.events(run,request),media_type='application/x-ndjson',headers={'Cache-Control':'no-store','X-Accel-Buffering':'no'})


@app.get('/api/sessions/{session_id}/runs/{run_id}',response_model=AnswerRunOut)
def read_answer_run(session_id: UUID,run_id: UUID):return load_run(engine,settings,session_id,run_id)


@app.post('/api/sessions/{session_id}/runs/{run_id}/cancel')
async def cancel_answer(session_id: UUID,run_id: UUID):
    run=await asyncio.to_thread(load_run,engine,settings,session_id,run_id)
    task=conversations.tasks.get(run_id)
    if run['status']=='running' and task:task.cancel();return {'status':'cancellation_requested','run_id':run_id}
    return {'status':run['status'],'run_id':run_id}


@app.get('/api/sessions/{session_id}/messages/{message_id}/sources/{label}',response_model=SourceOut)
def read_source(session_id: UUID,message_id: UUID,label: str,connection: Session=Depends(db)):
    owned_session(connection,session_id)
    if not __import__('re').fullmatch(r'S[1-8]',label):raise AppError('source_not_found','Source not found.',404)
    row=connection.execute(text('''SELECT a.* FROM answer_sources a JOIN messages m ON m.id=a.message_id
     WHERE a.message_id=:message AND m.session_id=:session AND m.role='assistant' AND a.source_label=:label'''),{'message':message_id,'session':session_id,'label':label}).mappings().first()
    if not row:raise AppError('source_not_found','Source not found.',404)
    source,video=source_links(row['source_metadata'])
    return {'source_label':row['source_label'],'chunk_id':row['chunk_id'],'original_text':row['evidence_text'],'metadata':row['source_metadata'],'quote_spans':row['quote_spans'],'source_url':source,'video_url':video}


@app.post("/api/sessions/{session_id}/messages", response_model=MessageOut, status_code=201, responses={409: {"model": ErrorOut}})
def save_message(session_id: UUID, body: MessageCreate, request: Request, connection: Session = Depends(db)):
    with connection.begin():
        chat = owned_session(connection, session_id, lock=True)
        existing = connection.scalar(select(Message).where(Message.session_id == session_id, Message.client_message_id == body.client_message_id))
        if existing:
            if existing.content != body.content:
                raise AppError("idempotency_conflict", "This message identifier has already been used.", 409)
            return MessageOut.model_validate(existing)
        item = Message(session_id=session_id, client_message_id=body.client_message_id, role="user", content=body.content, status="completed")
        connection.add(item); chat.updated_at = func.now()
        connection.flush(); connection.refresh(item)
        result = MessageOut.model_validate(item)
    event("message_saved", request_id=request.state.request_id, session_id=session_id, message_id=result.id)
    return result


@app.post('/api/sessions/{session_id}/essays',responses={200:{'content':{'application/x-ndjson':{}},'description':'Dedicated Ship30 workflow; deterministic checks then explicit manual review, not automatic semantic certification.'}})
async def write_essay(session_id:UUID,body:EssayCreate,request:Request):
    run,created=await asyncio.to_thread(prepare_essay,engine,settings,session_id,body)
    if not created:
        async def replay():yield json_value(EssayEvent(type=run['status'],run_id=run['id'],data={'run':run}).model_dump(mode='json'))+'\n'
        return StreamingResponse(replay(),media_type='application/x-ndjson',headers={'Cache-Control':'no-store','X-Accel-Buffering':'no'})
    return StreamingResponse(essays.events(run,request),media_type='application/x-ndjson',headers={'Cache-Control':'no-store','X-Accel-Buffering':'no'})


@app.get('/api/sessions/{session_id}/essays/{run_id}',response_model=EssayRunOut)
def read_essay(session_id:UUID,run_id:UUID):return load_essay(engine,settings,session_id,run_id)


@app.get('/api/sessions/{session_id}/essays/{run_id}/sources',response_model=list[SourceOut])
def essay_sources(session_id:UUID,run_id:UUID):return read_essay_sources(engine,settings,session_id,run_id)


@app.post('/api/sessions/{session_id}/essays/{run_id}/review',response_model=EssayRunOut)
def submit_essay_review(session_id:UUID,run_id:UUID,body:EssayReview):return review_essay(engine,settings,session_id,run_id,body)


@app.post('/api/sessions/{session_id}/essays/{run_id}/cancel')
async def cancel_essay(session_id:UUID,run_id:UUID):
    run=await asyncio.to_thread(load_essay,engine,settings,session_id,run_id)
    task=essays.tasks.get(run_id)
    if run['status']=='running' and task:task.cancel();return {'status':'cancellation_requested','run_id':run_id}
    return {'status':run['status'],'run_id':run_id}
