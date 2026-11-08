import {test} from 'node:test';
import assert from 'node:assert/strict';
import {assertProvider,cloudConversationPayload,cloudAdvicePayload,openrouterConversationPayload,openrouterAdvicePayload} from './provider_policy.ts';
test('local boundary cannot select a cloud endpoint',()=>{
 assert.throws(()=>assertProvider({provider:'anthropic-cloud',baseUrl:'https://api.anthropic.com'},{LENNY_PROVIDER:'ollama-local',LENNY_PROVIDER_BASE:'http://localhost:11434/v1'}));
 assert.throws(()=>assertProvider({provider:'anthropic-cloud',baseUrl:'https://evil.invalid'},{LENNY_PROVIDER:'anthropic-cloud',LENNY_PROVIDER_BASE:'https://evil.invalid'}));
});
test('native Anthropic tool routing and bounded JSON selection',()=>{
 const payload={system:'original',messages:[{role:'user',content:'fixture'}]};
 const first=cloudConversationPayload(payload,1,[],'fixture');assert.deepEqual(first.tool_choice,{type:'tool',name:'search_transcripts',disable_parallel_tool_use:true});assert.equal(first.max_tokens,128);
 const next=cloudConversationPayload(payload,2,['E1'],'fixture');assert.deepEqual(next.tool_choice,{type:'none'});assert.match(next.system,/E1/);assert.match(next.system,/NONE/);assert.equal(next.messages.length,2);
 assert.throws(()=>cloudConversationPayload(payload,3,[],''));
 assert.throws(()=>cloudConversationPayload({messages:[{content:'x'.repeat(14000)}]},1,[],''));
});
test('cloud advice removes local grammar and thinking fields',()=>{
 const p=cloudAdvicePayload({messages:[],grammar:'fixture',format:'json',response_format:{},tool_choice:'none',thinking:{}},'Proposed advice. /no_think',384);
 assert.equal(p.max_tokens,384);assert.equal(p.system,'Proposed advice.');for(const k of ['grammar','format','response_format','tool_choice','thinking'])assert.equal(p[k],undefined);
});

test('OpenRouter requires its approved boundary and fixed single-model routing',()=>{
 assert.equal(assertProvider({provider:'openrouter',baseUrl:'https://openrouter.ai/api/v1'},{LENNY_PROVIDER:'openrouter',LENNY_PROVIDER_BASE:'https://openrouter.ai/api/v1'}),'openrouter');
 assert.throws(()=>assertProvider({provider:'openrouter',baseUrl:'https://evil.invalid'},{LENNY_PROVIDER:'openrouter',LENNY_PROVIDER_BASE:'https://evil.invalid'}));
 const p={messages:[{role:'system',content:'fixture'},{role:'user',content:'question'}],models:['wrong-model'],route:'fallback',reasoning_effort:'none',max_completion_tokens:9999};
 const first=openrouterConversationPayload(p,1,[],'question');assert.deepEqual(first.tool_choice,{type:'function',function:{name:'search_transcripts'}});
 const next=openrouterConversationPayload(p,2,['E1'],'question');assert.equal(next.response_format,undefined);assert.equal(next.tool_choice,'none');
 assert.deepEqual(next.provider,{allow_fallbacks:false,require_parameters:true,data_collection:'deny'});assert.equal(next.models,undefined);assert.equal(next.route,undefined);assert.equal(next.max_completion_tokens,undefined);assert.equal(next.reasoning_effort,undefined);
 assert.throws(()=>openrouterConversationPayload(p,3,[],''));
 const advice=openrouterAdvicePayload({...p,grammar:'fixture',response_format:{}},'Advice. /no_think',384);assert.equal(advice.max_tokens,384);assert.equal(advice.grammar,undefined);assert.equal(advice.response_format,undefined);
});

test('OpenRouter follow-up preserves tool replay and omits incompatible JSON mode',()=>{
 const call={role:'assistant',tool_calls:[{id:'fixture-call',type:'function',function:{name:'search_transcripts',arguments:'{"query":"current"}'}}]};
 const result={role:'tool',tool_call_id:'fixture-call',content:'{"items":[{"id":"E1","text":"Synthetic evidence"}]}'};
 const payload={messages:[{role:'system',content:'fixture'},{role:'user',content:'fixture'},call,result],tools:[{type:'function',function:{name:'search_transcripts'}}],response_format:{type:'json_object'}};
 const next=openrouterConversationPayload(payload,2,['E1'],'fixture');
 assert.equal(next.response_format,undefined);assert.equal(next.tool_choice,'none');assert.equal(next.max_tokens,128);
 assert.deepEqual(next.messages[2],call);assert.deepEqual(next.messages[3],result);assert.deepEqual(next.tools,payload.tools);
 assert.match(next.messages[0].content,/JSON object/);assert.match(next.messages[0].content,/E1/);
});


test('GPT-OSS120B extends only its final answer after linked retrieval',()=>{
 const toolCall={role:'assistant',tool_calls:[{id:'fixture-call',type:'function',function:{name:'search_transcripts',arguments:'{"query":"current"}'}}]};
 const toolResult={role:'tool',tool_call_id:'fixture-call',content:'{"items":[{"id":"E1","text":"Synthetic fixture only"}]}'};
 const p={model:'openai/gpt-oss-120b',messages:[{role:'system',content:'fixture'},{role:'user',content:'question'},toolCall,toolResult]};
 const final=openrouterConversationPayload(p,2,['E1'],'question');assert.equal(final.max_tokens,1024);assert.equal(final.tool_choice,'none');
 assert.deepEqual(final.provider,{allow_fallbacks:false,require_parameters:true,data_collection:'deny'});assert.deepEqual(final.messages[2],toolCall);assert.deepEqual(final.messages[3],toolResult);
 assert.equal(openrouterConversationPayload(p,1,['E1'],'question').max_tokens,128);
 assert.equal(openrouterConversationPayload({...p,messages:p.messages.slice(0,2)},2,['E1'],'question').max_tokens,128);
 assert.equal(openrouterConversationPayload(p,2,[],'question').max_tokens,128);
 for(const model of ['google/gemini-2.5-flash-lite','openai/gpt-oss-20b:free','openai/gpt-oss-120b:free'])assert.equal(openrouterConversationPayload({...p,model},2,['E1'],'question').max_tokens,128);
 const unrelated={...p,messages:[...p.messages.slice(0,2),{...toolCall,tool_calls:[{...toolCall.tool_calls[0],function:{...toolCall.tool_calls[0].function,name:'unapproved_tool'}}]},toolResult]};
 assert.equal(openrouterConversationPayload(unrelated,2,['E1'],'question').max_tokens,128);
});
