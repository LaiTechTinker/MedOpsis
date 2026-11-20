# MedOpsis text-chat API

## POST /chat

Authenticate with an app-issued RS256 JWT in the Authorization bearer header. The backend verifies signature, issuer, audience, expiry and nonempty subject against server-pinned settings. It never trusts a key URL from the token. App authentication is distinct from the server's Groq API credential.

JSON request fields (unknown fields rejected):

| Field | Contract |
| --- | --- |
| language | Exactly en, yo, ig, or ha: English, Yoruba, Igbo, Hausa. Required; no automatic language detection or silent English fallback. |
| messages | One to sixteen ordered messages with role user/assistant and nonblank string content up to 4000 characters. Last message must be a user message. |
| screening_report | Optional nonblank report text up to 4000 characters, or null/omitted. No image/audio input. |

Raw body limit: 16384 bytes, checked during streaming before JSON parsing. Combined decoded message/report content limit: 8192 UTF-8 bytes. Oversized context is rejected, not silently shortened. The backend preserves supplied text and stores no conversation history. App-side SQLite manages the conversation history and its protection/retention.

The report is untrusted preliminary screening information; the chatbot does not recognize images, create measurements, change units, or equate a classifier flag with a confirmed diagnosis. Reports/messages cannot override server policy.

## Success

200 JSON with answer and references. Each reference contains only id, title, and url, resolved by the backend from its approved local reference pack. No clinical reference URL is fetched during the request. Provider output uses JSON object mode with explicit answer/reference_ids instructions and is strictly validated locally before publication; unknown IDs or malformed/truncated output are rejected.

Input language propagation and the response contract are mechanically tested. Medical and native-language accuracy remain unverified; a valid response schema is not clinical validation.

## Safe errors

Errors use `{"detail": {"code": "stable_code", "message": "safe explanation"}}`. They do not echo health content, keys, JWTs, or raw provider bodies.

| HTTP | Examples |
| --- | --- |
| 400 | invalid_json |
| 401 | authentication_required, invalid_token |
| 413 | body_too_large, content_too_large |
| 422 | invalid_request |
| 429 | provider_rate_limit; valid numeric Retry-After forwarded |
| 502 | provider_unavailable, provider_invalid_output |
| 503 | auth_not_configured, auth_unavailable, knowledge_unavailable, provider_not_configured, provider_access_unavailable |
| 504 | provider_timeout |

There are no automatic retries, provider/key rotation, paid fallbacks, tool calls, streaming responses, or voice integration. Groq calls use the fixed initial model qwen/qwen3.8-27b, a 600-token completion ceiling, reasoning disabled, a 20-second timeout, verified TLS, and no redirects/environment proxies. These bounds are not a promise of free-account quota or answer quality.

OpenAPI is available at /openapi.json and the normal FastAPI documentation UI at /docs. The request-body schema and bearer-security requirement are verified. These endpoints do not supply medical or identity data.

## Release boundary

Default configuration and missing approved clinical content fail closed. The endpoint was tested with synthetic data and mocked upstream services, plus real loopback error-path requests. Live Groq synthetic requests returned HTTP 200 for en, yo, ig and ha. Signing-key retrieval and reference content were synthetic/controlled; the real app issuer, clinical content and language fluency remain unverified. Patient use requires real clinical/source approval, native-language evaluation, actual auth/consent/storage integration, authorized HTTPS deployment, provider-account controls and qualified privacy/legal review.
