"""Real local model and TCP/FastAPI checks. No mocks or cloud fallback."""
import asyncio
from contextlib import suppress
from datetime import datetime, timezone
import importlib.metadata
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import uuid

import httpx
from spike.adapter import MODEL, ROOT, PiRPC, run_once


def pid_gone(pid):
    try:
        os.kill(pid, 0)
        return False
    except ProcessLookupError:
        return True


async def main():
    batch = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:6]
    folder = ROOT / "docs/agent-transcripts/phase-01" / batch
    folder.mkdir(parents=True)
    records = []
    def save(kind, **fields):
        record = {"kind": kind, "captured_at": datetime.now(timezone.utc).isoformat(), **fields}
        records.append(record)
        with (folder / "results.jsonl").open("a") as stream:
            stream.write(json.dumps(record) + "\n")
        print(json.dumps(record), flush=True)

    async with httpx.AsyncClient(trust_env=False, timeout=10) as client:
        tags = (await client.get("http://127.0.0.1:11434/api/tags")).json()
        version = (await client.get("http://127.0.0.1:11434/api/version")).json()
    save("environment", model=MODEL, ollama_version=version, installed_models=tags, python=sys.version, packages={p: importlib.metadata.version(p) for p in ["fastapi", "uvicorn", "httpx", "pydantic", "starlette"]})

    # Five fresh subprocess/config/history instances, two evidence topics.
    prior_markers = []
    sessions = []
    for index, topic in enumerate(["activation", "retention", "activation", "retention", "activation"]):
        marker = "PRIVATE-" + uuid.uuid4().hex[:10]
        prompt = f"My team is {marker}. For {topic}, what is the review window and evidence code? Use search_fixture and cite the source_id."
        try:
            result = await run_once(prompt, folder / f"repeat-{index + 1}")
            messages = json.dumps(result.pop("messages"))
            expected = ("13", "CEDAR-7319", "FIXTURE-A") if topic == "activation" else ("17", "BIRCH-4826", "FIXTURE-B")
            correct = all(x in result["text"] for x in expected)
            isolated = not any(x in messages for x in prior_markers) and result["session_id"] not in sessions
            policy_log = (folder / f"repeat-{index + 1}" / "stderr.log").read_text()
            policy = json.loads(policy_log.splitlines()[0])
            tools_only = policy.get("active") == ["search_fixture"]
            passed = correct and isolated and tools_only and len(result["tools"]) == 1 and topic in result["tools"][0]["args"].get("query", "").lower()
            save("fresh_local_run", attempt=index + 1, topic=topic, passed=passed, supported_values=correct, isolated=isolated, tool_policy=tools_only, result=result)
            sessions.append(result["session_id"])
        except Exception as exc:
            save("fresh_local_run", attempt=index + 1, topic=topic, passed=False, error=repr(exc))
        prior_markers.append(marker)

    # Real Pi cancellation after prompt acceptance; no fake executable.
    rpc = PiRPC(folder / "real-cancel")
    task = None
    try:
        await rpc.start()
        await rpc.call("prompt", message="Topic: activation. Return the window, code and source_id.")
        task = asyncio.create_task(rpc.ask("This second prompt should be rejected while streaming"))
        # Deliberately exercise actual RPC error behavior rather than count as a model run.
        try:
            await task
            save("real_rpc_busy_rejection", passed=False, error="second prompt unexpectedly accepted")
        except Exception as exc:
            save("real_rpc_busy_rejection", passed=exc.__class__.__name__ == "RemoteError", error=repr(exc))
    finally:
        pid = rpc.process.pid if rpc.process else None
        started = time.monotonic()
        await rpc.close()
        save("real_abort_cleanup", passed=bool(pid and pid_gone(pid)), pid=pid, elapsed=time.monotonic() - started, returncode=rpc.process.returncode if rpc.process else None)

    rpc = PiRPC(folder / "real-task-cancel")
    try:
        await rpc.start()
        task = asyncio.create_task(rpc.ask("Topic: retention. Return the window, code and source_id."))
        while rpc.process.stdin and not any(json.loads(l).get("type") == "agent_start" for l in (folder / "real-task-cancel/stdout.jsonl").read_text().splitlines()):
            if task.done():
                await task
                break
            await asyncio.sleep(0.01)
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task
    finally:
        pid = rpc.process.pid if rpc.process else None
        started = time.monotonic()
        await rpc.close()
        save("real_task_cancel_cleanup", passed=bool(pid and pid_gone(pid)), pid=pid, elapsed=time.monotonic() - started)

    rpc = PiRPC(folder / "real-generation-timeout")
    task = None
    timed_out = False
    try:
        await rpc.start()
        task = asyncio.create_task(rpc.ask("For activation, what is the review window and evidence code? Use search_fixture."))
        async with asyncio.timeout(15):
            while not any(json.loads(l).get("type") == "agent_start" for l in (folder / "real-generation-timeout/stdout.jsonl").read_text().splitlines()):
                if task.done():
                    raise RuntimeError("generation completed before deadline probe")
                await asyncio.sleep(0.005)
        timed_out = False
        try:
            await asyncio.wait_for(task, timeout=0.01)
        except TimeoutError:
            timed_out = True
    finally:
        if task and not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
        pid = rpc.process.pid if rpc.process else None
        started = time.monotonic()
        await rpc.close()
        save("real_generation_deadline", passed=bool(timed_out and pid and pid_gone(pid)), pid=pid, cleanup_seconds=time.monotonic() - started)

    # Real TCP HTTP path, including client disconnect; bind an inherited socket, no fixed-port collision.
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    sock.listen(16)
    port = sock.getsockname()[1]
    api_log = (folder / "api-stderr.log").open("wb")
    server = subprocess.Popen([sys.executable, "-m", "uvicorn", "spike.api:app", "--fd", str(sock.fileno()), "--log-level", "warning"], cwd=ROOT, pass_fds=(sock.fileno(),), stdout=api_log, stderr=api_log)
    sock.close()
    base = f"http://127.0.0.1:{port}"
    try:
        async with httpx.AsyncClient(trust_env=False, timeout=100) as client:
            for _ in range(100):
                try:
                    if (await client.get(base + "/spike/status")).status_code == 200:
                        break
                except httpx.TransportError:
                    pass
                await asyncio.sleep(0.05)
            else:
                raise RuntimeError("spike API startup failed")
            started = time.monotonic()
            response = await client.post(base + "/spike/run", json={"prompt": "For activation, what is the review window and evidence code? Use search_fixture and cite the source_id."})
            data = response.json()
            save("real_fastapi_run", passed=response.status_code == 200 and all(v in data.get("text", "") for v in ["13", "CEDAR-7319", "FIXTURE-A"]), status=response.status_code, wall_seconds=time.monotonic() - started, response=data)

            response = await client.post(base + "/spike/run", json={"prompt": "Topic: activation.", "timeout_seconds": 0.05})
            state = (await client.get(base + "/spike/status")).json()
            save("real_http_timeout", passed=response.status_code == 504 and not state["active"] and state["recent"][-1]["reaped"], status=response.status_code, state=state)

            # Open a real request and close only once its Pi process is visible.
            reader, writer = await asyncio.open_connection("127.0.0.1", port)
            body = json.dumps({"prompt": "Topic: retention. Return the window, code and source_id."}).encode()
            writer.write(f"POST /spike/run HTTP/1.1\r\nHost: 127.0.0.1\r\nContent-Type: application/json\r\nContent-Length: {len(body)}\r\n\r\n".encode() + body)
            await writer.drain()
            live_pid = None
            for _ in range(100):
                state = (await client.get(base + "/spike/status")).json()
                if state["active"] and state["active"][0]["pid"]:
                    live_pid = state["active"][0]["pid"]
                    break
                await asyncio.sleep(0.02)
            busy = await client.post(base + "/spike/run", json={"prompt": "Topic: activation."})
            save("single_request_admission", passed=busy.status_code == 409, status=busy.status_code)
            writer.close()
            await writer.wait_closed()
            for _ in range(200):
                state = (await client.get(base + "/spike/status")).json()
                if not state["active"]:
                    break
                await asyncio.sleep(0.02)
            save("real_http_disconnect", passed=bool(live_pid and pid_gone(live_pid) and not state["active"] and state["recent"][-1]["outcome"] == "disconnected"), pid=live_pid, state=state)
            # Prove a normal run still works after timeout and disconnected request cleanup.
            response = await client.post(base + "/spike/run", json={"prompt": "For retention, what is the review window and evidence code? Use search_fixture and cite the source_id."})
            data = response.json()
            save("real_http_recovery", passed=response.status_code == 200 and all(v in data.get("text", "") for v in ["17", "BIRCH-4826", "FIXTURE-B"]), status=response.status_code, response=data)
    except Exception as exc:
        save("real_http_checks_error", passed=False, error=repr(exc))
    finally:
        server.terminate()
        try:
            await asyncio.to_thread(server.wait, 5)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait()
        api_log.close()
    async with httpx.AsyncClient(trust_env=False, timeout=10) as client:
        save("loaded_model", response=(await client.get("http://127.0.0.1:11434/api/ps")).json())
    save("final_memory", commands={" ".join(cmd): subprocess.run(cmd, capture_output=True, text=True).stdout for cmd in [["memory_pressure", "-Q"], ["sysctl", "vm.swapusage"], ["df", "-h", "."]]})
    failed = [r["kind"] for r in records if r.get("passed") is False]
    save("batch_gate", passed=not failed, failures=failed, note="Fixture tool integration only; no real corpus, database persistence, browser or essay success implied.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
