"""Phase 2 local RPC boundary adapted from the preserved Phase 1 proof."""
import asyncio
from contextlib import suppress
import json
import os
from pathlib import Path
import signal
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parents[2]
from backend.app.config import load_settings
_AGENT_SETTINGS = load_settings()
MODEL = _AGENT_SETTINGS.generation_model
OLLAMA_BASE = _AGENT_SETTINGS.ollama_url + "/v1"
MAX_FRAME = 1_048_576
MAX_TOTAL = 8 * MAX_FRAME
ALLOWED_COMMANDS = {"get_state", "get_messages", "set_auto_retry", "set_auto_compaction", "prompt", "abort"}
SYSTEM = "You answer from synthetic fixture evidence only. First call search_fixture once. After the tool returns, copy its source_id and text as your answer. Never answer before using the tool. /no_think"


class SpikeError(Exception):
    code = "spike_error"


class ProtocolError(SpikeError):
    code = "rpc_protocol"


class ProviderUnavailable(SpikeError):
    code = "cloud_key_missing"


class RemoteError(SpikeError):
    code = "rpc_rejected"


def decode_frame(raw: bytes) -> dict:
    if len(raw) > MAX_FRAME:
        raise ProtocolError("RPC frame too large")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise ProtocolError("Invalid UTF-8 JSON record") from exc
    if not isinstance(value, dict) or not isinstance(value.get("type"), str):
        raise ProtocolError("RPC record must be an object with a type")
    if value["type"] == "response" and (
        not isinstance(value.get("id"), str)
        or type(value.get("success")) is not bool
        or not isinstance(value.get("command"), str)
    ):
        raise ProtocolError("Malformed RPC response")
    return value


def local_environment(config_dir: str) -> dict:
    # Preserve platform basics, never inherit cloud keys, proxy settings or user Pi config.
    env = {k: os.environ[k] for k in ("PATH", "HOME", "TMPDIR", "LANG", "SYSTEMROOT") if k in os.environ}
    env.update(PI_CODING_AGENT_DIR=config_dir, PI_OFFLINE="1", PI_SKIP_VERSION_CHECK="1", PI_TELEMETRY="0", OLLAMA_NO_CLOUD="1", LENNY_OLLAMA_BASE_URL=OLLAMA_BASE)
    return env


