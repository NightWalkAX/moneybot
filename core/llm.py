import json
import os
from typing import Any, Dict, List, Optional

import requests

OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
CODING_MODEL = os.getenv("CODING_MODEL", "mistralai/mistral-7b-instruct")
DEFAULT_MODEL = os.getenv("ROUTER_MODEL", "qwen/qwen2.5-7b-instruct:free")


class LLMError(RuntimeError):
    pass


def _headers() -> Dict[str, str]:
    if not OPENROUTER_API_KEY:
        raise LLMError("OPENROUTER_API_KEY is not set")
    return {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "nanobot-local-agent",
    }


def chat_completion(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    temperature: float = 0.2,
    max_tokens: int = 600,
    require_json: bool = False,
) -> str:
    payload: Dict[str, Any] = {
        "model": model or DEFAULT_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if require_json:
        payload["response_format"] = {"type": "json_object"}

    response = requests.post(
        f"{OPENROUTER_BASE_URL}/chat/completions",
        headers=_headers(),
        json=payload,
        timeout=90,
    )
    if response.status_code >= 400:
        raise LLMError(f"OpenRouter error {response.status_code}: {response.text}")

    data = response.json()
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError(f"Unexpected LLM response format: {json.dumps(data)}") from exc


def ask_llm(prompt: str, model: Optional[str] = None) -> str:
    messages = [
        {"role": "system", "content": "You are a concise and useful assistant."},
        {"role": "user", "content": prompt},
    ]
    return chat_completion(messages=messages, model=model or DEFAULT_MODEL)


def generate_code(task_description: str) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "You generate safe Python code only. Return Python code only, no markdown. "
                "Avoid shell/system command execution, subprocess, and network operations unless explicitly requested."
            ),
        },
        {"role": "user", "content": task_description},
    ]
    return chat_completion(messages=messages, model=CODING_MODEL, temperature=0.1, max_tokens=1400)
