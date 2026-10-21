"""Optional Streamlit-to-FastAPI client with a safe local fallback.

Set SURAKSHA_API_URL (e.g. http://127.0.0.1:8000) to use the API service.
If the API is not configured or is temporarily unavailable, established local
Python analysis functions are used so the demo can continue.
"""
from __future__ import annotations

import os
import requests
from dotenv import load_dotenv
from analyzer import analyze_message as _local_message, analyze_url as _local_url

load_dotenv()  # picks up SURAKSHA_API_URL from a local .env file


def _request(path: str, payload: dict):
    base = os.getenv("SURAKSHA_API_URL", "").strip().rstrip("/")
    if not base:
        return None
    headers = {}
    api_key = os.getenv("SURAKSHA_API_KEY", "").strip()
    if api_key:
        headers["X-API-Key"] = api_key
    try:
        response = requests.post(f"{base}{path}", json=payload, headers=headers, timeout=8)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError):
        return None


def analyze_message(text: str, language: str = "English"):
    result = _request("/v1/analyze/message", {"text": text, "language": language})
    return result if result is not None else _local_message(text)


def analyze_url(url: str, language: str = "English"):
    result = _request("/v1/analyze/url", {"url": url, "language": language})
    return result if result is not None else _local_url(url)


def api_configured() -> bool:
    return bool(os.getenv("SURAKSHA_API_URL", "").strip())
