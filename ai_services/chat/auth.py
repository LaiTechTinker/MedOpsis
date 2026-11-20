import os
from functools import lru_cache
from urllib.parse import urlsplit
import jwt
from fastapi import HTTPException


@lru_cache(maxsize=1)
def jwks_client(url: str):
    return jwt.PyJWKClient(url, timeout=20, cache_keys=False)


def authorize_token(token: str) -> str:
    if not isinstance(token, str) or not token or len(token) > 8192:
        raise HTTPException(401, detail={"code": "invalid_token", "message": "A valid application token is required."})
    issuer = os.environ.get("MEDOPSIS_AUTH_ISSUER", "")
    audience = os.environ.get("MEDOPSIS_AUTH_AUDIENCE", "")
    url = os.environ.get("MEDOPSIS_AUTH_JWKS_URL", "")
    try:
        parsed = urlsplit(url)
        # Reject malformed port values before any signing-key request.
        _ = parsed.port
        valid_url = parsed.scheme == "https" and parsed.hostname and not parsed.username and not parsed.password
    except ValueError:
        valid_url = False
    if not issuer.strip() or not audience.strip() or not valid_url:
        raise HTTPException(503, detail={"code": "auth_not_configured", "message": "Application authentication is not configured."})
    try:
        header = jwt.get_unverified_header(token)
        if header.get("alg") != "RS256":
            raise jwt.InvalidTokenError()
        key = jwks_client(url).get_signing_key_from_jwt(token).key
        claims = jwt.decode(token, key, algorithms=["RS256"], issuer=issuer, audience=audience, options={"require": ["exp", "iss", "aud", "sub"]})
        subject = claims["sub"]
        if not isinstance(subject, str) or not subject.strip():
            raise jwt.InvalidTokenError()
        return subject
    except jwt.PyJWKClientConnectionError:
        raise HTTPException(503, detail={"code": "auth_unavailable", "message": "Application authentication is temporarily unavailable."}) from None
    except jwt.PyJWTError:
        raise HTTPException(401, detail={"code": "invalid_token", "message": "The application token is invalid or expired."}) from None
