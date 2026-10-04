# n8n Support Triage + QA

A local n8n portfolio workflow with strict input validation, a deterministic classifier stub, classifier-output validation and queue assignment. It includes executable Code-node tests and opt-in API contract tests against real n8n webhooks.

**No LLM, API key or payment is required.** Queue assignment is returned as data; no ticket, email, Slack message or external queue entry is created. Validated locally with n8n 2.40.5 running in Docker: both workflows imported and published successfully, and all 32 webhook integration tests passed.

## Workflow
POST Webhook -> Validate Input -> Simulated Classifier -> Validate Output and Route -> Respond to Webhook.
Invalid input bypasses classification using a response envelope. Billing takes precedence over technical, then shipping. Unmatched messages receive confidence 0.4 and manual_review. Keyword recognition is deliberately limited and is not measured AI accuracy.

## Setup
Requirements: existing local n8n at localhost:5678, Python 3.13 and Node.js 22 or newer available in PATH.
```powershell
git clone https://github.com/viktor-krastev-qa/n8n-support-triage-qa.git
cd n8n-support-triage-qa
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
node --version
python -m pytest -v
python -m qa.runner --mode offline --output reports/offline
Start-Process reports/offline/report.html
```
If already cloned, skip the clone/cd steps. Offline tests execute the exact JavaScript embedded in workflow exports via Node, not a duplicate Python implementation. They do not execute n8n nodes, webhook handling or expressions. Integration tests are skipped until explicitly configured.

## Import into n8n
Open http://localhost:5678 and import both files from `workflows/` using Import from File. Save and publish/activate both workflows. Do not change the webhook paths. No credentials are required. See [Bulgarian setup](docs/SETUP_BG.md).

Production endpoints (workflows must be published/active):
- POST http://localhost:5678/webhook/support-triage-qa
- POST http://localhost:5678/webhook/support-triage-qa-faults

Test URLs under `/webhook-test/` require manual listening and are not intended for the full repeated test suite.

Send a sample:
```powershell
$ticket = Get-Content data/sample-ticket.json -Raw
Invoke-RestMethod -Method Post -Uri "http://localhost:5678/webhook/support-triage-qa" -ContentType "application/json" -Body $ticket
```
Run real-webhook tests and create a report:
```powershell
$env:N8N_WEBHOOK_BASE = "http://localhost:5678/webhook"
python -m pytest -m integration -v
python -m qa.runner --mode webhook --output reports/webhook
Start-Process reports/webhook/report.html
```
The integration suite makes requests only when the environment variable is set. CI runs offline code tests only; it does not assert an n8n integration pass.

## Contract
Required fields: ticket_id (TKT- plus three digits), email (basic syntax check, max 254), message (trimmed length 10..2000). Unknown fields are rejected. Only synthetic ticket data should be used in this demo.

| Status | Meaning |
|---|---|
| 200 | Classified and assigned a queue |
| 400 | Invalid request fields/body |
| 502 | Invalid classifier JSON/schema |
| 503 | Simulated classifier unavailable |

Main workflow rejects simulation controls. The separate fault workflow accepts `simulate`: normal, unavailable, invalid_json, invalid_label or invalid_confidence. These controls deterministically inject failures and do not represent real network timeouts. A real AI provider and retry/backoff behavior are future scope.

Successful output includes ticket_id, category, priority, confidence, queue and classification_source=deterministic_stub. It does not echo the email or message, though n8n execution history may retain inputs.

## Validation and reports
See [validation status](docs/VALIDATION.md). [Offline HTML report](examples/offline/report.html) (download/open) and [JSON report](examples/offline/report.json) are generated Code-node evaluations, not real webhook evidence. FAIL means a contract expectation disagreed; ERROR means a request/execution could not be evaluated. Exit code 1 indicates at least one FAIL/ERROR.

- Local offline tests: 37 passed.
- Local n8n webhook integration tests: 32 passed.
- Webhook evaluation report: 32 PASS, 0 FAIL, 0 ERROR.
- [Actual webhook HTML report](examples/webhook/report.html) — download and open.
- [Actual webhook JSON report](examples/webhook/report.json).

## Scope
The webhook is an unauthenticated local demo. This project does not add production authentication, durable queues, duplicate-ticket prevention, rate limiting or delivery guarantees. The injection-text case verifies that keyword-based routing cannot be redirected to an unsupported queue; it does not establish LLM prompt-injection resistance. Email validation is basic syntax, not deliverability. Malformed raw JSON is parsed by n8n before Code-node validation and is outside this contract corpus.

Changing workflow_code requires `python scripts/build_workflows.py` and re-importing both exports. Tests verify exports match source. All test messages are English and synthetic.

## License
MIT — see [LICENSE](LICENSE).

## References
- https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/
- https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.respondtowebhook/
- https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.code/
