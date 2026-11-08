// Offline installed-Pi serializer probe. Synthetic history; never an actual saved payload.
import assert from 'node:assert/strict';
import {writeFileSync} from 'node:fs';
import {stream} from '../spike/node_modules/@earendil-works/pi-ai/dist/api/openai-completions.js';
import {normalizeContext} from '../spike/node_modules/@earendil-works/pi-ai/dist/utils/transcript.js';
import {openrouterConversationPayload} from '../agent/provider_policy.ts';
const label=process.argv[2]||'original';
assert.ok(['original','fixed'].includes(label));
const model={id:'google/gemini-2.5-flash-lite',name:'Synthetic serializer probe',api:'openai-completions',provider:'openrouter',baseUrl:'https://openrouter.ai/api/v1',reasoning:false,input:['text'],contextWindow:4096,maxTokens:128,cost:{input:0,output:0,cacheRead:0,cacheWrite:0}};
const tool={name:'search_transcripts',description:'Synthetic fixture only',parameters:{type:'object',properties:{query:{type:'string'}},required:['query'],additionalProperties:false}};
const user={role:'user',content:'Synthetic question, not a source passage.',timestamp:1};
const assistant={role:'assistant',content:[{type:'toolCall',id:'fixture-call',name:tool.name,arguments:{query:'current'}}],api:model.api,provider:model.provider,model:model.id,stopReason:'toolUse',timestamp:2,usage:{input:0,output:0,cacheRead:0,cacheWrite:0,totalTokens:0,cost:{input:0,output:0,cacheRead:0,cacheWrite:0,total:0}}};
const result={role:'toolResult',toolCallId:'fixture-call',toolName:tool.name,content:[{type:'text',text:JSON.stringify({items:[{id:'E1',text:'Synthetic evidence, not real transcript.'}]})}],isError:false,timestamp:3};
let fetches=0;const observations=[];
for(const turn of [1,2]){
 const context=normalizeContext({systemPrompt:'Synthetic system instruction.',tools:[tool],messages:turn===1?[user]:[user,assistant,result]});
 let captured=false;
 const output=stream(model,context,{apiKey:'synthetic-not-a-key',maxTokens:128,maxRetries:0,fetch:async()=>{fetches++;throw new Error('NETWORK_FORBIDDEN');},onPayload:payload=>{
  const shaped=openrouterConversationPayload(payload,turn,['E1'],'Synthetic question');captured=true;
  const call=shaped.messages.find(m=>m.role==='assistant'&&m.tool_calls)?.tool_calls[0];const response=shaped.messages.find(m=>m.role==='tool');
  observations.push({turn,model:shaped.model,max_tokens:shaped.max_tokens,temperature:shaped.temperature,stream:shaped.stream,stream_options:shaped.stream_options,tool_choice:shaped.tool_choice,response_format:shaped.response_format??null,routing:shaped.provider,tools_count:shaped.tools?.length??0,message_roles:shaped.messages.map(m=>m.role),tool_call_function_name:call?.function?.name??null,function_arguments_are_json_string:call?typeof call.function.arguments==='string'&&JSON.parse(call.function.arguments).query==='current':null,tool_result_role:response?.role??null,tool_result_content_is_string:response?typeof response.content==='string':null,tool_result_is_json:response?!!JSON.parse(response.content).items:null,tool_call_result_ids_match:call?call.id===response?.tool_call_id:null});
  throw new Error('OFFLINE_CAPTURE_COMPLETE');
 }});
 await output.result();assert.ok(captured);
}
assert.equal(fetches,0);
const report={label,installed_pi_ai_version:'1.5.0',synthetic_history:true,real_historical_payload:false,provider_requests:0,fetch_calls:fetches,observations,limits:'Exact installed serializer and current extension transformation with synthetic messages. Historical tool IDs, payload and upstream error body were not saved and cannot be recovered by this probe.'};
writeFileSync(`docs/agent-transcripts/phase-09/openrouter-sdk-offline-${label}.json`,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
