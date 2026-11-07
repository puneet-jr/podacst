import {test} from 'node:test';
import assert from 'node:assert/strict';
import {sourceSpan} from './src/lib.ts';
test('review spans retain exact Unicode code-point positions',()=>{
 const original='A 😀 preface. Exact café evidence 🧪. More text.';
 const quote='Exact café evidence 🧪.';const span=sourceSpan(original,quote);
 assert.equal(Array.from(original).slice(span.start,span.end).join(''),quote);
});
test('review cannot submit invented or empty evidence',()=>{
 assert.throws(()=>sourceSpan('Actual source.','Invented claim.'));
 assert.throws(()=>sourceSpan('Actual source.',''));
});
