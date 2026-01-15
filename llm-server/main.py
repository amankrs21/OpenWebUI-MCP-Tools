import os
import json
import time
from functools import lru_cache
from fastapi import FastAPI
from typing import Any, List, Dict
from pydantic import BaseModel, Field
from langchain_mistralai import ChatMistralAI
from fastapi.responses import ORJSONResponse, StreamingResponse


# -----------------------------
# App
# -----------------------------
app = FastAPI()


# -----------------------------
# Config
# -----------------------------
MODEL_NAME = "mistral-large-latest"
DEFAULT_TEMPERATURE = 0.7
MAX_RETRIES = 3


# -----------------------------
# Utils
# -----------------------------
def _require_mistral_key() -> str:
    token = os.getenv("MISTRAL_API_KEY")
    if not token:
        raise RuntimeError(
            "MISTRAL_API_KEY is not set. Export it before starting the server."
        )
    return token


@lru_cache
def get_mistral_llm() -> ChatMistralAI:
    return ChatMistralAI(
        model=MODEL_NAME,
        temperature=DEFAULT_TEMPERATURE,
        max_retries=MAX_RETRIES,
        api_key=_require_mistral_key(),
    )


# -----------------------------
# OpenAI-style schemas
# -----------------------------
class ChatRequest(BaseModel):
    model: str | None = None
    messages: List[Dict[str, Any]]
    temperature: float = Field(default=DEFAULT_TEMPERATURE, ge=0.0)
    stream: bool = False


# -----------------------------
# Streaming helper (token/chunk streaming)
# -----------------------------
def stream_openai_response(chunks, model_name: str):
    created = int(time.time())

    # Initial role event
    yield (
        "data: "
        + json.dumps(
            {
                "id": "chatcmpl-mistral",
                "object": "chat.completion.chunk",
                "created": created,
                "model": model_name,
                "choices": [{"index": 0, "delta": {"role": "assistant"}, "finish_reason": None}],
            }
        )
        + "\n\n"
    )

    for chunk in chunks:
        content = getattr(chunk, "content", None)
        if not content:
            continue

        yield (
            "data: "
            + json.dumps(
                {
                    "id": "chatcmpl-mistral",
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": model_name,
                    "choices": [{"index": 0, "delta": {"content": content}, "finish_reason": None}],
                }
            )
            + "\n\n"
        )

    # Final finish_reason event
    yield (
        "data: "
        + json.dumps(
            {
                "id": "chatcmpl-mistral",
                "object": "chat.completion.chunk",
                "created": created,
                "model": model_name,
                "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
            }
        )
        + "\n\n"
    )
    yield "data: [DONE]\n\n"


# -----------------------------
# Routes
# -----------------------------
@app.get("/v1/models")
def list_models() -> ORJSONResponse:
    return ORJSONResponse(
        content={
            "data": [
                {
                    "id": MODEL_NAME,
                    "object": "model",
                }
            ]
        }
    )


@app.post("/v1/chat/completions")
def chat(req: ChatRequest):
    model_name = req.model or MODEL_NAME
    llm = get_mistral_llm()

    # Convert OpenAI messages → LangChain format
    prompt = []
    for m in req.messages:
        role = m.get("role")
        content = m.get("content", "")

        if role == "user":
            prompt.append(("human", content))
        elif role == "assistant":
            prompt.append(("ai", content))
        elif role == "system":
            prompt.append(("system", content))

    # ---- Streaming response ----
    if req.stream:
        stream = llm.stream(prompt)
        return StreamingResponse(
            stream_openai_response(stream, model_name),
            media_type="text/event-stream",
        )

    response = llm.invoke(prompt)
    final_text = response.content

    created = int(time.time())
    # ---- Normal response ----
    return ORJSONResponse(
        content={
            "id": "chatcmpl-mistral",
            "object": "chat.completion",
            "created": created,
            "model": model_name,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": final_text,
                    },
                    "finish_reason": "stop",
                }
            ],
        }
    )
