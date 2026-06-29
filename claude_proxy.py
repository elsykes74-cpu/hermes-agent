"""
Minimal OpenAI-compatible proxy that routes requests through `claude -p`.
Claude Code is already authenticated, so no API key is needed.
Run this alongside the Hermes gateway.
"""

import asyncio
import json
import subprocess
import sys
import time
import uuid

try:
    from aiohttp import web
except ImportError:
    print("Installing aiohttp...", flush=True)
    subprocess.run([sys.executable, "-m", "pip", "install", "aiohttp", "-q"], check=True)
    from aiohttp import web


PORT = 9191
CLAUDE_BIN = "claude"


def _messages_to_prompt(messages: list) -> str:
    parts = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        if isinstance(content, list):
            content = " ".join(
                c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"
            )
        if role == "system":
            parts.append(f"[System: {content}]")
        elif role == "user":
            parts.append(content)
        elif role == "assistant":
            parts.append(f"[Previous response: {content}]")
    return "\n\n".join(parts)


async def chat_completions(request: web.Request) -> web.Response:
    try:
        body = await request.json()
    except Exception:
        return web.Response(status=400, text="Bad JSON")

    messages = body.get("messages", [])
    prompt = _messages_to_prompt(messages)
    stream = body.get("stream", False)

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        lambda: subprocess.run(
            [CLAUDE_BIN, "-p", prompt, "--max-turns", "1"],
            capture_output=True,
            text=True,
            timeout=180,
        ),
    )

    content = result.stdout.strip()
    if result.returncode != 0 and not content:
        content = f"[Error from claude: {result.stderr.strip()[:200]}]"

    completion_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
    created = int(time.time())
    model = body.get("model", "claude-proxy")

    if stream:
        # Stream a single chunk then done
        async def stream_gen():
            chunk = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": model,
                "choices": [{"index": 0, "delta": {"role": "assistant", "content": content}, "finish_reason": None}],
            }
            yield f"data: {json.dumps(chunk)}\n\n"
            done_chunk = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": model,
                "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
            }
            yield f"data: {json.dumps(done_chunk)}\n\n"
            yield "data: [DONE]\n\n"

        return web.Response(
            status=200,
            content_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
            body=b"".join([s.encode() async for s in stream_gen()]),
        )

    response = {
        "id": completion_id,
        "object": "chat.completion",
        "created": created,
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }
    return web.json_response(response)


async def models(request: web.Request) -> web.Response:
    return web.json_response({
        "object": "list",
        "data": [{"id": "claude-proxy", "object": "model", "created": 0, "owned_by": "claude-code"}],
    })


async def health(request: web.Request) -> web.Response:
    return web.json_response({"status": "ok"})


def main():
    app = web.Application()
    app.router.add_post("/v1/chat/completions", chat_completions)
    app.router.add_get("/v1/models", models)
    app.router.add_get("/health", health)
    print(f"Claude proxy listening on http://localhost:{PORT}", flush=True)
    web.run_app(app, host="127.0.0.1", port=PORT, print=None)


if __name__ == "__main__":
    main()
