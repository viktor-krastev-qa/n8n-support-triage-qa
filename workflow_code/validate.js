const input = $input.first().json;
const b = input.body;
const errors = [];
const isObject = b !== null && typeof b === 'object' && !Array.isArray(b);
if (!isObject) errors.push('body_must_be_object');
if (isObject) {
  const allowed = ['ticket_id','email','message'];
  if (TEST_MODE) allowed.push('simulate');
  if (Object.keys(b).some(k => !allowed.includes(k))) errors.push('unknown_field');
  if (typeof b.ticket_id !== 'string' || !/^TKT-[0-9]{3}$/.test(b.ticket_id)) errors.push('invalid_ticket_id');
  if (typeof b.email !== 'string' || b.email.length > 254 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(b.email)) errors.push('invalid_email');
  if (typeof b.message !== 'string' || b.message.trim().length < 10 || b.message.trim().length > 2000) errors.push('invalid_message');
  if (TEST_MODE && b.simulate !== undefined && !['normal','unavailable','invalid_json','invalid_label','invalid_confidence'].includes(b.simulate)) errors.push('invalid_simulation');
}
if (errors.length) return [{json:{ready:true,http_status:400,response:{ok:false,error:'validation_error',details:errors}}}];
return [{json:{ready:false,ticket:{ticket_id:b.ticket_id,email:b.email.trim().toLowerCase(),message:b.message.trim()},simulate:TEST_MODE ? (b.simulate || 'normal') : 'normal'}}];
