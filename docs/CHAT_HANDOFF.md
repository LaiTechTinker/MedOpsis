# MedOpsis — text-chat feature handoff

## 1. Start here: scope and approval state

**Current status: backend implemented; 51 automated tests passed, and four synthetic live qwen/qwen3.8-27b requests returned app/provider HTTP 200. Live app-auth, clinical/native-language and patient-release checks remain outstanding.**

See [Qwen smoke-test evidence](QWEN_SMOKE_TEST.md): the actual POST /chat route used real synthetic JWT signatures, controlled signing-key retrieval and synthetic references, NOT clinical approval. Free-tier status was user-confirmed, not independently audited.

Architecture approval was recorded at `2026-11-19T11:54:28Z`. The current specification is [MedOpsis text-chat v1 design](superpowers/specs/2026-11-19-medopsis-chat-design.md), on the local branch `feat/text-chat`.

The remaining sections preserve the earlier discovery/proposal snapshot. Statements below about approval, implementation, model choice, credentials and execution are historical; the linked specification and smoke-test evidence describe the current state. Patient-use requirements remain unsatisfied. No deployment or paid access has been authorized.

This document transfers the conversation and research to another agent. It is not an approved implementation specification, authorization to deploy, or a clinical/compliance certification. The user's request to produce this handoff authorizes documentation, not implementation.

MedOpsis is a group project: an AI-powered platform for optical-based health screening, Nigerian-language support, and medical education. The user and the continuing agent are responsible for the **text-chat feature**, not the entire platform.

The intended interaction is a **ChatGPT-style, health-focused text conversation**: consultation-like health education and explanations of results produced by a separate image-recognition model. The voice feature is separate. Do not reconnect voice to our chat service simply because reusing one service appears convenient; that was an explicit scope correction from the user.

No runnable chat API, application tests, model evaluations, or deployment were produced in this session. The next development step is to resolve necessary integration decisions and obtain approval of a concrete design before writing application code.

The design-approval question was cancelled without an answer. The user's earlier “yes” confirmed availability of a qualified clinician; it did **not** approve the architecture.

## 2. Confirmed requirements and team context

These facts came directly from the user and should not be re-asked unless circumstances change:

| Topic | Confirmed information |
| --- | --- |
| Project | MedOpsis; AI-powered optical health screening, local Nigerian-language support, and medical education. |
| Repository | https://github.com/LaiTechTinker/MedOpsis.git |
| Team | There is an app developer and an AI teammate working on the voice feature. The user and this agent work on chat. |
| App technologies | Kotlin and SQLite are the technologies the team knows it will use. No backend framework or app-to-chat API contract was agreed. |
| Chat purpose | Patient health education, consultation-like conversation, explaining screening results, and appropriate next-step guidance. |
| Chat experience | Text-based, like ChatGPT; separate from voice. This does not imply every ChatGPT feature is required. |
| Image recognition | A separate model performs image recognition. Chat consumes its results; chat does not perform the recognition. Ownership of that model was not established. |
| Connectivity | An online AI API is acceptable for generating answers. Offline inference is not required. |
| Languages | English, Yoruba, Igbo, and Hausa are all in scope for the first version. |
| Data | The intended pilot/app will handle real people's health data, not only synthetic demonstrations. |
| Budget | Free API access initially; paid access could be introduced in the future. Paid calls are not currently authorized. |
| Clinical reviewer | A qualified clinician is available to review medical responses and screening explanations before the pilot. No review has occurred in this session. |

Native-speaker reviewers, reviewed medical documents, actual screening-report examples, authentication details, deployment arrangements, and a project API account/key have **not** been supplied or agreed.

“Doctor chatbot” describes the desired conversational style. It is not permission to impersonate a licensed doctor or present model output as a confirmed diagnosis.

## 3. Repository snapshot: verified, not inferred

Repository snapshot taken at **2026-11-18T21:52:24Z**.

- Local working directory: `/home/ubuntu/projects/MedOpsis`
- Git origin: `https://github.com/LaiTechTinker/MedOpsis.git`
- Local branch: `main`
- Local HEAD: `86e3c3fb2f52d2832ad82f06230d32bc3e70731d`
- GitHub `refs/heads/main` returned the same HEAD at the snapshot check.
- Worktree was clean before this handoff was created.
- There were **2 commits and 13 tracked files**; all 13 existing tracked files were **0 bytes**.
- No repository or checked parent-directory `AGENTS.md` instructions were found at that check.

