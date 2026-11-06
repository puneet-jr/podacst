// Compatibility adapter for a narrowly validated model-written tool request.
// Never interprets source/tool-result text or a final answer as an instruction.
export function normalizeToolRequest(message:any, requests:number, calls:number) {
  if (requests !== 1 || calls !== 0 || message.role !== 'assistant' || message.stopReason !== 'stop') return;
  if (!Array.isArray(message.content) || message.content.length !== 1 || message.content[0].type !== 'text') return;
  const raw = message.content[0].text;
  if (typeof raw !== 'string' || raw.length > 250) return;
  let value:any;
  try { value=JSON.parse(raw); } catch { return; }
  if (!value || Array.isArray(value) || Object.keys(value).sort().join(',') !== 'arguments,name' || value.name !== 'search_transcripts') return;
  const args=value.arguments;
  if (!args || Array.isArray(args) || Object.keys(args).join(',') !== 'query' || args.query !== 'current') return;
  return {raw, message:{...message,stopReason:'toolUse',content:[{type:'toolCall',id:'normalized_'+crypto.randomUUID().replaceAll('-',''),name:'search_transcripts',arguments:{query:'current'}}]}};
}
