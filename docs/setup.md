# Text-chat backend setup

Run from the repository root. Current verification used Python 3.14 in a project-local virtual environment; rerun the suite on the deployment Python version.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements-dev.txt
.venv/bin/python -m pytest tests -q --basetemp="$TMPDIR/medopsis-pytest"
.venv/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --no-access-log
```

Ensure TMPDIR points to an owned scratch directory. The environment, imports, pytest command, and loopback Uvicorn startup were exercised. Uvicorn was bound only to loopback for verification; no deployment was performed. Stop the development server when finished. Do not enable raw request/body/debug logging or expose this server publicly without authorization.

## Server configuration

Supply these environment variables through your deployment/service environment or another secure local mechanism:

- GROQ_API_KEY: project-specific, authorized Groq credential. Never paste it into chat, source control, or the APK.
- MEDOPSIS_AUTH_ISSUER: exact trusted app-token issuer.
- MEDOPSIS_AUTH_AUDIENCE: exact audience for this API.
- MEDOPSIS_AUTH_JWKS_URL: fixed HTTPS signing-key endpoint, without embedded credentials.

The application reads the process environment; it does not load or execute .env. `.env.example` lists names only. Protect any local credential file with mode 0600 and keep it Git-ignored. Do not reuse another workload's key or alter organization-wide controls without authorization.

The app team must supply compatible RS256 JWTs with issuer, audience, expiry, and a nonempty subject. No identity-provider account, user database, or login UI is created here. Missing/invalid setup fails closed.

## Clinical reference input

An approved asset must be supplied at `ai_services/medical_knowledge/references.json`. It is intentionally absent until real clinical review occurs. Required fields:

- version: nonblank string.
- approval_status: `approved`.
- reviewed_by: real reviewer identifier, not an invented approval.
- reviewed_at: valid ISO review date.
- sources: one to eight objects with unique id, title, HTTPS url, and nonblank text.

The model context containing IDs, titles and excerpts may not exceed 4096 UTF-8 bytes. The raw pack file is bounded to 32768 bytes. Curate/review a smaller pack instead of silently truncating it. The loader validates the approval record's structure; this is not independent authentication of a clinician or a clinical-quality certificate.

`tests/fixtures/synthetic_knowledge.json` is expressly a software-test fixture with a synthetic reviewer. Its approval_status value exists to test the parser; it is NOT actual clinician-approved material and must never be copied to the production asset location for patient use.

## Verification status

Automated tests exercise real application code with synthetic JWT signatures and reference fixtures. Provider HTTP and signing-key retrieval are controlled/mocked. A real loopback server was checked: OpenAPI returned 200, unauthenticated POST /chat returned 401, and a dummy bearer token with missing auth configuration returned 503.

Real Qwen 3.8 27B inference through the backend returned HTTP 200 for synthetic en/yo/ig/ha cases. The live app issuer, clinical reference approval and native-language fluency remain unverified. No real health data was used. Before any live-model test, verify the authorized account's free/billing state and applicable data controls; use synthetic inputs only. Native/clinical answer quality cannot be inferred from successful JSON or passing mocked tests.