Recent commits, preserving the timestamps reported by Git:

| Commit | Author timestamp | Subject |
| --- | --- | --- |
| `86e3c3fb2f52d2832ad82f06230d32bc3e70731d` | `2026-11-17T22:25:04+01:00` | changes made |
| `3be4c68486887f2c95383f8beb622b9b92cf4e29` | `2026-11-17T22:14:01+01:00` | folder setup |

Existing tracked files before this document:

```text
.env.example
README.md
ai_services/chat/.gitkeep
ai_services/medical_knowledge/.gitkeep
ai_services/safety/.gitkeep
ai_services/vision/.gitkeep
ai_services/voice/.gitkeep
android/app/.gitkeep
backend/app/main.py
backend/requirements.txt
docs/api_documentation.md
docs/architecture.md
docs/setup.md
```

This is a folder/file skeleton, **not an existing implemented stack**. In particular:

- `backend/app/main.py` does not yet contain a FastAPI application or any route.
- `backend/requirements.txt` does not specify dependencies.
- README, setup, architecture, and API documentation are empty.
- There are no tracked application tests or CI workflows in this snapshot.
- No tracked `.gitignore` is present; establish appropriate secret/build exclusions before introducing credentials or development artifacts.
- Kotlin/SQLite is confirmed team intent; runnable Android code is not present in this checkout.

No application startup or build command is currently verified. Do not tell the user that a server can already be started or that application tests pass.

This handoff is a local documentation addition. It has not been committed or pushed by this session. Public clone/read access succeeded; write/push authorization was not tested. No deployment was performed or verified elsewhere.

Before continuing, check live state rather than relying on this snapshot:

```text
git -C /home/ubuntu/projects/MedOpsis status --short --branch
git -C /home/ubuntu/projects/MedOpsis log -5 --oneline
git ls-remote --heads https://github.com/LaiTechTinker/MedOpsis.git
```

On another machine, use that machine's checkout path. This local handoff will need to be transferred; it is not yet available through a new GitHub commit. Preserve any teammates' new or uncommitted work; do not reset, force-push, or pull changes blindly.

## 4. Explicitly outside our current scope

- Voice capture, speech recognition, speech generation, and voice-chat integration.
- Image capture, image recognition, optical-model training, and hardware calibration.
- Building or rewriting the whole Android application.
- Replacing Kotlin or SQLite without a new team decision.
- Model fine-tuning or training a medical language model.
- Agent frameworks, tool-using autonomous medical agents, or a vector database at this stage.
- Server-side chat-history storage or an additional chat database in the proposed v1.
- Full ChatGPT parity: browsing, arbitrary file/image uploads, tool execution, and other unrelated features.
- Provider-account changes, paid upgrades, production deployment, or remote publishing without authorization.

Do not infer that “optical” means specifically eye screening. Earlier examples of heart-rate, oxygen-saturation, or eye-image findings were explanations of what a screening result could look like, **not confirmed MedOpsis capabilities**. The actual screening conditions, measurements, report format, and model calibration remain unknown.

## 5. Two approaches discussed — recommendation is not approval

### Recommended for the intended real-data pilot

A small chat API + hosted model + a **small clinician-approved medical reference pack** included directly in the model context.

This adds content preparation and review, but allows explanations to be grounded in selected material without introducing retrieval infrastructure, a vector database, or model training. Reference coverage is intentionally bounded; unsupported medical questions should acknowledge the gap rather than invent an answer.

### Leanest synthetic-demo alternative

The same small API with a medical system prompt and model knowledge alone.

This requires less preparation, but medical claims are not grounded in a reviewed reference pack. It was not recommended as the basis for unrestricted patient-facing use. This alternative has not been selected or implemented.

The user has not approved either architecture. The next agent may refine the proposal with the user; do not silently convert a recommendation into a committed decision.

## 6. Proposed v1 architecture and ownership

**Everything in this section is a proposal awaiting approval.**

```text
Kotlin text-chat interface
    -> authenticated HTTPS POST /chat
    -> small Python/FastAPI backend
    -> Groq-hosted language model with reviewed reference context
    -> answer text and references
```

Python/FastAPI was proposed because the repository already reserves `backend/app/main.py`. It is **not** an agreed or installed backend framework. Confirm this choice before implementation; Kotlin/SQLite does not by itself settle the backend language/framework.

Proposed team split:

