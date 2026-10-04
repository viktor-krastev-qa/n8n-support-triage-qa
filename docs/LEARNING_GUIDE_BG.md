# Разбор на проекта

1. Webhook приема HTTP POST; примерен вход е data/sample-ticket.json.
2. Validate Input проверява типове и полета; невалиден вход връща 400.
3. Simulated Classifier е keyword stub, не AI. Позволява ни да тестваме без платени заявки.
4. Validate Output and Route проверява JSON/schema и връща queue. Не изпраща към реална система.
5. Respond to Webhook определя истинските HTTP status и response body в n8n.
6. Offline тестовете изпълняват само Code логиката в Node. Integration тестовете проверяват целия n8n endpoint.
7. Fault workflow показва 502/503; тези грешки са симулирани.

Обяснение за интервю: „Създадох n8n workflow за support triage с input и classifier-output validation. Използвах deterministic stub, за да тествам договора без API разходи, и отделих offline тестовете от истинските webhook integration тестове.“