class PiRPC:
    def __init__(self, log_dir: Path, command=None, *, tool_name='search_fixture', extension=None, system=SYSTEM, extra_env=None, max_tokens=256,require_tool=True,model=None,settings=None):
        self.log_dir = log_dir
        self.command_override = command
        self.process = None
        self.pending = {}
        self.events = asyncio.Queue(maxsize=2048)
        self.tasks = []
        self.error = None
        self.closed = False
        self.temp = None
        self.total = 0
        self.protocol = None
        self.diagnostics = None
        self.session_id = None
        self.last_model_text = None
        self.text_tool_call_normalized = False
        self.tool_name, self.extension, self.system = tool_name, extension, system
        self.extra_env, self.max_tokens = extra_env or {}, max_tokens
        self.require_tool=require_tool
        self.settings=settings or _AGENT_SETTINGS
        self.model=model or self.settings.selected_model()
        self.provider_id=self.settings.provider_id
        self.base_url=self.settings.model_base_url

    async def start(self):
        try:self.settings.require_provider()
        except ValueError as exc:raise ProviderUnavailable() from exc
        self.log_dir.mkdir(parents=True, exist_ok=False,mode=0o700)
        self.protocol = (self.log_dir / "stdout.jsonl").open("wb")
        self.diagnostics = (self.log_dir / "stderr.log").open("wb")
        self.temp = tempfile.TemporaryDirectory(prefix="lenny-pi-")
        config = Path(self.temp.name)
        (config / "models.json").write_text(json.dumps({"providers": {self.provider_id: {
            "baseUrl": self.base_url, "api": self.settings.provider_api, "apiKey": "local-placeholder" if self.settings.default_provider=="ollama" else "$LENNY_CLOUD_KEY",
            "models": [{"id": self.model, "name": self.provider_id, "contextWindow": 4096, "maxTokens": self.max_tokens, "reasoning": False}],
        }}}))
        (config / "settings.json").write_text(json.dumps({"compaction": {"enabled": False}, "retry": {"enabled": False}}))
        command = self.command_override or [self.settings.pi_path, "--mode", "rpc", "--no-session", "--offline", "--no-extensions", "--no-mcp", "--no-skills", "--no-prompt-templates", "--no-themes", "--no-context-files", "--no-approve", "--tools", self.tool_name, "-e", str(self.extension or ROOT / "agent/retrieval.ts"), "--provider", self.provider_id, "--model", self.model, "--thinking", "off", "--system-prompt", self.system]
        child_env={**local_environment(str(config)), **self.extra_env, "LENNY_PROVIDER":self.provider_id,"LENNY_PROVIDER_BASE":self.base_url}
        child_env.pop("LENNY_CLOUD_KEY",None)
        if self.settings.default_provider!="ollama":child_env["LENNY_CLOUD_KEY"]=self.settings.selected_key.get_secret_value()
        self.process = await asyncio.create_subprocess_exec(*command, cwd=config, env=child_env, stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, limit=MAX_FRAME + 1, start_new_session=True)
        self.tasks = [asyncio.create_task(self._read_stdout()), asyncio.create_task(self._read_stderr())]
        state = await self.call("get_state")
        self.session_id = state.get("sessionId")
        if not self.command_override:
            model = state.get("model", {})
            if model.get("provider") != self.provider_id or model.get("id") != self.model or model.get("baseUrl") != self.base_url:
                raise ProtocolError("Unexpected provider/model endpoint")
        if state.get("messageCount") != 0:
            raise ProtocolError("Fresh session contains history")
        await self.call("set_auto_retry", enabled=False)
        await self.call("set_auto_compaction", enabled=False)
        return state

    def _fail(self, error):
        self.error = error
        for _, future in self.pending.values():
            if not future.done():
                future.set_exception(error)
        with suppress(asyncio.QueueFull):
            self.events.put_nowait(error)

    async def _read_stdout(self):
        try:
            while True:
                raw = await self.process.stdout.readuntil(b"\n")
                self.total += len(raw)
                if self.total > MAX_TOTAL:
                    raise ProtocolError("RPC stream budget exhausted")
                value = decode_frame(raw)
                projection={k:value[k] for k in ("type","id","command","success","toolName") if k in value}
                self.protocol.write(raw if self.settings.private_rpc_traces else json.dumps(projection).encode()+b"\n")
                self.protocol.flush()
                if value["type"] == "response":
                    entry = self.pending.get(value["id"])
                    if entry is None:
                        raise ProtocolError("Uncorrelated RPC response")
                    command, future = entry
                    if value["command"] != command:
                        raise ProtocolError("Response command mismatch")
                    if not future.done():
                        if value["success"]:
                            future.set_result(value.get("data", {}))
                        else:
                            future.set_exception(RemoteError(str(value.get("error", "RPC rejected"))[:300]))
                else:
                    self.events.put_nowait(value)
        except asyncio.IncompleteReadError as exc:
            if not self.closed:
                self._fail(ProtocolError("Truncated RPC frame" if exc.partial else "Pi exited before completion"))
        except (asyncio.LimitOverrunError, asyncio.QueueFull):
            self._fail(ProtocolError("RPC frame/event limit exceeded"))
        except SpikeError as exc:
            self._fail(exc)

    async def _read_stderr(self):
        captured = 0
        while chunk := await self.process.stderr.read(4096):
            if captured < 65536:
                self.diagnostics.write(chunk[:65536 - captured] if self.settings.private_rpc_traces else json.dumps({"event":"pi_diagnostic","bytes":len(chunk)}).encode()+b"\n")
                self.diagnostics.flush()
            captured += len(chunk)

    async def call(self, rpc_command, **params):
        if rpc_command not in ALLOWED_COMMANDS or {"id", "type"} & params.keys():
            raise ProtocolError("RPC command not allowed")
        if self.error:
            raise self.error
        request_id = uuid.uuid4().hex
        future = asyncio.get_running_loop().create_future()
        self.pending[request_id] = (rpc_command, future)
        try:
            payload = json.dumps({"id": request_id, "type": rpc_command, **params}, ensure_ascii=False).encode() + b"\n"
            self.process.stdin.write(payload)
            await self.process.stdin.drain()
            return await asyncio.wait_for(future, timeout=15)
        finally:
            self.pending.pop(request_id, None)

    async def ask(self, prompt):
        await self.call("prompt", message=prompt)
        tool_trace = []
        turns = 0
        while True:
            event = await self.events.get()
            if isinstance(event, Exception):
                raise event
            kind = event["type"]
            if kind == "turn_start":
                turns += 1
                if turns > 3:
                    raise ProtocolError("Provider turn budget exhausted")
            if kind == "tool_execution_start":
                self.text_tool_call_normalized |= str(event.get("toolCallId", "")).startswith("normalized_")
                if not self.require_tool or event.get("toolName") != self.tool_name or len(tool_trace) >= (2 if self.tool_name=='search_fixture' else 1):
                    raise ProtocolError("Unapproved tool or exhausted tool budget")
                tool_trace.append({"tool": event["toolName"], "args": event.get("args"), "tool_call_id": event.get("toolCallId")})
            if kind == "tool_execution_end":
                if event.get("isError"):
                    raise RemoteError("Fixture tool failed")
                for tool in tool_trace:
                    if tool["tool_call_id"] == event.get("toolCallId"):
                        tool["result"] = event.get("result")
            if kind == "agent_settled":
                break
        messages = (await self.call("get_messages")).get("messages", [])
        assistant = [m for m in messages if m.get("role") == "assistant"]
        if not assistant:
            raise RemoteError("No assistant response")
        if assistant[-1].get("stopReason") in ("error", "aborted"):
            error=RemoteError("Selected model response failed")
            status=__import__("re").search(r"(?<![0-9])(400|401|402|403|404|408|429|500|502|503|504)(?![0-9])",str(assistant[-1].get("errorMessage","")))
            if status:error.code="provider_http_"+status[1]
            raise error
        text = "".join(b.get("text", "") for b in assistant[-1].get("content", []) if b.get("type") == "text")
        self.last_model_text = text
        if not text.strip() or self.require_tool and not tool_trace or any("result" not in t for t in tool_trace):
            raise RemoteError("Missing final text or successful fixture call")
        # Attribution comes from executed tool evidence, never invented model labels.
        sources = [t["result"]["details"]["source_id"] for t in tool_trace] if self.tool_name=='search_fixture' else []
        return {"session_id": self.session_id, "provider": self.provider_id, "model": self.model, "model_text": text,
                "text": text + " " + " ".join(f"[{s}]" for s in dict.fromkeys(sources)),
                "sources": sources, "tools": tool_trace, "messages": messages}

    async def close(self):
        if self.closed:
            return
        # Abort is cooperative first; terminate/reap our process group if it fails.
        if self.process and self.process.returncode is None:
            with suppress(Exception):
                await asyncio.wait_for(self.call("abort"), timeout=0.75)
            self.closed = True
            if self.process.stdin:
                self.process.stdin.close()
            try:
                await asyncio.wait_for(self.process.wait(), timeout=1)
            except asyncio.TimeoutError:
                with suppress(ProcessLookupError):
                    os.killpg(self.process.pid, signal.SIGTERM)
                try:
                    await asyncio.wait_for(self.process.wait(), timeout=1)
                except asyncio.TimeoutError:
                    with suppress(ProcessLookupError):
                        os.killpg(self.process.pid, signal.SIGKILL)
                    await self.process.wait()
        self.closed = True
        for task in self.tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
        for stream in (self.protocol, self.diagnostics):
            if stream:
                stream.close()
        if self.temp:
            self.temp.cleanup()


async def run_once(prompt: str, log_dir: Path, timeout=90, on_adapter=None):
    if not isinstance(prompt, str) or not 1 <= len(prompt) <= 600 or not 0 < timeout <= 90:
        raise ValueError("Prompt or timeout outside spike bounds")
    rpc = PiRPC(log_dir)
    if on_adapter:
        on_adapter(rpc)
    started = time.monotonic()
    try:
        async with asyncio.timeout(timeout):
            await rpc.start()
            result = await rpc.ask(prompt)
            result["duration_seconds"] = time.monotonic() - started
            return result
    finally:
        await rpc.close()
