import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def build(test_mode=False):
    prefix = "support-triage-qa-faults" if test_mode else "support-triage-qa"
    nodes = [{"parameters":{"httpMethod":"POST","path":prefix,"responseMode":"responseNode","options":{}},
              "id":"webhook","name":"Support Webhook","type":"n8n-nodes-base.webhook","typeVersion":2,
              "position":[0,0],"webhookId":prefix}]
    for index, (file, name) in enumerate([( "validate", "Validate Input"),("simulate","Simulated Classifier"),("route","Validate Output and Route")],1):
        code = (ROOT / f"workflow_code/{file}.js").read_text(encoding="utf-8")
        if file == "validate":
            code = "const TEST_MODE = " + ("true" if test_mode else "false") + ";\n" + code
        nodes.append({"parameters":{"mode":"runOnceForAllItems","jsCode":code},"id":file,"name":name,
                      "type":"n8n-nodes-base.code","typeVersion":2,"position":[index*260,0]})
    nodes.append({"parameters":{"respondWith":"json","responseBody":"={{ $json.response }}",
                                "options":{"responseCode":"={{ $json.http_status }}"}},
                  "id":"respond","name":"Respond to Webhook","type":"n8n-nodes-base.respondToWebhook",
                  "typeVersion":1.4,"position":[1040,0]})
    connections = {a["name"]:{"main":[[{"node":b["name"],"type":"main","index":0}]]} for a,b in zip(nodes,nodes[1:])}
    return {"name":"Support Triage QA" + (" - Fault Injection" if test_mode else ""),
            "nodes":nodes,"connections":connections,"settings":{"executionOrder":"v1"},
            "active":False,"pinData":{},"tags":[]}


if __name__ == "__main__":
    for fault, filename in [(False,"support-triage.json"),(True,"support-triage-faults.json")]:
        path = ROOT / "workflows" / filename
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(build(fault),indent=2),encoding="utf-8")
        print(path)
