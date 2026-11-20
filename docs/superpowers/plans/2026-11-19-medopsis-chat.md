# MedOpsis text-chat implementation checklist

User approval: the user explicitly confirmed that the plan is approved; do not ask for design/plan approval again. The approved specification is ../specs/2026-11-19-medopsis-chat-design.md.

## Global constraints

Text chat only, Python/FastAPI, Groq qwen/qwen3.8-27b, en/yo/ig/ha, Kotlin/SQLite app-side. No voice/image implementation, agents, vector database, server chat storage, deployment, paid calls, or real patient data. Preserve all validation, authentication, source-review, privacy, and error contracts from the approved specification. Default reference asset is absent until clinician-reviewed content is supplied; do not fabricate clinical approval.

Work in the existing feat/text-chat branch. Earlier tasks used direct/sequential implementation and self-review. The user's latest authorization permits an implementer/reviewer pair for the remaining Task 9 documentation/evidence checkpoint and local task commit only; no additional worktree setup. Scope is the backend and its tests/documentation, not the rest of the platform.

## Tasks

- [x] Bootstrap an isolated .venv with backend/requirements.txt and backend/requirements-dev.txt; protect local artifacts with .gitignore.
- [x] Add a failing HTTP authentication test in tests/test_chat.py, observe RED, then create backend/app/main.py with fail-closed access.
- [x] Implement strict request/reply schemas in ai_services/chat/models.py through test-first slices: languages, roles, history, nonblank text, exact content preservation, UTF-8 limits, and reply/reference validation.
- [x] Implement ai_services/chat/knowledge.py: bounded local approved pack loading, unique source IDs, HTTPS metadata, actual context-size checks; tests use explicitly synthetic fixtures only.
- [x] Implement ai_services/chat/auth.py: RS256 JWT verification against server-configured issuer/audience/HTTPS JWKS; reject token-controlled key URLs; test real signatures with synthetic keys and controlled retrieval.
- [x] Implement ai_services/chat/provider.py: one Groq client, bounded strict JSON output, no redirects/tools/retries/paid fallback, correct safe error mapping and reference resolution. Mock external transport in tests, never claim those are live model results.
- [x] Integrate the authenticated streamed-size-limited POST /chat route and OpenAPI contract; verify conversation/report/language forwarding and errors without health-data or credential leaks.
- [x] Document .env.example, docs/setup.md, docs/api_documentation.md and README.md with commands actually exercised; run the full suite and a local HTTP smoke test.
- [x] Perform the user-authorized synthetic live-model smoke test: actual POST /chat requests for en/yo/ig/ha returned app/provider HTTP 200 with qwen/qwen3.8-27b. See [Qwen smoke-test evidence](../../QWEN_SMOKE_TEST.md). Clinical/native-language review, app identity integration and patient-release governance remain separate external gates.

## Execution and verification

For each behaviour: write its test, run .venv/bin/python -m pytest tests/test_chat.py -q --basetemp="$TMPDIR/medopsis-pytest", observe the missing behaviour, implement minimally, rerun, then self-review the diff. Commit verified task batches locally. All pytest temporary artifacts stay under TMPDIR. Before claiming delivery, run the complete suite and actual local HTTP request; label any mocked dependencies. Do not push or deploy without authorization.

## Verified execution

Automated suite: 51 tests passed. In automated tests, provider HTTP and signing-key retrieval are mocked/controlled; JWT signatures and application code are real. Earlier loopback Uvicorn HTTP checks: OpenAPI 200, missing bearer 401, dummy bearer with unconfigured issuer 503.

Live synthetic verification: the actual POST /chat route and real Groq HTTP calls returned app/provider HTTP 200 for exactly en, yo, ig and ha using qwen/qwen3.8-27b. JWT signatures were real and synthetic; signing-key retrieval was controlled, and the reference pack was an explicitly synthetic software fixture, NOT clinical approval. The final checkpoint parsed the aggregate and all four individual evidence files, checked their equality, exact case IDs, model, statuses, response shape and synthetic reference metadata. See [Qwen smoke-test evidence](../../QWEN_SMOKE_TEST.md).

The user authorized the saved key and confirmed Free tier; billing/account controls were not independently audited and no billing/data-control settings were changed. No further inference was performed for this checkpoint. Generated non-English text is unreviewed, not proof of usable translations. The approved clinical pack, clinical/native-language evaluation, real app issuer/authentication, consent/report association/protected SQLite history, provider controls, authorized authenticated HTTPS deployment and qualified privacy/legal review remain external patient-release gates. No real patient data, remote push or deployment was used/performed.
