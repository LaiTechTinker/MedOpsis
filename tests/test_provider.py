import importlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import pytest
import requests
from fastapi import HTTPException
from ai_services.chat.models import ChatRequest
from ai_services.chat.knowledge import KnowledgePack


def provider_module():
    assert importlib.util.find_spec("ai_services.chat.provider") is not None, "Groq transport is missing"
    return importlib.import_module("ai_services.chat.provider")


def synthetic_pack():
    return KnowledgePack.model_validate_json((Path(__file__).parent / "fixtures/synthetic_knowledge.json").read_bytes())


def transport(monkeypatch, provider, status=200, content=None, finish="stop", failure=None, retry_after="10"):
    captured = {}
    content = content or json.dumps({"answer": "Synthetic software response", "reference_ids": ["synthetic-1"]})
    class ControlledSession:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def post(self, url, **kwargs):
            captured.update(url=url, trust_env=self.trust_env, **kwargs)
            if failure: raise failure
            return SimpleNamespace(status_code=status, headers={"Retry-After": retry_after}, json=lambda: {"choices": [{"finish_reason": finish, "message": {"content": content}}]})
    monkeypatch.setattr(provider.requests, "Session", ControlledSession)
    return captured


@pytest.mark.parametrize("language,name", [("en", "English"), ("yo", "Yoruba"), ("ig", "Igbo"), ("ha", "Hausa")])
def test_generation_preserves_context_and_resolves_references(monkeypatch, language, name):
    provider = provider_module()
    captured = transport(monkeypatch, provider)
    request = ChatRequest(language=language, messages=[{"role": "user", "content": "  Synthetic request  "}], screening_report="Synthetic report, not a diagnosis")
    result = provider.generate_reply(request, synthetic_pack())
    assert result["answer"] == "Synthetic software response"
    assert result["references"] == [{"id": "synthetic-1", "title": "Synthetic software reference, not medical content", "url": "https://example.invalid/synthetic-reference"}]
    assert captured["url"] == "https://api.groq.com/openai/v1/chat/completions"
    assert captured["trust_env"] is False and captured["allow_redirects"] is False and captured["verify"] is True
    payload = captured["json"]
    assert payload["model"] == "qwen/qwen3.8-27b" and payload["stream"] is False
    assert payload["reasoning_effort"] == "none"
    assert payload["max_completion_tokens"] == 600
    assert payload["response_format"] == {"type": "json_object"}
    assert name in payload["messages"][0]["content"]
    assert "not a licensed doctor" in payload["messages"][0]["content"]
    assert "Translate only the answer value" in payload["messages"][0]["content"]
    data = json.loads(payload["messages"][-1]["content"])
    assert data["message"] == request.messages[-1].content
    assert data["screening_report"] == request.screening_report
    assert "synthetic-unit-test-key-not-real" not in json.dumps(payload)


@pytest.mark.parametrize("status,expected", [(401,503),(403,503),(429,429),(500,502),(302,502)])
def test_provider_http_failures_are_safe(monkeypatch,status,expected):
    provider = provider_module()
    transport(monkeypatch,provider,status=status)
    request=ChatRequest(language="en",messages=[{"role":"user","content":"Synthetic"}])
    with pytest.raises(HTTPException) as exc:
        provider.generate_reply(request,synthetic_pack())
    assert exc.value.status_code==expected
    if status==429: assert exc.value.headers["Retry-After"]=="10"
    assert "synthetic-unit-test-key-not-real" not in str(exc.value.detail)


@pytest.mark.parametrize("content", ["not json", json.dumps({"answer":"Synthetic","reference_ids":["invented"]}), json.dumps({"answer":"Synthetic","reference_ids":[],"extra":"untrusted"})])
def test_invalid_or_untrusted_provider_output_is_rejected(monkeypatch,content):
    provider=provider_module()
    transport(monkeypatch,provider,content=content)
    with pytest.raises(HTTPException) as exc:
        provider.generate_reply(ChatRequest(language="en",messages=[{"role":"user","content":"Synthetic"}]),synthetic_pack())
    assert exc.value.status_code==502


def test_provider_timeout_is_not_a_medical_answer(monkeypatch):
    provider=provider_module()
    transport(monkeypatch,provider,failure=requests.Timeout())
    with pytest.raises(HTTPException) as exc:
        provider.generate_reply(ChatRequest(language="en",messages=[{"role":"user","content":"Synthetic"}]),synthetic_pack())
    assert exc.value.status_code==504


def test_truncated_provider_output_is_rejected(monkeypatch):
    provider = provider_module()
    transport(monkeypatch, provider, finish="length")
    with pytest.raises(HTTPException) as exc:
        provider.generate_reply(ChatRequest(language="en", messages=[{"role": "user", "content": "Synthetic"}]), synthetic_pack())
    assert exc.value.status_code == 502
    assert exc.value.detail["code"] == "provider_invalid_output"


def test_provider_connection_failure_is_unavailable(monkeypatch):
    provider = provider_module()
    transport(monkeypatch, provider, failure=requests.ConnectionError())
    with pytest.raises(HTTPException) as exc:
        provider.generate_reply(ChatRequest(language="en", messages=[{"role": "user", "content": "Synthetic"}]), synthetic_pack())
    assert exc.value.status_code == 502
    assert exc.value.detail["code"] == "provider_unavailable"


@pytest.mark.parametrize("retry_after,forwarded", [("abc", False), ("1" * 13, False), ("4000", False), ("10", True)])
def test_rate_limit_retry_after_is_sanitized(monkeypatch, retry_after, forwarded):
    provider = provider_module()
    transport(monkeypatch, provider, status=429, retry_after=retry_after)
    with pytest.raises(HTTPException) as exc:
        provider.generate_reply(ChatRequest(language="en", messages=[{"role": "user", "content": "Synthetic"}]), synthetic_pack())
    assert exc.value.status_code == 429
    if forwarded:
        assert exc.value.headers["Retry-After"] == retry_after
    else:
        assert exc.value.headers is None or "Retry-After" not in exc.value.headers
