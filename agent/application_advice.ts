import {assertProvider,cloudAdvicePayload,openrouterAdvicePayload} from "./provider_policy.ts";
import type {ExtensionAPI} from '@earendil-works/pi-coding-agent';

// Deliberately separate from the essay-writing skill: this stage writes advice
// only. Source statements, headings, labels and citations belong to the server.
export default function(pi:ExtensionAPI){
 const output=Number(process.env.LENNY_ADVICE_OUTPUT_TOKENS||256);
 if(![256,384].includes(output))throw new Error("unapproved advice output budget");
 let requests=0;
 pi.on('session_start',()=>{requests=0;pi.setActiveTools([]);console.error(JSON.stringify({event:'tool_policy',active:pi.getActiveTools(),mode:'application_advice_only'}));});
 pi.on('tool_call',()=>({block:true,reason:'No tools in advice-only stage'}));
 pi.on('before_provider_request',(event,ctx)=>{
  const provider=assertProvider(ctx.model);
  if(++requests>1)throw new Error('single request required');
  const payload=event.payload as Record<string,unknown>;
  const messages=(payload.messages as any[]).map(m=>({...m}));
  const system=messages.find(m=>m.role==='system'||m.role==='developer');
  if(!system&&provider!=='anthropic-cloud')throw new Error('missing system message');
  const instruction='Write one paragraph of proposed advice, following the requested word count. Propose an experiment, a metric to track and a decision after reviewing data. Expected improvements must be explicitly framed as hypotheses to test, never established effects. No historical or general factual assertions, case restatement, guarantees or promised outcomes. No preamble, headings, labels, lists, citations, IDs, JSON, code fences or tools. /no_think';
  if(provider==='openrouter')return openrouterAdvicePayload(payload,instruction,output);
  if(provider==='anthropic-cloud')return cloudAdvicePayload(payload,instruction,output);
  system.content=instruction;
  const bytes=Buffer.byteLength(JSON.stringify(messages),'utf8');
  if(bytes>4000)throw new Error('advice context exhausted');
  const result={...payload,messages,temperature:0,reasoning_effort:'none',max_tokens:output,tool_choice:'none'} as Record<string,unknown>;
  delete result.response_format;delete result.grammar;delete result.format;
  console.error(JSON.stringify({event:'provider_request',provider:ctx.model.provider,model:ctx.model.id,prompt_bytes:bytes,max_tokens:output,structured_grammar:false,mode:'application_advice_only'}));
  return result;
 });
}
