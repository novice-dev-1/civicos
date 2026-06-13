"""Gemini wrapper. Falls back to DEMO_MODE canned responses if no key."""

from __future__ import annotations

import json
from typing import Any

from app.config import settings

_client = None


def _get_client():
    global _client
    if _client is not None:
        return _client
    if not settings.gemini_api_key:
        return None
    try:
        from google import genai

        _client = genai.Client(api_key=settings.gemini_api_key)
    except Exception as e:
        print(f"[llm] failed to init Gemini client: {e}")
        _client = None
    return _client


async def gemini_json(
    prompt: str, system: str = "", temperature: float = 0.2
) -> dict[str, Any]:
    """Call Gemini, return parsed JSON. Returns {} on failure."""
    client = _get_client()
    if client is None or settings.demo_mode:
        return {}
    try:
        model = "gemini-2.5-flash"
        full = (system + "\n\n" + prompt).strip() if system else prompt
        resp = client.models.generate_content(
            model=model,
            contents=full,
            config={"temperature": temperature, "response_mime_type": "application/json"},
        )
        text = resp.text or "{}"
        return json.loads(text)
    except Exception as e:
        print(f"[llm] gemini call failed: {e}")
        return {}
