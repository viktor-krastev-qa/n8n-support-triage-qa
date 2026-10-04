import os
import pytest
from qa.runner import CASES, webhook, check

URL = os.environ.get('N8N_WEBHOOK_BASE')


@pytest.mark.integration
@pytest.mark.skipif(not URL,reason='Set N8N_WEBHOOK_BASE after importing and publishing both workflows')
@pytest.mark.parametrize('case',CASES,ids=lambda c:c['id'])
def test_real_n8n_webhook(case):
    status,body = webhook(case,URL)
    assert all(c['passed'] for c in check(case,status,body)), (status,body)
