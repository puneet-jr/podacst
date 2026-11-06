"""Protocol fixture process for tests; never used for live evidence."""
import json
import os
import signal
import sys
import time

mode = sys.argv[1]
messages = []
held = None
if mode == "stubborn":
    signal.signal(signal.SIGTERM, signal.SIG_IGN)


def emit(value):
    raw = json.dumps(value, ensure_ascii=False).encode() + b"\n"
    if mode == "fragmented":
        for byte in raw:
            os.write(1, bytes([byte]))
    else:
        os.write(1, raw)


for line in sys.stdin.buffer:
    command = json.loads(line)
    kind = command["type"]
    response = {"type": "response", "id": command["id"], "command": kind, "success": True}
    if kind == "get_state":
        response["data"] = {"sessionId": "fake-only", "messageCount": 0, "text": "é\u2028行\u2029"}
    if kind == "get_messages":
        response["data"] = {"messages": messages}
    if mode == "wrong-command":
        response["command"] = "unexpected"
    if kind == "prompt":
        if mode == "rejected":
            response.update(success=False, error="fixture rejects prompt")
        emit(response)
        if mode == "rejected":
            continue
        if mode == "malformed":
            os.write(1, b"not-json\n")
        elif mode == "truncated":
            os.write(1, b'{"type":')
            break
        elif mode == "oversize":
            os.write(1, b"x" * 1_048_580 + b"\n")
        elif mode == "unknown-id":
            emit({"type": "response", "id": "unknown", "command": "prompt", "success": True})
        elif mode == "stubborn":
            while True:
                time.sleep(0.1)
        elif mode == "turn-budget":
            for _ in range(4):
                emit({"type": "turn_start"})
        else:
            for _ in range(3 if mode == "tool-budget" else 1):
                emit({"type": "tool_execution_start", "toolName": "bash" if mode == "unsafe-tool" else "search_fixture", "toolCallId": "fixture", "args": {"topic": "activation"}})
                emit({"type": "tool_execution_end", "toolName": "search_fixture", "toolCallId": "fixture", "isError": mode == "tool-error", "result": {"details": {"source_id": "mock"}}})
            messages = [{"role": "assistant", "stopReason": "error" if mode == "model-error" else "stop", "content": [{"type": "text", "text": "mock response"}]}]
            emit({"type": "agent_end"})
            emit({"type": "agent_settled"})
        continue
    if mode == "out-of-order" and kind in ("get_state", "get_messages") and command.get("reorder"):
        if held is None:
            held = response
        else:
            emit(response)
            emit(held)
            held = None
        continue
    emit(response)
