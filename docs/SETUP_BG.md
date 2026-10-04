# Настройка в съществуващия n8n Docker

Копирай ZIP съдържанието в E:\GitHub\n8n-support-triage-qa, запазвайки .git и LICENSE. Не променяй Docker контейнера и не създавай друг.

1. Отвори проекта в Cursor. Провери node --version. Docker има Node вътре, но за offline тестовете Node трябва да е достъпен и в Windows терминала. Ако командата липсва, спри и уточни инсталацията с нас.
2. Създай/активирай .venv и инсталирай requirements.txt според README.
3. Отвори http://localhost:5678. Създай workflow и от менюто с три точки избери Import from File.
4. Импортирай workflows/support-triage.json. Запази и Publish/Activate според видимия интерфейс.
5. Повтори за workflows/support-triage-faults.json като отделен workflow.
6. Провери Webhook: POST, path support-triage-qa (или support-triage-qa-faults), Respond Using Respond to Webhook Node.
7. Използвай /webhook/ URL за целия test suite, а не /webhook-test/.
8. Изпълни примерната Invoke-RestMethod заявка от README. След това integration тестовете.

HTTP 404 обикновено означава непубликуван workflow или грешен path. HTTP 200 с текст Workflow got started означава неправилен Webhook response mode. При ERROR прегледай n8n execution и точния резултат; не го записвай като успешно тестван.

Преди commit настрой user.name, user.email (точния noreply адрес) и GitHub credential username за това repository. .venv и reports са игнорирани. След потвърден реален run добавяме evidence в README.
