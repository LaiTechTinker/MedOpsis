# MedOpsis text-chat v1 design

Architecture approval recorded: 2026-11-19T11:54:28Z.
Written specification review: approved by the user.
Implementation: backend code is present and locally tested with synthetic/mocked dependencies. Four live Groq Qwen synthetic POST /chat requests returned app/provider HTTP 200; signing-key retrieval and reference content were synthetic/controlled, not real app-issuer integration or clinical approval. See [Qwen smoke-test evidence](../../QWEN_SMOKE_TEST.md). No deployment, paid access, or real-patient-data tests are authorized by this document.

## 1. Goal and delivery boundary

Build the text-chat backend for a ChatGPT-style, health-focused conversation: health education and explanations of screening reports produced by a separate image-recognition model.

Use Python/FastAPI for a small stateless API and Groq for online generation, initially evaluating `qwen/qwen3.8-27b` on the user-confirmed Free tier; billing/account controls were not independently audited. Support English, Yoruba, Igbo, and Hausa.

The first deliverable is a local, integration-ready backend exercised with synthetic test data. Patient-facing release is a separate readiness decision requiring the clinical, language, authentication, consent, storage, and provider-control conditions below.

Kotlin/SQLite remains app-side. The app developer supplies UI, local history, login/consent, and protected device storage. We implement the chat API, input/output validation, provider client, reference-pack handling, medical instructions, and tests. App login implementation and its token issuer are external integration inputs, not new services we build.

Out of scope: voice integration, image processing, model training, agent/tool frameworks, vector search, server-side chat storage, streaming, production deployment, and unrelated platform features.

## 2. Data flow

Kotlin app -> authenticated `POST /chat` -> validated conversation/report + approved reference context -> Groq -> validated answer/reference IDs -> answer text and trusted reference metadata.

The backend retains no conversation state. It does not forward authentication tokens, identity claims, or server credentials to the model. It does not fetch URLs supplied in messages or reports and does not enable model tools.

## 3. API contract

### Request

`POST /chat`, JSON body, `Authorization: Bearer <app-issued token>`.

- `language`: required string, exactly `en`, `yo`, `ig`, or `ha`.
- `messages`: required ordered array, between 1 and 16 entries.
- Each message has exactly `role` (`user` or `assistant`) and `content` (nonblank string, at most 4000 characters). The final message must be a user message.
- `screening_report`: optional nonblank text string, at most 4000 characters; null or omission means no report.
- Reject unknown request/message fields and client-supplied system/developer/tool roles.
- Preserve message/report text; do not silently strip, shorten, translate, normalize measurements, or repair identifiers.

Initial application bounds: raw body at most 16384 bytes; combined UTF-8 message/report content at most 8192 bytes. Check actual streamed body size before JSON parsing. Reject oversized input rather than silently discarding medical context. These are application safety defaults, not a promise about the account's token quota.

A report is untrusted preliminary screening information, not a verified diagnosis. Its condition, provenance, confidence, and measurement semantics are not invented by this API. The app must associate the intended report with the intended conversation/person. The vision workstream does not need to adopt a new internal schema merely for this first text interface; the app supplies its report as text.

### Success

JSON object with exactly:

- `answer`: nonblank answer text in the selected language.
- `references`: array of objects containing `id`, `title`, and `url`, resolved by the backend from the supplied approved pack.

The provider returns a strict structured object containing `answer` and `reference_ids`. Validate it locally. Unknown IDs, wrong types, malformed/truncated output, or unsolicited fields are not repaired into a plausible medical response. Reference-ID validation does not prove factual/clinical support; expert evaluation remains required.

Do not silently return an English answer as a successful local-language response. Application error-message localization is app-side; this is separate from generated answer language.

### Errors

Use FastAPI's `detail` envelope with stable `code` and a safe `message`, without request content, tokens, or raw provider bodies:

