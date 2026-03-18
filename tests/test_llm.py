"""LLM client tests."""

from __future__ import annotations

import asyncio
from typing import Any

from nanoclaw.core.llm import ConnectionPool, LLMClient


class FakeResponse:
    """Minimal fake aiohttp response."""

    def __init__(self) -> None:
        self.status = 200

    async def json(self) -> dict[str, Any]:
        return {
            "choices": [{"message": {"content": "ok"}}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1},
        }

    async def text(self) -> str:
        return ""


class FakePostContext:
    """Async context manager for post responses."""

    def __init__(self, resp: FakeResponse) -> None:
        self._resp = resp

    async def __aenter__(self) -> FakeResponse:
        return self._resp

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None


class FakeSession:
    """Fake session that captures post arguments."""

    def __init__(self) -> None:
        self.endpoint = ""
        self.payload: dict[str, Any] = {}
        self.headers: dict[str, str] = {}

    def post(self, endpoint: str, json: dict[str, Any], headers: dict[str, str]):
        self.endpoint = endpoint
        self.payload = json
        self.headers = headers
        return FakePostContext(FakeResponse())


def test_azure_openai_uses_deployment_endpoint_and_api_key_header() -> None:
    """Azure OpenAI mode should use deployment endpoint and api-key header."""
    fake = FakeSession()
    original = ConnectionPool.get_session

    async def _fake_get_session() -> FakeSession:
        return fake

    ConnectionPool.get_session = _fake_get_session  # type: ignore[assignment]
    try:
        client = LLMClient(
            provider="azure_openai",
            api_key="secret",
            default_model="my-deploy",
            base_url="https://example.openai.azure.com",
            api_version="2024-10-21",
        )
        result = asyncio.run(client.chat([{"role": "user", "content": "hi"}]))
    finally:
        ConnectionPool.get_session = original

    assert result.content == "ok"
    assert "Authorization" not in fake.headers
    assert fake.headers["api-key"] == "secret"
    assert "model" not in fake.payload
    assert fake.endpoint.endswith(
        "/openai/deployments/my-deploy/chat/completions?api-version=2024-10-21"
    )
