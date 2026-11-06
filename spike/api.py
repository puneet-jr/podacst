"""Local spike endpoint. No product sessions, persistence or cloud providers."""
import asyncio
from pathlib import Path
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from spike.adapter import ROOT, SpikeError, run_once

app = FastAPI(title="Phase 1 local Pi spike")
active = {}
outcomes = []
slot = asyncio.Lock()


class RunRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=600)
    timeout_seconds: float = Field(default=90, ge=0.05, le=90)


@app.get("/spike/status")
async def status():
    return {"active": [{"request_id": k, "pid": v.process.pid if v.process else None} for k, v in active.items()], "recent": outcomes[-10:]}


@app.post("/spike/run")
async def run(body: RunRequest, request: Request):
    if slot.locked():
        return JSONResponse({"code": "spike_busy"}, status_code=409)
    await slot.acquire()
    request_id = uuid.uuid4().hex
    def register(rpc):
        active[request_id] = rpc
    task = asyncio.create_task(run_once(body.prompt, ROOT / "docs/agent-transcripts/phase-01/runs" / request_id, body.timeout_seconds, register))
    async def disconnected():
        while not await request.is_disconnected():
            await asyncio.sleep(0.05)
    watcher = asyncio.create_task(disconnected())
    outcome = "failed"
    try:
        done, _ = await asyncio.wait([task, watcher], return_when=asyncio.FIRST_COMPLETED)
        if watcher in done and task not in done:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
            outcome = "disconnected"
            return JSONResponse({"code": "client_disconnected"}, status_code=499)
        result = await task
        outcome = "completed"
        result.pop("messages", None)
        return {"request_id": request_id, **result}
    except TimeoutError:
        outcome = "timeout"
        return JSONResponse({"code": "model_timeout", "request_id": request_id}, status_code=504)
    except SpikeError as exc:
        return JSONResponse({"code": exc.code, "request_id": request_id}, status_code=502)
    finally:
        task.cancel()
        watcher.cancel()
        await asyncio.gather(task, watcher, return_exceptions=True)
        rpc = active.pop(request_id, None)
        outcomes.append({"request_id": request_id, "outcome": outcome, "pid": rpc.process.pid if rpc and rpc.process else None, "reaped": bool(rpc and (not rpc.process or rpc.process.returncode is not None))})
        slot.release()
