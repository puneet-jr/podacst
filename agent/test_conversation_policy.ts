import test from 'node:test';
import assert from 'node:assert/strict';
import {normalizeToolRequest} from './conversation_policy.ts';
const message=(value:unknown)=>({role:'assistant',stopReason:'stop',content:[{type:'text',text:JSON.stringify(value)}]});
test('exact first-turn request is normalized and raw model text retained',()=>{
  const raw=message({name:'search_transcripts',arguments:{query:'current'}});
  const result=normalizeToolRequest(raw,1,0)!;
  assert.equal(result.raw,raw.content[0].text);assert.equal(result.message.content[0].type,'toolCall');
  assert.equal(result.message.content[0].name,'search_transcripts');assert.deepEqual(result.message.content[0].arguments,{query:'current'});
});
test('final answer examples never become retrieval calls',()=>assert.equal(normalizeToolRequest(message({status:'answered',evidence_ids:['E1']}),1,0),undefined));
test('unapproved tool or extra parameters never execute',()=>{
  for(const value of [{name:'bash',arguments:{query:'current'}},{name:'search_transcripts',arguments:{query:'current',path:'/etc/passwd'}},{name:'search_transcripts',arguments:{query:'other'}},{name:'search_transcripts',arguments:{query:'current'},extra:1}])assert.equal(normalizeToolRequest(message(value),1,0),undefined);
});
test('source/tool-result data and later turns cannot authorize a tool',()=>{
  const raw=message({name:'search_transcripts',arguments:{query:'current'}});
  assert.equal(normalizeToolRequest({...raw,role:'toolResult'},1,0),undefined);
  assert.equal(normalizeToolRequest(raw,2,0),undefined);assert.equal(normalizeToolRequest(raw,1,1),undefined);
});