| Responsibility | Proposed owner / boundary |
| --- | --- |
| Android chat UI and conversation display | App developer. |
| Local conversation history | App developer, using SQLite with an agreed protection/retention policy. |
| User login, consent flow, and protected local storage | App-team dependencies; ownership and contract need explicit agreement. |
| Chat API and provider calls | User + continuing agent. |
| Server-side validation and auth-token verification | Chat backend; integrate with the app team's agreed authentication scheme. No scheme has been chosen. |
| Medical instructions and reference-pack handling | User + continuing agent, reviewed by the clinician. |
| Clinical and language review | Clinician plus suitable native-language reviewers; native reviewers have not been confirmed. |
| Vision and voice implementations | Other workstreams; not modified by our chat implementation. |

The backend should be stateless with respect to chat history in v1. The app supplies the relevant history for the current conversation. Do not add server persistence simply to imitate ChatGPT's interface.

A plain request/response endpoint was proposed. Streaming was not requested or agreed. Do not add streaming infrastructure unless the app developer establishes a concrete need.

## 7. Proposed API contract — not implemented or finalized

Proposed endpoint: **POST /chat**.

| Request concept | Purpose | Boundary / unresolved detail |
| --- | --- | --- |
| Conversation history | Enables follow-up questions and continuity. | Bound its size; agree field names and role conventions with the app developer. Client history is untrusted. |
| Selected language | Requests English, Yoruba, Igbo, or Hausa. | Agree representation: names or platform language codes. Automatic detection is not a confirmed requirement. |
| Optional screening report | Supplies the separate image model's findings for explanation. | Actual schema, provenance, confidence/quality fields, and whether the transport is structured JSON or report text are unknown. |
| Authentication token | Identifies an authorized pilot/app user. | Token issuer, audience, verification method, and login ownership are unresolved. |

Proposed response concepts:

- Answer text suitable for display in the selected language.
- References drawn from the approved reference pack, not invented URLs.
- Appropriate uncertainty and clinician-follow-up guidance where relevant.
- A clear error when a request or provider operation fails; never a fabricated successful medical response.

These are design concepts, not a runnable API example. Do not invent response traces, HTTP success results, or a screening schema and claim the team supplied them.

Important implementation boundaries to preserve after approval:

- Accept only the history roles the team explicitly permits; never accept a client-supplied system/developer instruction as trusted policy.
- Treat reports, messages, and source text as data, not authority to override the backend's instructions.
- Preserve supplied readings, units, labels, and uncertainty if they exist; never manufacture missing measurements or convert classifier confidence into a clinical diagnosis probability.
- Establish request/body/history/output limits using the selected account's effective quotas and realistic multilingual payloads.
- Return only reference IDs/URLs that exist in the supplied approved pack. Citation-ID validation alone does not prove that a medical statement is supported; clinical/content evaluation is still required.
- Do not silently fall back to English when a local language was selected. Agree fallback behavior and test it.
- Integrate real authentication; do not ship a provider API key or a shared backend secret inside a public APK as a substitute for user authentication.

## 8. Model/provider proposal and verified policy findings

### Candidate, not a completed selection

The proposed first provider to evaluate is **Groq**, initially using its free-plan allowance.

The exact initial model candidate is **`openai/gpt-oss-120b`**, which was listed in Groq's production-model catalog when checked.[14]

“Production” here is the provider's service/catalog designation; this session established **no clinical validation or English/Yoruba/Igbo/Hausa medical-language fitness** for this route.

The `openai/` prefix in the model ID does not make the proposed calls OpenAI API calls. The proposal is to use the model **through Groq**. Do not inherit a model maker's API privacy rules, ChatGPT subscription entitlement, or another router's pricing for this route.

The published Groq catalog showed paid-usage prices of **$0.15 input / $0.60 output per 1M tokens** for this model.[14]

Those are Groq's published route prices, not a free-tier bill, a cost-per-chat estimate, or authorization to spend. Recheck before budgeting or upgrading. A capped free-plan allowance is not a guarantee that the hosted endpoint is universally or permanently zero-priced.

Groq documents an upgrade from Free to Developer with a payment method and usage billing.[17]

The future paid option does not justify building a multi-provider abstraction now. First agree one route and prove it works. Do not enable paid access without renewed user authorization.

### Privacy and quota findings actually checked

