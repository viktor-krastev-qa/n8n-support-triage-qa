# Test strategy
Three distinct layers: workflow export structure, execution of embedded Code-node logic, and real n8n HTTP contracts. CI covers the first two; local opt-in integration verifies runtime expressions, Webhook parsing, response status and JSON serialization.

Risk coverage: wrong category/route, missing fields, incorrect types, extra user-controlled fields, trimmed message boundaries, word boundaries, conflicting keywords, unavailable classifier and invalid provider output. The fault workflow isolates injected failure controls from the main workflow.

All expected outputs are curated for a deterministic stub. PASS percentages describe contract conformance, not model quality. No side effects beyond workflow execution history occur. Review n8n executions and actual response bodies before recording integration success.
