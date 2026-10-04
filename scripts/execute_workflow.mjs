import fs from 'node:fs';
// Execute the exact embedded n8n Code-node bodies, not a Python reimplementation.
// n8n runtime/webhook/expressions are not emulated; integration tests cover those.
const payload = JSON.parse(fs.readFileSync(0,'utf8'));
const workflow = JSON.parse(fs.readFileSync(payload.workflow,'utf8'));
const AsyncFunction = Object.getPrototypeOf(async function(){}).constructor;
let items = [{json:{body:payload.body}}];
for (const node of workflow.nodes) {
  if (node.type !== 'n8n-nodes-base.code') continue;
  const input = {first:()=>items[0],all:()=>items};
  items = await new AsyncFunction('$input',node.parameters.jsCode)(input);
  if (!Array.isArray(items) || !items[0]?.json) throw new Error('Invalid Code node output');
}
process.stdout.write(JSON.stringify(items[0].json));