- Groq documentation says customers may enable **Zero Data Retention**, preventing retention for system reliability and abuse monitoring; retention-dependent features are disabled as applicable.[4]
- The same documentation describes retained customer data as stored in GCP buckets in the United States.[4]
- These statements are public documentation, **not proof that a MedOpsis account is configured this way**. Exact processing/transit/residency arrangements, contracts, and account controls have not been verified.
- Groq states that rate limits apply at the **organization level**, not independently to each app user.[15]
- Do not treat numeric rows in the source appendix as guaranteed account entitlements. Verify the actual Free/Developer tier, selected model access, and effective request/input/output quotas in account settings and real response headers. No project account limits were read.
- Groq's responsible-AI policy says outputs may be inaccurate and calls for appropriate human oversight, testing, and safeguards for consequential uses.[13]
- Google's **Unpaid Gemini Services** terms explicitly prohibit submission of sensitive, confidential, or personal information.[7]
- Unpaid Gemini was therefore excluded for live health data under the checked arrangement. Do not generalize this to all Google products or billing-enabled/paid arrangements; those require a separate policy review.

No MedOpsis API key was supplied, inspected, created, or used. No LLM inference request, paid request, or real-patient-data transmission was performed. Existing host credentials/accounts were not inspected and must not be reused implicitly.

Before patient use, verify and read back the chosen account's data controls, model access, quota, and billing state. Prefer project-specific credentials and appropriate separation from unrelated applications; changing organization-wide controls can affect other workloads.

## 9. Proposed medical-reference and conversational behaviour

The following are proposed safeguards and evaluation targets, not implemented guarantees:

- Identify the service as an AI health assistant rather than a licensed doctor.
- Provide useful health education and consultation-like follow-up within the agreed clinical scope.
- Explain the report supplied by the image-recognition workstream; do not perform image recognition or declare a screening finding a confirmed diagnosis.
- Ground medical explanations in the selected, reviewed reference material.
- Acknowledge uncertainty, insufficient information, and unsupported topics.
- Recommend suitable clinician follow-up; agree handling of urgent presentations with the clinician rather than improvising local emergency instructions or contact numbers.
- Avoid unsupported diagnoses, prescriptions, treatment changes, and other consequential autonomous medical decisions.
- Treat a system prompt as one safeguard, not proof of clinical or translation safety.

A small reference pack can initially be supplied directly in context. Do not add embeddings, search infrastructure, or a vector store until the actual content volume/use case requires it and the user approves.

The clinician should help select the initial covered topics, source material, screening-explanation rules, and escalation wording. Record the actual source origin, title, version/date, and review status. Do not mark content “clinician approved” because a clinician is available or because another model graded it.

No medical reference pack, reviewed translations, screening-specific rules, or patient-facing disclaimer wording currently exists in the repository. Exact content selection and review are unfinished work.

## 10. Patient-use privacy, security, and release gates

**Real-data use is the stated target, but readiness has not been established.** The following are proposed launch conditions to settle with the team, not a claim that the application satisfies them.

### Backend / API

- Server-side provider credentials; no keys in Git, application bundles, client SQLite, logs, or exception messages.
- Authenticated HTTPS access and backend verification of the agreed user-authentication token.
- Input validation, bounded request/history sizes, safe provider-error handling, and appropriate abuse/rate controls.
- No raw medical-conversation logging, request-body tracing, or accidental response dumps in errors.
- Verified provider data controls and a documented billing/quota boundary.
- No invented answers when a provider is unavailable, a report is missing, or a reference is unsupported.

### App-team dependencies

- Login/account handling and consent mechanisms with explicit ownership.
- An agreed policy for history retention, deletion, device backups, and protected local SQLite storage.
- Clear AI/screening limitations and language/clinical-review status in the patient experience.
- Correct association of a screening report with the intended conversation/person.

### Clinical / native-language review

- Clinician review of the actual reference content, prompts, representative replies, screening explanations, and escalation behaviour.
- Native-speaker review of medical meaning and terminology in Yoruba, Igbo, and Hausa, with English clinical review as well.
- Evaluation of uncertainty, code-switching, follow-up continuity, dangerous advice, and incorrect or overconfident interpretations.
- An agreed process for identifying and responding to harmful or misleading pilot outputs.

### Privacy/legal review

NDPC guidance states that cross-border transfers of personal data require adequate protection under the NDP Act's transfer provisions.[1]

