const item = $input.first().json;
if (item.ready) return [{json:item}];
if (item.simulate === 'unavailable') return [{json:{...item,provider_error:'simulated_unavailable'}}];
if (item.simulate === 'invalid_json') return [{json:{...item,raw_output:'not-json'}}];
const text = item.ticket.message.toLowerCase();
// Deterministic stub, not an AI model. Mixed categories use explicit precedence.
let category = 'general';
if (/\b(refund|invoice|payment|charged)\b/.test(text)) category = 'billing';
else if (/\b(error|crash|login|password)\b/.test(text)) category = 'technical';
else if (/\b(shipping|delivery|parcel|tracking)\b/.test(text)) category = 'shipping';
const priority = /\b(urgent|immediately)\b/.test(text) ? 'high' : 'normal';
const confidence = category === 'general' ? 0.4 : 0.9;
const output = {category,priority,confidence};
if (item.simulate === 'invalid_label') output.category = 'admin';
if (item.simulate === 'invalid_confidence') output.confidence = 5;
return [{json:{...item,raw_output:JSON.stringify(output)}}];
