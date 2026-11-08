import test from 'node:test';
import assert from 'node:assert/strict';
import {plainMarkdownPayload} from './essay_format.ts';
test('plain Markdown removes every structured grammar parameter without changing other limits',()=>{
  const original={response_format:{type:'json_schema'},grammar:'old',format:'json',max_tokens:850,messages:[{role:'user',content:'Pinned evidence'}]};
  const result=plainMarkdownPayload(original);
  for(const key of ['response_format','grammar','format'])assert.equal(key in result,false);
  assert.equal(result.tool_choice,'none');assert.equal(result.max_tokens,850);assert.deepEqual(result.messages,original.messages);
  assert.equal('response_format' in original,true);
});