Have a qualified privacy/legal reviewer determine the applicable lawful basis, consent/notice requirements, transfer safeguards, provider agreements, and whether an impact assessment, registration, or health-sector approvals are required for this particular pilot. No such compliance assessment has been performed in this session.

A provider ZDR switch, clinician availability, a disclaimer, or passing software tests is not by itself a legal or clinical clearance. Do not assume US HIPAA is the governing Nigerian rule, and do not assume this document settles medical-device classification or approval requirements.

Development should use synthetic cases until the relevant clinical/data-handling conditions are settled. Free API access is not a reason to send identifiable health data to an unreviewed route.

## 11. Verification plan — not tests already run

After design approval, use the project's agreed test tooling and a small meaningful test suite. Do not fabricate test results or substitute mocks for a claimed live-provider test.

| Area | Planned checks |
| --- | --- |
| Request validation | Missing/wrong types, unsupported languages, oversized history/body, disallowed roles, malformed reports. |
| Conversation continuity | Follow-up questions use the supplied conversation context; no leakage or mixing between unrelated conversations. |
| Screening explanations | No report, incomplete report, unknown findings, source uncertainty, units/labels preserved, no invented readings or diagnoses. |
| Grounding | Unknown references rejected; URLs come from reviewed metadata; unsupported claims/refusal behaviour evaluated. |
| Prompt injection | Attempts through user messages, prior assistant messages, or report text do not gain trusted instruction status. |
| Languages | Representative educational and result-explanation cases in English, Yoruba, Igbo, and Hausa; clinician/native review, not just an LLM grader. |
| Safety | Unsafe requests, overconfident interpretation, treatment/prescription requests, and urgent-presentation handling reviewed against clinician expectations. |
| Provider failures | Invalid/revoked key, forbidden access, quota/rate rejection, timeout, upstream failure, malformed output; clear errors without fabricated medical replies or secret/health-data leaks. |
| Access / privacy | Missing/invalid/expired auth, agreed ownership boundaries, consent integration, protected history handling, and absence of raw medical logs. |
| Actual integration | A real HTTP request reaches the implemented route, calls the authorized selected provider with synthetic data, and returns the agreed response shape. |

Mocked provider tests are useful and must be labelled as mocked. A live synthetic-data smoke test requires project credentials and user-authorized access. Confirm the account is on the permitted free arrangement before calls; do not silently upgrade or use a paid fallback.

No application tests, model-language benchmarks, clinician evaluations, or end-to-end chat requests have been executed yet. Document what ran, its actual output, and remaining limits when those tests occur.

## 12. Open decisions to resolve, in priority order

1. **Design approval:** Python/FastAPI backend, the reference-pack approach, API contract, team responsibilities, and release conditions are proposed, not approved.
2. **Authentication and app integration:** Who provides login/tokens and consent; token verification contract; API hosting/base URL; request/response field names; app history behaviour.
3. **Screening reports:** Which conditions/results the recognition workstream produces; exact schema; provenance and confidence/quality semantics; handling of insufficient-quality/unsupported results. Do not guess hardware/model capabilities.
4. **Medical content:** Initial covered topics, authoritative sources, review method, scope limits, and clinician-approved escalation/limitation wording.
5. **Native-language evaluation:** Identify reviewers and acceptance criteria; no reviewer availability or translation quality is yet confirmed.
6. **Provider/account setup:** Approved route/model, project-specific credentials, ZDR readback, effective model access and quotas, and permitted billing state.
7. **Real-data governance:** Consent/notice, retention/deletion/backup rules, transfer safeguards, provider agreements, and qualified clinical/privacy review.
8. **Hosting and pilot size:** Deployment target, transport/security controls, expected concurrency and workload, and operations/support responsibilities. No hosting target or pilot volume was agreed.
9. **UI details:** Language selection/fallback, report attachment/display, reference presentation, and whether streaming is actually needed; coordinate with the app developer rather than rebuilding the app.

Do not restart discovery by asking again whether this is chat or voice, which four languages are needed, whether internet is acceptable, whether the budget starts free, or whether a clinician is available. Those were answered. Ask only necessary unresolved questions, unless the user changes the requirements.

## 13. Continuation runbook for the next agent

### Immediate next steps

