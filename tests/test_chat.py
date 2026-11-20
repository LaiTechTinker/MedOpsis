from fastapi.testclient import TestClient


def test_chat_requires_application_authentication():
    import backend.app.main as entrypoint
    assert hasattr(entrypoint, "app"), "The chat API has not been implemented"
    response = TestClient(entrypoint.app).post("/chat", json={"language": "en", "messages": [{"role": "user", "content": "Synthetic test message"}]})
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "authentication_required"


def test_authenticated_chat_uses_real_route_with_synthetic_dependencies(chat_client):
    client, headers = chat_client
    response = client.post("/chat", headers=headers, json={"language": "yo", "messages": [{"role": "user", "content": "Synthetic request"}], "screening_report": "Synthetic SCREENING_TEST flag"})
    assert response.status_code == 200
    assert response.json()["answer"] == "Synthetic integration response, not clinical advice"
    assert response.json()["references"][0]["id"] == "synthetic-1"


import pytest


@pytest.mark.parametrize("body,status", [(b"not json", 400), (b" " * 17000, 413)])
def test_raw_body_limits_and_json_errors(chat_client, body, status):
    client, headers = chat_client
    response = client.post("/chat", headers=headers, content=body)
    assert response.status_code == status


@pytest.mark.parametrize("payload,status", [
    ({"language":"de","messages":[{"role":"user","content":"Synthetic"}]},422),
    ({"language":"en","messages":[{"role":role,"content":"a"*3000} for role in ["user","assistant","user"]]},413),
])
def test_request_errors_use_safe_api_envelope(chat_client,payload,status):
    client,headers=chat_client
    response=client.post("/chat",headers=headers,json=payload)
    assert response.status_code==status
    assert "code" in response.json()["detail"]
    assert "a"*100 not in response.text


def test_api_requires_approved_reference_pack(chat_client,monkeypatch,tmp_path):
    from ai_services.chat import knowledge
    client,headers=chat_client
    monkeypatch.setattr(knowledge,"SOURCE_PATH",tmp_path/"missing.json")
    response=client.post("/chat",headers=headers,json={"language":"en","messages":[{"role":"user","content":"Synthetic"}]})
    assert response.status_code==503


def test_openapi_documents_chat_input_and_bearer_auth(chat_client):
    client,_=chat_client
    operation=client.get("/openapi.json").json()["paths"]["/chat"]["post"]
    assert "requestBody" in operation
    assert operation["security"]


def test_chat_forwards_full_history_and_is_stateless(chat_client, monkeypatch):
    import json
    from types import SimpleNamespace
    from ai_services.chat import provider
    client, headers = chat_client
    captured = []
    class CapturingSession:
        trust_env = True
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def post(self, url, **kwargs):
            captured.append(kwargs["json"])
            content = json.dumps({"answer": "Synthetic integration response, not clinical advice", "reference_ids": ["synthetic-1"]})
            return SimpleNamespace(status_code=200, headers={}, json=lambda: {"choices": [{"finish_reason": "stop", "message": {"content": content}}]})
    monkeypatch.setattr(provider.requests, "Session", CapturingSession)
    history = [
        {"role": "user", "content": "Synthetic first question"},
        {"role": "assistant", "content": "Synthetic first answer"},
        {"role": "user", "content": "Synthetic follow-up question"},
    ]
    response = client.post("/chat", headers=headers, json={"language": "en", "messages": history})
    assert response.status_code == 200
    assert captured[0]["messages"][0]["role"] == "system"
    assert captured[0]["messages"][1:] == history
    fresh = [{"role": "user", "content": "Synthetic independent question"}]
    response = client.post("/chat", headers=headers, json={"language": "en", "messages": fresh})
    assert response.status_code == 200
    assert captured[1]["messages"][1:] == fresh
    assert len(captured[1]["messages"]) == 2