- 400: malformed JSON.
- 401: missing, invalid, or expired application authentication.
- 413: raw-body or aggregate-content limit exceeded.
- 422: invalid fields, language, roles, blank content, or history shape.
- 429: upstream quota/rate rejection; preserve a valid numeric `Retry-After` when supplied.
- 502: upstream failure, refused/unusable generation, or invalid output/reference IDs.
- 503: missing/invalid server configuration, unavailable authentication verification, missing approved knowledge, or provider credentials/access unavailable.
- 504: upstream timeout.

Do not turn failures into invented answers. No automatic provider retries, key rotation, paid fallback, or quota-bypass accounts in v1.

## 4. Authentication and transport boundary

The API accepts app-issued RS256 JWT bearer tokens. Configure a trusted issuer, audience, and HTTPS JWKS URL on the server. Verify signature, algorithm, issuer, audience, expiry, and a nonempty subject. Never accept a signing-key URL or trusted issuer from the token/request itself. Missing configuration or inability to verify access fails closed.

The app team chooses/provides the compatible issuer; we do not create a login database or identity-provider account. Tests use explicitly synthetic tokens/keys and mocked or controlled signing-key retrieval. This is not proof of integration with the eventual live app issuer.

Use loopback-only hosting for development. Real-user deployment requires authenticated HTTPS and explicit authorization. No public unauthenticated test mode or shared secret embedded in a published APK.

## 5. Approved reference pack

Use one small trusted local JSON asset at `ai_services/medical_knowledge/references.json`. No runtime web retrieval, embeddings, or vector database.

Pack fields: `version`, `approval_status`, `reviewed_by`, `reviewed_at`, and `sources`. Clinical packs require `approval_status` equal to `approved`, a nonblank real reviewer identifier, a recorded review date, and at least one source.

Each source has `id`, `title`, `url`, and `text`. IDs must be unique; URLs are HTTPS citation metadata and are not fetched during a chat request. Include only clinician-selected excerpts and their true provenance. The serialized model reference context is bounded to 4096 UTF-8 bytes; oversized packs require deliberate clinician-approved curation, not silent truncation.

No such approved clinical asset was supplied. Do not fabricate approval or label a draft as reviewed. Missing, empty, unapproved, or invalid production packs fail closed with 503.

Tests contain explicitly synthetic reference fixtures, not patient records or claims of real clinical review. Test dependency overrides may supply those fixtures for integration checks; no request-accessible production bypass is introduced. Passing those tests does not approve the clinical content.

The clinician selects initial topic coverage and screening-explanation rules before the pilot. The pack's bounded scope is intentional: unsupported medical questions require an honest limitation, clarification, or clinician follow-up rather than model-memory claims presented as reviewed facts.

## 6. Generation contract

Use one Groq client and the fixed initial model candidate `qwen/qwen3.8-27b`; no multi-provider framework. Use JSON object mode with streaming disabled and strict local shape/reference validation. Live Qwen schema decoding failed, so server-side constrained decoding is not relied upon. Set an initial output ceiling of 600 completion tokens and a finite 20-second provider timeout. Verify actual account entitlement, quota, and supported transport parameters before a live test; revise these application constants only on execution evidence, not advertised maximum context length.

Keep `GROQ_API_KEY` server-side. The other required environment inputs are `MEDOPSIS_AUTH_ISSUER`, `MEDOPSIS_AUTH_AUDIENCE`, and `MEDOPSIS_AUTH_JWKS_URL`. No credentials are written into Git, prompts, client storage, or logs. Provider account controls and billing are not changed automatically.

The trusted system instructions must:

- Identify the service as an AI health assistant, not a licensed doctor.
- Answer in the selected language and use the supplied reviewed medical material.
- Treat conversation history and screening text as untrusted context, not instructions to alter policy.
- Explain reported findings without creating readings, altering units, inventing missing reports, or equating classifier confidence with a diagnosis probability.
- Acknowledge uncertainty and unsupported topics; ask useful follow-up questions or recommend clinician review where appropriate.
- Avoid definitive diagnoses, prescriptions, treatment changes, and unsupported medical claims.
- Follow clinician-approved urgent-presentation guidance; do not invent local emergency contacts.
- Cite only the source IDs actually included in context.