1. Read this document and inspect the current repository/branch/status; teammates may have added code since the snapshot.
2. Keep the workstream text-chat only. Confirm unresolved app-auth/report integration details with the user/team.
3. Present/refine the proposed design and obtain **explicit design approval**. The handoff request, cancelled approval prompt, and clinician-availability answer are not that approval.
4. If continuing under the current Superpowers workflow, load the relevant namespaced skills and honour phase gates. The observed phase remains `idle`; no implementation transition was made.
5. After design approval, write the approved specification, review it with the user, then create the implementation plan using the required workflow. This handoff is not the approved spec or implementation plan.

### After approval — suggested implementation scope, not permission to start now

Use existing boundaries and the smallest complete change. Likely affected locations, to re-evaluate against actual new callers:

| Location | Potential chat-related work |
| --- | --- |
| `backend/app/main.py` | Small API entry point, chat route, request validation, safe error/auth integration. |
| `backend/requirements.txt` | Only dependencies actually required for the approved backend. |
| `ai_services/chat/` | Chat/model instructions and provider-call logic if this is the agreed module boundary. |
| `ai_services/medical_knowledge/` | Approved reference data/metadata, coordinating ownership if this becomes shared. Do not create a voice dependency. |
| `ai_services/safety/` | Use only if approved and genuinely useful; a placeholder folder is not a reason to add an abstraction. |
| `.env.example` and a new `.gitignore` | Non-secret configuration examples and appropriate exclusions before real credentials appear. |
| `docs/api_documentation.md` and `docs/setup.md` | Actual API/setup instructions that match exercised code; never document invented commands. |
| Tests / fixtures | Small test coverage for new non-trivial logic and labelled synthetic data. No test structure exists yet. |
| App-side callers | Coordinate contract updates with the app developer; do not claim their caller is integrated until verified. |

Do not add exports, wrappers, database schemas, config options, or “future provider” machinery without an actual caller/need. Preserve existing validation/error handling when teammates' code appears. Search all callers before changing shared behaviour.

Follow test-first development for non-trivial logic once implementation is approved. Exercise the resulting API, not just isolated helpers. Report mocked tests and real provider/HTTP tests separately. Keep physician/native review and privacy-release blockers separate from code-test status.

### Completion reporting

Report only verified facts: changed files, tests/requests actually run, and remaining blockers. Do not call the pilot patient-ready just because a route returns text. Do not publish, deploy, upgrade billing, alter unrelated host services, or mutate provider controls without authorization.

The user's active coding preference is Ponytail `full`: smallest complete solution, existing patterns/platform features first, no unnecessary dependencies/abstractions, but never omit trust-boundary validation, data-loss handling, security, accessibility, required tests, or requested functionality. Give concise progress checkpoints and end reports with what was not checked and material risk.

For user-facing questions in the current Hermes/Superpowers workflow, use `clarify` rather than a plain-text question; ask one question per call under the active question gate. In another agent environment, obtain equivalent explicit approvals using its available interaction mechanism.

## 14. Evidence provenance and limitations

- User-confirmed facts are listed in Section 2. Proposed design choices are explicitly labelled elsewhere.
- Repository files, commit IDs, and the matching remote main were verified through real Git/filesystem commands at the stated snapshot time.
- Provider/NDPC claims below come from primary pages fetched during this conversation, with verbatim evidence verified against saved page text. They are snapshots, not an account configuration audit or a promise that terms remain unchanged.
- Initial Groq model/rate/billing extracts were silently cropped near the end of the content despite a larger requested character budget. Full live HTML was fetched and parsed with the standard-library HTML parser for the relevant context. Do not rely on a successful extractor status or an unlabeled table fragment as proof of tier/eligibility.
- The optional raw research cache is `/home/ubuntu/.hermes/cache/scratch/medopsis-chat.GYLVWd/`, including `ledger.json`. Scratch/cache data may be pruned; this handoff includes source URLs and evidence so it is not dependent on that cache for understanding.
- No project dependency installs, source-code implementation, LLM inference, real-patient-data calls, paid upgrades, deployment, or GitHub writes were performed in this session. This local handoff is the documentation artifact being delivered.

**Bottom line:** the next agent inherits confirmed chat requirements and a researched proposal, not a working application or an approved design. Obtain approval, settle the integration/clinical/data-handling boundaries, implement the smallest complete chat feature, and verify it with real execution before claiming it works.

## Sources

[1] https://ndpc.gov.ng/faqs — FAQs – Nigeria Data Protection Commission
    > "Sections 41-43 (Part VIII) of the NDP Act, addresses transfer of personal data to a foreign country. To comply with the provision and other aspects of the Act, the Data Controller or Data Processor is under legal obligation to ensure that there is adequate level of protection of the personal data being transferred."
