import json
from pathlib import Path
import pytest
from qa.runner import CASES, ROOT, offline, check, write_report
from scripts.build_workflows import build


@pytest.mark.parametrize('case',CASES,ids=lambda c:c['id'])
def test_embedded_code_contract(case):
    status,body = offline(case)
    assert all(c['passed'] for c in check(case,status,body)), (status,body)


@pytest.mark.parametrize('fault,name',[(False,'support-triage.json'),(True,'support-triage-faults.json')])
def test_export_matches_source(fault,name):
    assert json.loads((ROOT / 'workflows' / name).read_text()) == build(fault)


def test_workflow_has_response_node_and_connections():
    workflow = build()
    assert workflow['nodes'][0]['parameters']['responseMode'] == 'responseNode'
    assert workflow['nodes'][-1]['parameters']['options']['responseCode'] == '={{ $json.http_status }}'
    for a,b in zip(workflow['nodes'],workflow['nodes'][1:]):
        assert workflow['connections'][a['name']]['main'][0][0]['node'] == b['name']


def test_checker_detects_wrong_route():
    case = CASES[0]
    assert not all(c['passed'] for c in check(case,200,{'category':'billing','queue':'admin'}))


def test_html_escapes_output(tmp_path):
    report = {'mode':'offline','summary':{'total':1},'results':[{'id':'<script>','status':'FAIL','http_status':200,'response':{},'checks':[],'error':None}]}
    write_report(report,tmp_path)
    page = (tmp_path/'report.html').read_text()
    assert '<script>' not in page and '&lt;script&gt;' in page
