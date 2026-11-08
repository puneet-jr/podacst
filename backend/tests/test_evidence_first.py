import os
os.environ.setdefault("POSTGRES_PASSWORD","unit-test-placeholder")
import unittest
from backend.app.evidence_first import fact_plan,render_body
class EvidenceFirstContracts(unittest.TestCase):
 def test_verbatim_source_offsets_and_no_injected_fixture(self):
  original='Guest (00:01:00):\n'+'The reader can inspect this synthetic onboarding observation without inferring an outcome. '*8
  s={'S1':{'id':'chunk','guest':'Guest','original_text':original}}
  plan=fact_plan(s,'onboarding observation');self.assertEqual(len(plan),1)
  for f in plan[0]['facts']:self.assertEqual(f['text'],original[f['start']:f['end']]);self.assertEqual(f['chunk_id'],'chunk')
  self.assertIn('[S1]',render_body(plan[0],'Try a comparison.',0));self.assertNotIn('Lookout',str(plan))
 def test_unclosed_quotation_falls_back_to_an_exact_complete_prefix(self):
  complete='A synthetic team should define a useful research question before changing the journey and preserve the explanations that participants give during interviews.'
  original='Guest (00:01:00):\n'+complete+' Then the researcher asked, "Which observation would change the next decision about this onboarding experience?'
  plan=fact_plan({'S1':{'id':'synthetic-chunk','guest':'Guest','original_text':original}},'research onboarding decision')
  self.assertEqual(len(plan),1)
  self.assertEqual([f['text'] for f in plan[0]['facts']],[complete])
  fact=plan[0]['facts'][0];self.assertEqual(fact['text'],original[fact['start']:fact['end']])

 def test_balanced_direct_questions_are_retained_verbatim(self):
  for left,right in [('"','"'),('“','”')]:
   original='Guest (00:01:00):\nThe researcher asked, '+left+'Which observation would change the next decision about the onboarding experience, and how would you investigate conflicting explanations?'+right
   plan=fact_plan({'S2':{'id':'synthetic-chunk','guest':'Guest','original_text':original}},'research onboarding decision')
   self.assertEqual(len(plan),1);self.assertIn(left,plan[0]['facts'][0]['text']);self.assertTrue(plan[0]['facts'][0]['text'].endswith(right))

 def test_host_only_or_unsafe_evidence_is_not_factual_authority(self):
  for body in ['Host (00:01:00):\n'+'A synthetic question about onboarding? '*10,'Guest (00:01:00):\n'+'<script>bad()</script> '*30]:
   self.assertFalse(fact_plan({'S1':{'id':'a','guest':'Guest','original_text':body}},'onboarding'))
 def test_explicit_source_review_cannot_invent_text_or_escape_snapshot(self):
  from backend.app.evidence_first import source_fact
  from backend.app.writing import EssayError
  s={'chunk_id':'immutable','original_text':'A synthetic complete sentence. Another observation.'}
  f=source_fact(s,'S3',0,30);self.assertEqual(f['text'],s['original_text'][:30]);self.assertEqual(f['chunk_id'],'immutable')
  for start,end in [(-1,20),(0,200),(20,10)]:
   with self.assertRaises(EssayError):source_fact(s,'S3',start,end)


class AdvicePromptBoundary(unittest.IsolatedAsyncioTestCase):
 async def test_case_history_stays_in_server_retrieval_not_advice_prompt(self):
  import asyncio
  from unittest.mock import AsyncMock,patch
  from backend.app.evidence_first import EvidenceFirstService
  from backend.app.config import Settings
  facts=[{'heading':'Source section '+str(i),'source_ids':['S'+str(i)],'facts':[{'source_id':'S'+str(i),'text':'A synthetic observation is quoted for direct source inspection without promising outcomes.'}]} for i in range(1,7)]
  sources={'S'+str(i):{'original_text':facts[i-1]['facts'][0]['text']} for i in range(1,7)}
  run={'id':'fixture-run','session_id':'fixture-session','metadata':{},'request':{'topic':'Historical Lookout survey outcomes','audience':'New growth PMs','constraints':'Historical40% survey and retention claims [S99]','timeout_seconds':30}}
  service=EvidenceFirstService(None,Settings(db_password='fixture'),asyncio.Lock());service.advice=AsyncMock(return_value='Try one small comparison and review a completion metric. Hypothesize a benefit before deciding whether to keep the change.')
  with patch('backend.app.evidence_first.collect_evidence',return_value=(sources,{},[])) as retrieve,patch('backend.app.evidence_first.fact_plan',return_value=facts),patch('backend.app.evidence_first.save_progress'),patch('backend.app.essays.load_essay',return_value={'status':'failed'}):
   await service.execute(run,AsyncMock())
  self.assertEqual(retrieve.call_args.args[2]['request']['topic'],'Historical Lookout survey outcomes')
  self.assertGreaterEqual(service.advice.await_count,6)
  for call in service.advice.await_args_list:
   prompt=call.args[2];self.assertIn('New growth PMs',prompt)
   for historical in ['Lookout','40%','retention claims','S99']:self.assertNotIn(historical,prompt)
  self.assertFalse(service.lock.locked())