[4] https://console.groq.com/docs/your-data — Your Data in GroqCloud - GroqDocs
    > "All customers may enable Zero Data Retention (ZDR) in [Data Controls settings](https://console.groq.com/settings/data-controls).
When ZDR is enabled, Groq will not retain customer data for system reliability and abuse monitoring. As noted above, this also means that features that rely on data retention to function will be disabled. Organization admins can decide to enable ZDR globally or on a per-feature basis at any time on the Data Controls page in [Data Controls settings](https://console.groq.com/settings/data-controls)."
    > "All customer data is retained in Google Cloud Platform (GCP) buckets located in the United States. Groq maintains strict access controls and security standards as detailed in the [Groq Trust Center](https://trust.groq.com/). Where applicable, Customers can rely on standard contractual clauses (SCCs) for transfers between third countries and the U.S."
[7] https://ai.google.dev/gemini-api/terms — ai.google.dev/gemini-api/terms
    > "To help with quality and improve our products, human reviewers may read,annotate, and process your API input and output. Google takes steps to protectyour privacy as part of this process. This includes disconnecting this data fromyour Google Account, API key, and Cloud project before reviewers see or annotateit. **Do not submit sensitive, confidential, or personal information to theUnpaid Services.**"
[13] https://console.groq.com/docs/legal/ai-policy — Groq Acceptable Use & Responsible AI Policy - GroqDocs
    > "Customer and its Authorized Users are responsible for all decisions made, advice given, actions taken, and failures to take action based on the use of the Cloud Services and AI Model Services. AI Model Services use artificial intelligence and machine learning models that generate outputs, which may be inaccurate. Outputs should be evaluated for accuracy and appropriateness. If you use the AI Model Services to make consequential decisions, you must evaluate the potential risks of your use case and implement appropriate human oversight, testing, and other use case-specific safeguards to mitigate such risks. Customer is responsible for compliance with any laws, rules, and regulations applicable to its use of the Cloud Services and AI Model Services, including laws specific to artificial intelligence such as the EU AI Act."
[14] https://console.groq.com/docs/models — Supported Models - GroqDocs
    > "GPT OSS 120B
openai/gpt-oss-120b
500
$0.15 input$0.60 output
250K TPM1K RPM
131,072
65,536
-"
    > "Production Models
Note: Production models are intended for use in your production environments. They meet or exceed our high standards for speed, quality, and reliability. Read more here.
MODEL ID
SPEED
(T/SEC)
PRICE PER
1M TOKENS
RATE LIMITS
(DEVELOPER PLAN)
CONTEXT WINDOW
(TOKENS)
MAX
COMPLETION TOKENS
MAX FILE
SIZE
Llama 3.1 8BEnterprise
llama-3.1-8b-instant
560
ContactSales
ContactSales
131,072
131,072
-
Llama 3.3 70BEnterprise
llama-3.3-70b-versatile
280
ContactSales
ContactSales
131,072
32,768
-
GPT OSS 120B
openai/gpt-oss-120b
500
$0.15 input$0.60 output
250K TPM1K RPM
131,072
65,536
-
GPT OSS 20B
openai/gpt-oss-20b
1000
$0.075 input$0.30 output
250K TPM1K RPM
131,072
65,536
-
Whisper
whisper-large-v3
-
$0.111 per hour
200K ASH300 RPM
-
-
100 MB
Whisper Large V3 Turbo
whisper-large-v3-turbo
-
$0.04 per hour
400K ASH400 RPM
-
-
100 MB"
[15] https://console.groq.com/docs/rate-limits — Rate Limits - GroqDocs
    > "openai/gpt-oss-120b
30
1K
8K
200K
-
-"
    > "Rate limits apply at the organization level, not individual users. You can hit any limit type depending on which threshold you reach first."
[17] https://console.groq.com/docs/billing-faqs — Billing FAQs - GroqDocs
    > "When you upgrade, there's no immediate charge - you'll be billed for tokens at month-end or when you reach progressive billing thresholds (see below for details).
To upgrade from the Free tier to the Developer tier, you'll need to provide a valid payment method (credit card, US bank account, or SEPA debit account).
Your upgrade takes effect immediately, but billing only occurs at the end of your monthly billing cycle or when you cross progressive thresholds ($1, $10, $100, $500, $1,000; see below for details)."
