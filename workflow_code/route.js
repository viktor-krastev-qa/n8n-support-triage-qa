const item = $input.first().json;
if (item.ready) return [{json:item}];
if (item.provider_error) return [{json:{ready:true,http_status:503,response:{ok:false,error:'classifier_unavailable',ticket_id:item.ticket.ticket_id}}}];
let output;
try { output = JSON.parse(item.raw_output); } catch { output = null; }
const valid = output && typeof output === 'object' && !Array.isArray(output)
  && Object.keys(output).sort().join(',') === 'category,confidence,priority'
  && ['billing','technical','shipping','general'].includes(output.category)
  && ['high','normal'].includes(output.priority)
  && typeof output.confidence === 'number' && Number.isFinite(output.confidence)
  && output.confidence >= 0 && output.confidence <= 1;
if (!valid) return [{json:{ready:true,http_status:502,response:{ok:false,error:'invalid_classifier_output',ticket_id:item.ticket.ticket_id}}}];
const routes = {billing:'billing_queue',technical:'technical_queue',shipping:'shipping_queue',general:'manual_review'};
const queue = output.confidence < 0.7 ? 'manual_review' : routes[output.category];
return [{json:{ready:true,http_status:200,response:{ok:true,ticket_id:item.ticket.ticket_id,category:output.category,priority:output.priority,queue,confidence:output.confidence,classification_source:'deterministic_stub'}}}];