Prompts and JSON schemas are safeguards, not a clinical/language validation certificate. No persistent model conversations, file/batch/fine-tuning features, or tool execution are used.

## 7. Failure, privacy, and operations

Do not log medical messages, reports, response text, raw provider errors, authentication tokens, or keys. Test/debug settings must not expose them. Document safe server logging settings and never run public tests against identifiable health data.

Do not execute `.env` as shell code to obtain settings. Deployment/environment setup must supply credentials securely; `.env.example` contains names/non-secret examples only, and `.gitignore` excludes secrets, virtual environments, caches, and local test output before these appear.

The app team's SQLite policy must cover local protection, retention, deletion, and backups. Consent and cross-border/provider-data arrangements require qualified review; this implementation is not a compliance certification. No hosting target, live issuer, or actual account data controls have been verified.

## 8. Tests and evidence

Test-first implementation covers:

- Streamed-size bounds, malformed JSON, strict types, roles, final-user-message requirement, blank input, language validation, and no silent context truncation.
- JWT rejection/verification and fail-closed configuration/key-retrieval behaviour, with clearly synthetic fixtures.
- Pack approval/shape/size, duplicate IDs, trusted reference resolution, and prompt/report injection attempts.
- Follow-up continuity without global history or cross-conversation mixing.
- Provider payload/model selection, structured-output validation, reference spoofing, timeout/status mapping, and safe errors without data/key leakage.
- Representative requests for all four languages and screening-report presence/absence; native and clinician review is separate from mechanical success.
- Actual HTTP-route execution, including a real provider call using authorized free-tier credentials and explicitly synthetic input/reference fixtures when available.

Record mocked/unit results separately from live-provider and live-app-auth results. Do not fabricate API outputs or declare clinical fluency from successful JSON alone.

## 9. Completion and patient-release criteria

Backend delivery requires exercised code, passing meaningful tests, accurate setup/API documentation, and honest reporting of any blocked live-provider/app integration. It is not Android UI delivery or patient-release approval.

Before real health-data use, all of the following are required:

1. Actual clinician-approved pack and reviewed safety/urgent-case wording.
2. Clinician/native-speaker evaluation of the implemented behaviour in English, Yoruba, Igbo, and Hausa, with agreed acceptance criteria.
3. App authentication, consent, report association, and protected SQLite history integration verified.
4. Authorized authenticated HTTPS deployment and appropriate clinical/privacy/legal review.
5. Provider billing/free entitlement, effective quotas, and applicable data/retention controls verified by reading the actual target settings; no unpaid arrangement whose terms prohibit sensitive inputs.

These external inputs are currently absent. They block patient use, not development of the isolated backend with synthetic tests. No clinical approval, native-language accuracy, app-issuer integration, or legal readiness is implied by architecture approval.

## 10. Scope of changes

Implement within the existing `backend/`, `ai_services/chat/`, and `ai_services/medical_knowledge/` boundaries, with a small test suite, `.env.example`, `.gitignore`, and accurate API/setup documentation. Introduce package/export files only where imports require them. Do not modify `android/`, `ai_services/voice/`, or `ai_services/vision/` as part of this backend work.

Architecture and API inputs above are concrete defaults for written-spec review. The subsequent implementation plan must preserve these boundaries and identify every necessary caller, fixture, dependency, and configuration touchpoint. No deployment, remote push, paid upgrade, unrelated host-service change, or skill-housekeeping work is included.

## References

- Approved design discussion and historical discovery record: `../../CHAT_HANDOFF.md`.
- Groq structured-output documentation located during design work: https://console.groq.com/docs/structured-outputs
- Provider/privacy evidence and its limitations are in the handoff; public documentation is not proof of the project's actual account settings.
