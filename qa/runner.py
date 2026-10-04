import argparse
from datetime import datetime, timezone
import html
import json
from pathlib import Path
import subprocess
from urllib.request import Request, urlopen
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
CASES = json.loads((ROOT / "data/cases.json").read_text(encoding="utf-8"))


def offline(case):
    name = "support-triage-faults.json" if case["workflow"] == "faults" else "support-triage.json"
    data = {"workflow":str(ROOT / "workflows" / name),"body":case["body"]}
    result = subprocess.run(["node",str(ROOT / "scripts/execute_workflow.mjs")],input=json.dumps(data),
                            text=True,capture_output=True,check=True,timeout=10)
    output = json.loads(result.stdout)
    return output["http_status"],output["response"]


def webhook(case, base_url):
    path = "support-triage-qa-faults" if case["workflow"] == "faults" else "support-triage-qa"
    request = Request(base_url.rstrip('/') + '/' + path, data=json.dumps(case["body"]).encode(),
                      headers={"Content-Type":"application/json"},method="POST")
    try:
        with urlopen(request,timeout=15) as response:
            return response.status,json.loads(response.read())
    except HTTPError as response:
        return response.code,json.loads(response.read())


def check(case, status, body):
    checks = [{"name":"http_status","passed":status == case["expected_status"],
               "actual":status,"expected":case["expected_status"]}]
    if not isinstance(body,dict):
        return checks + [{"name":"object_response","passed":False,"actual":body,"expected":"object"}]
    for key,value in case["expected"].items():
        checks.append({"name":key,"passed":body.get(key) == value,"actual":body.get(key),"expected":value})
    if status == 200:
        checks.append({"name":"source","passed":body.get("classification_source") == "deterministic_stub"})
        checks.append({"name":"ticket_id","passed":body.get("ticket_id") == case["body"]["ticket_id"]})
        checks.append({"name":"no_personal_input_echo","passed":"email" not in body and "message" not in body})
    return checks


def run_suite(mode="offline",base_url="http://localhost:5678/webhook"):
    rows = []
    for case in CASES:
        try:
            status,body = offline(case) if mode == "offline" else webhook(case,base_url)
            checks = check(case,status,body)
            outcome = "PASS" if all(c["passed"] for c in checks) else "FAIL"
            error = None
        except Exception as exc:
            status,body,checks,outcome,error = None,None,[],"ERROR",type(exc).__name__
        rows.append({"id":case["id"],"workflow":case["workflow"],"http_status":status,
                     "response":body,"checks":checks,"status":outcome,"error":error})
    return {"created_utc":datetime.now(timezone.utc).isoformat(),"mode":mode,"results":rows,
            "summary":{"total":len(rows),**{s.lower():sum(r["status"]==s for r in rows) for s in ("PASS","FAIL","ERROR")}}}


def write_report(report,output):
    output = Path(output);output.mkdir(parents=True,exist_ok=True)
    (output / "report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    page = """<!doctype html><html lang="en"><meta charset="utf-8"><title>Support triage QA</title>
<style>body{font:16px system-ui;margin:30px}table{border-collapse:collapse;width:100%}th,td{padding:10px;border:1px solid #ccd;text-align:left;vertical-align:top}td{white-space:pre-wrap}th{background:#e9eef7}</style>
<h1>n8n Support Triage QA</h1><p>Deterministic classifier simulation. Offline mode executes Code-node logic only; webhook mode tests the actual n8n endpoint.</p>"""
    page += '<pre>' + html.escape(json.dumps({"mode":report["mode"],"summary":report["summary"]},indent=2)) + '</pre>'
    page += '<table><tr><th>Case</th><th>Status</th><th>HTTP</th><th>Response</th><th>Failures / errors</th></tr>'
    for row in report["results"]:
        values = [row["id"],row["status"],row["http_status"],json.dumps(row["response"],indent=2),json.dumps([c for c in row["checks"] if not c["passed"]],indent=2) if not row["error"] else row["error"]]
        page += '<tr>' + ''.join('<td>'+html.escape(str(v))+'</td>' for v in values) + '</tr>'
    (output / "report.html").write_text(page+'</table></html>',encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode',choices=['offline','webhook'],default='offline')
    parser.add_argument('--base-url',default='http://localhost:5678/webhook')
    parser.add_argument('--output',default='reports/offline')
    args = parser.parse_args()
    report = run_suite(args.mode,args.base_url)
    write_report(report,args.output)
    print(json.dumps(report['summary']))
    print(f"Report: {Path(args.output) / 'report.html'}")
    return int(bool(report['summary']['fail'] or report['summary']['error']))


if __name__ == '__main__':
    raise SystemExit(main())
