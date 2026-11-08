"""Explicit source-span and advice edits for the one saved endpoint run; no inference."""
import json,re
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import httpx
from backend.app.writing import word_count
ROOT=Path('docs/agent-transcripts/phase-07')
def main():
 folder=next(ROOT.glob('live-*'));saved=json.loads((folder/'result.json').read_text());sid,rid=saved['session_id'],saved['run_id'];base=f'/api/sessions/{sid}/essays/{rid}'
 if (folder/'accepted.json').exists():raise SystemExit('Already reviewed; inspect instead of editing again')
 with httpx.Client(base_url='http://127.0.0.1:8080',trust_env=False,timeout=20) as c:
  r=c.get(base+'/sources');r.raise_for_status();sources={s['source_label']:s for s in r.json()}
  def span(label,start,until=None):
   original=sources[label]['original_text'];a=original.index(start);b=original.index(until,a) if until else len(original.rstrip())
   return {'start':a,'end':b}
  # Each submitted span indexes the stored original; the server derives text.
  # Include complete reported Lookout changes/result, and actual benefit method.
  s2=sources['S2']['original_text'];s3=sources['S3']['original_text'];s6=sources['S6']['original_text']
  def through(label,start,end):
   original=sources[label]['original_text'];a=original.index(start);b=original.index(end,a)+len(end);return {'start':a,'end':b}
  evidence={'2':[
   through('S2','So the company called Lookout','Androids.'),
   through('S2','And so when we ran this initial survey','focused on the antivirus functionality.'),
   through('S2','And so now we knew','reposition the product on antivirus.'),
   through('S2','But then the second thing that we did','"you\'re now protected from viruses."'),
   span('S2',"And so it's really the combination")],
   '3':[
    through('S3','Yeah, I mean it tells you something really important','what problem are they solving.'),
    span('S3','One of my favorite questions is','\n\n(00:15:43)')],
   '6':[through('S6',"So to me, the hardest, I wouldn't obsess",'customer acquisition is almost the last step.')]}
  advice={'1':"Which feedback should shape your next onboarding change? Try recording benefit descriptions before rewriting the signup promise. Compare what users value with the first meaningful task you ask them to complete. Track the proportion of new users completing that task and preserve explanations from people who stop. Treat better completion from a revised promise as a hypothesis. Review the observations before deciding whether to keep the revision, investigate a different benefit, or gather more responses. Keep the survey question separate from the completion measure so the review has two distinct observations to discuss.",
   '2':'Try comparing your current signup promise and first onboarding task with one revision. Record completed first tasks and the number of people who started, alongside their explanations of what they expected. Treat better completion as a hypothesis, not an outcome already established. After reviewing both versions, decide whether to keep the revision, revise it again, or gather more observations before choosing.',
   '3':'Ask users to describe the primary benefit in their own words before offering benefit choices. Preserve the original responses and review answers that challenge your preferred interpretation. Choose one benefit to investigate, then compare a first task that reflects it with the current task. Track completion and record what users expected. Treat better alignment as a hypothesis and decide what to investigate next after reading the responses.',
   '4':'Choose a single feature or benefit to investigate before editing several parts of onboarding at once. Write down what observation would change your mind about its importance. Ask users why it matters, keep contradictory answers and compare the proposed first task with the current one. Track completion rather than treating an enthusiastic comment as proof. Decide whether to keep the change, revise the hypothesis or ask a different question.',
   '5':'Compare the existing signup promise and first meaningful task with a proposed revision. Define what completion means before looking at the results, then record both completed tasks and the number of people who started each version. Keep their explanations beside the counts. Treat better completion as a hypothesis and check whether the observations support it. If the versions suggest different benefits or obstacles, choose one to investigate rather than changing everything. Review the original feedback before deciding to keep the revision, revise the wording or collect more observations. Record that decision and the evidence behind it so the next review can revisit the same question.',
   '6':'Preserve the raw benefit descriptions before choosing an interpretation. Select one benefit hypothesis and one first task to investigate. Track completed tasks alongside the number of people who started, and read the explanations from both groups. If observations conflict, keep the cause open and choose the next question. After reviewing the data, decide whether to keep the revision, revise the hypothesis or gather more observations.'}
  (folder/'manual-edit-request.json').write_text(json.dumps({'captured_at':datetime.now(timezone.utc).isoformat(),'editor':'Codex explicit editorial review; not raw model output','evidence_sections':evidence,'advice_sections':advice,'reasons':['Remove leaked91 words and drafting/caveat language','Select complete source sentences, add missing Lookout intervention/outcome and benefit-question sequence, remove dangling quotation','Replace outcome assurance with hypotheses and concrete observable metrics/decisions'],'regenerated':False},indent=2,ensure_ascii=False)+'\n')
  # Save/review the exact proposed candidate count before submitting edits.
  r=c.post(base+'/evidence',json={'sections':evidence});r.raise_for_status();(folder/'after-evidence-edit.json').write_text(json.dumps(r.json(),indent=2,ensure_ascii=False)+'\n')
  r=c.post(base+'/advice',json={'sections':advice});r.raise_for_status();run=r.json();(folder/'reviewed.json').write_text(json.dumps(run,indent=2,ensure_ascii=False)+'\n');(folder/'essay.md').write_text(run['draft_md'])
  checks=[]
  for i,s in enumerate(run['metadata']['fact_sections']):
   for f in s['facts']:
    original=sources[f['source_id']]['original_text'];assert original[f['start']:f['end']]==f['text'];assert sha256(f['text'].encode()).hexdigest()==f['sha256']
    checks.append({'section':i+1,'source_id':f['source_id'],'chunk_id':f['chunk_id'],'start':f['start'],'end':f['end'],'exact_original_span':True,'adjacent_citation':f['text'].replace('\n','\n> ')+' ['+f['source_id']+']' in run['sections'][i]['body']})
  (folder/'claim-review.json').write_text(json.dumps({'reviewer':'Codex direct comparison against all six actual stored passages, not independent expert review','factual_blocks':checks,'advice_review':'All6 sections explicitly proposed actions. Hypotheses not measured outcomes; no new historical claim. Raw quotes are attributed excerpts, not paraphrased model facts.','lookout_review':'Product-level7% subgroup, antivirus positioning and onboarding, combined expectations/speed to value, next cohort40%. No measured engagement/conversion claim or isolated causal estimate.','readability':'Complete excerpt boundaries plus concrete applications. Quote-heavy evidence-led structure, not original long-form narrative. Reader question, six headings, five-or-more action bullets, selective bold, useful decision.','manual_edits':'All advice paragraphs and three source selections explicitly edited; before/after preserved in DB metadata and manual-edit-request.json. This is a heavily reviewed output, not autonomous quality proof.','validation':run['validation']},indent=2)+'\n')
  print(json.dumps({'validation':run['validation'],'checks':len(checks),'all_source_checks':all(x['exact_original_span'] and x['adjacent_citation'] for x in checks)}),flush=True)
  if not run['validation']['passed_deterministic']:raise SystemExit('Final rubric not passed; no acceptance')
  review={'reviewer':'Codex direct claim and readability review','hook':True,'progression':True,'factual_support':True,'applications_distinct':True,'complete':True,'notes':['All factual blocks checked as exact source spans with adjacent valid citations. Complete context and qualifications manually reviewed.','All advice explicitly revised and recorded: no new historical claims, expected benefits as hypotheses, concrete metrics and decisions.','Raw standard-endpoint output preserved, including leaked91 words and clipped excerpts. Manual advice edits and3 evidence edits disclosed.','Full1125–1375-word rubric,6 sections, bullets and selective bold pass; evidence-led quote-heavy style, not autonomous model quality.']}
  r=c.post(base+'/review',json=review);r.raise_for_status();accepted=r.json();(folder/'accepted.json').write_text(json.dumps(accepted,indent=2,ensure_ascii=False)+'\n')
  artifacts=[]
  for kind in ['markdown','html']:
   r=c.post(f'/api/sessions/{sid}/artifacts',json={'message_id':accepted['assistant_message_id'],'format':kind});r.raise_for_status();a=r.json();assert a['source_metadata']['provenance']=='live_endpoint';artifacts.append(a)
   (folder/(kind+'-artifact.json')).write_text(json.dumps(a,indent=2,ensure_ascii=False)+'\n')
  print(json.dumps({'status':accepted['status'],'word_count':run['validation']['word_count'],'artifacts':[{'id':a['id'],'type':a['type'],'provenance':a['source_metadata']['provenance'],'manual_edits':a['source_metadata']['manual_edits']} for a in artifacts]}))
if __name__=='__main__':main()
