# Qwen live smoke-test evidence

Model: qwen/qwen3.8-27b through Groq. The user authorized the saved default-profile key and confirmed Free-tier access; billing/account controls were not independently audited. No key was displayed, copied into the repository, or included in prompts. No billing/data-control settings were changed.

The actual POST /chat route, JWT signature validation, request validation, reference loader, provider client, and output validator ran. Signing-key retrieval used a synthetic controlled key; references came from the explicitly synthetic software-test fixture, not a real clinical approval.

Server-side JSON-schema modes produced json_validate_failed/malformed output. JSON object mode plus explicit untranslated field-name instructions passed the local strict output and reference checks. Invalid output is still rejected; no parser repair or automatic retry was added.

## Verified requests

| Requested language | App HTTP | Provider HTTP |
| --- | --- | --- |
| English (en) | 200 | 200 |
| Yoruba (yo) | 200 | 200 |
| Igbo (ig) | 200 | 200 |
| Hausa (ha) | 200 | 200 |

All inputs/reports were synthetic and nonclinical. These checks prove mechanical integration only. Generated language meaning/fluency and clinical safety have NOT been reviewed by native speakers or clinicians; non-English outputs are unreviewed, not proof of usable translations. No patient use, live app identity integration, or legal/data-governance approval is established. App consent, report association, protected SQLite history and applicable provider controls remain external gates.

Raw synthetic outputs and usage evidence were saved in /home/ubuntu/.hermes/cache/scratch/medopsis-qwen-json-results.json and the individual medopsis-qwen-json-en.json, medopsis-qwen-json-yo.json, medopsis-qwen-json-ig.json and medopsis-qwen-json-ha.json files in that same directory. The final documentation checkpoint programmatically checked exactly these four cases, their model/app/provider statuses, aggregate/individual equality, response shape and synthetic reference metadata without further inference. Scratch may be pruned; this summary records the observed statuses without exposing credentials.
