import importlib
import importlib.util
from types import SimpleNamespace
import time
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException


def auth_module():
    assert importlib.util.find_spec("ai_services.chat.auth") is not None, "JWT verification is missing"
    return importlib.import_module("ai_services.chat.auth")


@pytest.mark.parametrize("changes,expected", [({}, 200), ({"iss": "wrong"}, 401), ({"aud": "wrong"}, 401), ({"exp": 1}, 401), ({"sub": ""}, 401)])
def test_jwt_signature_and_claim_verification(monkeypatch, auth_setup, changes, expected):
    auth = auth_module()
    seen = []
    class ControlledKeys:
        def get_signing_key_from_jwt(self, token):
            return SimpleNamespace(key=auth_setup.public_key)
    def configured_client(url):
        seen.append(url)
        return ControlledKeys()
    monkeypatch.setattr(auth, "jwks_client", configured_client)
    token = auth_setup.token(**changes)
    if expected == 200:
        assert auth.authorize_token(token) == "synthetic-user"
        assert seen == [auth_setup.issuer + "/jwks"]
    else:
        with pytest.raises(HTTPException) as exc:
            auth.authorize_token(token)
        assert exc.value.status_code == expected


def test_auth_configuration_fails_closed(monkeypatch, auth_setup):
    auth = auth_module()
    monkeypatch.delenv("MEDOPSIS_AUTH_AUDIENCE")
    with pytest.raises(HTTPException) as exc:
        auth.authorize_token(auth_setup.token())
    assert exc.value.status_code == 503


def test_invalid_jwks_port_never_reaches_key_retrieval(monkeypatch, auth_setup):
    auth = auth_module()
    monkeypatch.setenv("MEDOPSIS_AUTH_JWKS_URL", "https://synthetic-issuer.example.invalid:not-a-port/jwks")
    def forbidden(url):
        raise AssertionError("Invalid authentication URL reached key retrieval")
    monkeypatch.setattr(auth, "jwks_client", forbidden)
    with pytest.raises(HTTPException) as exc:
        auth.authorize_token(auth_setup.token())
    assert exc.value.status_code == 503


def test_jwks_connection_failure_is_unavailable(monkeypatch, auth_setup):
    auth = auth_module()
    def broken(url):
        raise jwt.exceptions.PyJWKClientConnectionError("Synthetic JWKS connection failure")
    monkeypatch.setattr(auth, "jwks_client", broken)
    with pytest.raises(HTTPException) as exc:
        auth.authorize_token(auth_setup.token())
    assert exc.value.status_code == 503
    assert exc.value.detail["code"] == "auth_unavailable"


def test_wrong_signature_token_is_rejected(monkeypatch, auth_setup):
    auth = auth_module()
    class ControlledKeys:
        def get_signing_key_from_jwt(self, token):
            return SimpleNamespace(key=auth_setup.public_key)
    monkeypatch.setattr(auth, "jwks_client", lambda url: ControlledKeys())
    other_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    claims = {"iss": auth_setup.issuer, "aud": auth_setup.audience, "sub": "synthetic-user", "exp": int(time.time()) + 300}
    token = jwt.encode(claims, other_key, algorithm="RS256", headers={"kid": "synthetic-key"})
    with pytest.raises(HTTPException) as exc:
        auth.authorize_token(token)
    assert exc.value.status_code == 401
    assert exc.value.detail["code"] == "invalid_token"


@pytest.mark.parametrize("algorithm,key", [("HS256", "synthetic-shared-secret-0123456789ab"), ("none", None)])
def test_non_rs256_algorithm_is_rejected_before_key_retrieval(monkeypatch, auth_setup, algorithm, key):
    auth = auth_module()
    def forbidden(url):
        raise AssertionError("Non-RS256 token reached key retrieval")
    monkeypatch.setattr(auth, "jwks_client", forbidden)
    claims = {"iss": auth_setup.issuer, "aud": auth_setup.audience, "sub": "synthetic-user", "exp": int(time.time()) + 300}
    token = jwt.encode(claims, key, algorithm=algorithm)
    with pytest.raises(HTTPException) as exc:
        auth.authorize_token(token)
    assert exc.value.status_code == 401
    assert exc.value.detail["code"] == "invalid_token"
