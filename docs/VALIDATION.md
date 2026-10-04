# Validation status

- Build environment: Python 3.12, Node 24.19.0, pytest 9.1.1.
- 37 offline/export/report tests passed.
- 32 opt-in real-webhook tests skipped because no n8n endpoint was configured.
- Offline report: 32 PASS, 0 FAIL, 0 ERROR.
- Actual n8n 2.40.5 import and publication verified locally.
- All 32 webhook integration tests passed.
- Webhook evaluation: 32 PASS, 0 FAIL, 0 ERROR.
- No real LLM requests, payments or external ticket operations.

Update this file with observed integration results after local testing; do not treat offline results as n8n runtime evidence.
