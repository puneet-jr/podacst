// Offline wire probe for the installed Pi serializer and running extension.
// All model/bridge fetches are synthetic; no credential/header/payload logging.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import extension from '/app/agent/conversation.ts';
import {stream} from '/app/agent/node_modules/@earendil-works/pi-ai/dist/api/openai-completions.js';
import {normalizeContext} from '/app/agent/node_modules/@earendil-works/pi-ai/dist/utils/transcript.js';
const observations=[];let stubbedRequests=0,stubbedBridges=0;
for(const [provider,id,baseUrl,wanted] of [
 ['openrouter','openai/gpt-oss-120b','https://openrouter.ai/api/v1',1024],
 ['openrouter','google/gemini-2.5-flash-lite','https://openrouter.ai/api/v1',128],
 ['ollama-local','qwen3:0.6b','http://host.docker.internal:11434/v1',128],
]){
 const handlers={};let tool;
 process.env.LENNY_PROVIDER=provider;process.env.LENNY_PROVIDER_BASE=baseUrl;process.env.LENNY_OLLAMA_BASE_URL=baseUrl;
 process.env.LENNY_CHAT_BRIDGE='http://127.0.0.1:9/search';process.env.LENNY_CHAT_TOKEN='synthetic-operation-token';process.env.LENNY_CHAT_QUESTION='Synthetic fixture question';
 extension({registerTool:t=>{tool=t},on:(event,handler)=>{handlers[event]=handler},setActiveTools:()=>{},getActiveTools:()=>['search_transcripts']});handlers.session_start();
 const model={id,name:'Offline wire probe',api:'openai-completions',provider,baseUrl,reasoning:false,input:['text'],contextWindow:4096,maxTokens:128,cost:{input:0,output:0,cacheRead:0,cacheWrite:0}};
 let turn=1;
 const fakeFetch=async(input,init)=>{
  const req=new Request(input,init);
  if(req.url==='http://127.0.0.1:9/search'){
   stubbedBridges++;return Response.json({items:[{id:'E1',text:'Synthetic fixture evidence;no public transcript payload.'}]});
  }
  assert.ok(req.url.startsWith(baseUrl+'/chat/completions'),'Unexpected endpoint blocked');
  const body=JSON.parse(await req.text());stubbedRequests++;
  assert.equal(body.max_tokens,turn===1?128:wanted);assert.equal(body.model,id);
  if(provider==='openrouter')assert.equal(body.max_completion_tokens,undefined);
  else if(body.max_completion_tokens!==undefined)assert.equal(body.max_completion_tokens,128);
  const call=body.messages.find(m=>m.role==='assistant'&&m.tool_calls)?.tool_calls[0];const result=body.messages.find(m=>m.role==='tool');
  if(turn===2){assert.ok(call&&result);assert.equal(call.id,result.tool_call_id)}
  if(provider==='openrouter'){assert.equal(body.provider.only,undefined);assert.equal(body.provider.allow_fallbacks,false)}
  observations.push({provider,model:id,turn,serialized_max_tokens:body.max_tokens,serialized_max_completion_tokens:body.max_completion_tokens??null,tool_result_ids_match:turn===2?call.id===result.tool_call_id:null,only_omitted:body.provider?.only===undefined});
  const chunks=turn===1?[
   {id:'synthetic-response',choices:[{index:0,delta:{role:'assistant',tool_calls:[{index:0,id:'synthetic-call',type:'function',function:{name:'search_transcripts',arguments:'{"query":"current"}'}}]},finish_reason:null}]},
   {id:'synthetic-response',choices:[{index:0,delta:{},finish_reason:'tool_calls'}],usage:{prompt_tokens:10,completion_tokens:10,total_tokens:20}},
  ]:[
   {id:'synthetic-response',choices:[{index:0,delta:{role:'assistant',content:'{"evidence_id":"E1"}'},finish_reason:null}]},
   {id:'synthetic-response',choices:[{index:0,delta:{},finish_reason:'stop'}],usage:{prompt_tokens:10,completion_tokens:10,total_tokens:20}},
  ];
  return new Response(chunks.map(x=>'data: '+JSON.stringify(x)+'\n\n').join('')+'data: [DONE]\n\n',{status:200,headers:{'Content-Type':'text/event-stream'}});
 };
 globalThis.fetch=fakeFetch;
 const messages=[{role:'user',content:'Synthetic fixture question',timestamp:1}];
 const run=()=>stream(model,normalizeContext({systemPrompt:'Synthetic system',tools:[{name:tool.name,description:tool.description,parameters:tool.parameters}],messages}),{apiKey:'synthetic-not-a-key',maxTokens:128,maxRetries:0,fetch:fakeFetch,onPayload:payload=>handlers.before_provider_request({payload},{model})}).result();
 const first=await run();assert.equal(first.stopReason,'toolUse');const call=first.content.find(b=>b.type==='toolCall');assert.ok(call);
 const result=await tool.execute(call.id,{query:'current'},new AbortController().signal);
 messages.push(first,{role:'toolResult',toolCallId:call.id,toolName:'search_transcripts',content:result.content,isError:false,timestamp:3});turn=2;
 const final=await run();assert.equal(final.stopReason,'stop');assert.ok(final.content.some(b=>b.type==='text'));
}
const sha=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
console.log(JSON.stringify({fixture:true,actual_network_requests:0,stubbed_wire_requests:stubbedRequests,stubbed_bridge_requests:stubbedBridges,actual_installed_serializer:true,actual_extension_hook:true,observations,provider_policy_sha256:sha('/app/agent/provider_policy.ts'),conversation_extension_sha256:sha('/app/agent/conversation.ts')}));
