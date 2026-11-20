import json
import time
from types import SimpleNamespace
import jwt
import pytest
import requests
from cryptography.hazmat.primitives.asymmetric import rsa


@pytest.fixture(autouse=True)
def forbid_unmocked_provider_calls(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "synthetic-unit-test-key-not-real")
    def blocked(*args, **kwargs):
        raise AssertionError("A unit test attempted a real provider request")
    monkeypatch.setattr(requests.Session, "post", blocked)


@pytest.fixture
def signing_key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture
def auth_setup(monkeypatch, signing_key):
    issuer = "https://synthetic-issuer.example.invalid"
    audience = "medopsis-synthetic-test"
    monkeypatch.setenv("MEDOPSIS_AUTH_ISSUER", issuer)
    monkeypatch.setenv("MEDOPSIS_AUTH_AUDIENCE", audience)
    monkeypatch.setenv("MEDOPSIS_AUTH_JWKS_URL", issuer + "/jwks")
    def token(**changes):
        claims = {"iss": issuer, "aud": audience, "sub": "synthetic-user", "exp": int(time.time()) + 300}
        claims.update(changes)
        return jwt.encode(claims, signing_key, algorithm="RS256", headers={"kid": "synthetic-key", "jku": "https://attacker.example.invalid/ignored"})
    return SimpleNamespace(token=token, public_key=signing_key.public_key(), issuer=issuer, audience=audience)


@pytest.fixture
def chat_client(monkeypatch, auth_setup, tmp_path):
    from pathlib import Path
    from fastapi.testclient import TestClient
    from ai_services.chat import auth, knowledge, provider
    from backend.app.main import app
    class ControlledKeys:
        def get_signing_key_from_jwt(self, token):
            return SimpleNamespace(key=auth_setup.public_key)
    monkeypatch.setattr(auth, "jwks_client", lambda url: ControlledKeys())
    path = tmp_path / "synthetic-knowledge.json"
    path.write_bytes((Path(__file__).parent / "fixtures/synthetic_knowledge.json").read_bytes())
    monkeypatch.setattr(knowledge, "SOURCE_PATH", path)
    class ControlledSession:
        trust_env = True
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def post(self, url, **kwargs):
            content = json.dumps({"answer": "Synthetic integration response, not clinical advice", "reference_ids": ["synthetic-1"]})
            return SimpleNamespace(status_code=200, headers={}, json=lambda: {"choices": [{"finish_reason": "stop", "message": {"content": content}}]})
    monkeypatch.setattr(provider.requests, "Session", ControlledSession)
    return TestClient(app), {"Authorization": "Bearer " + auth_setup.token()}
