"""Build explicit editorial instructions from this run's sources; not generation."""
import json,httpx
from pathlib import Path
from backend.app.writing import assemble,word_count
ROOT=Path('docs/agent-transcripts/phase-08');folder=next(ROOT.glob('live-*'));g=json.loads((folder/'generation.json').read_text());raw=json.loads((folder/'essay-raw.json').read_text())
with httpx.Client(base_url='http://127.0.0.1:8080',trust_env=False,timeout=20) as c:
 r=c.get(f"/api/sessions/{g['session_id']}/essays/{g['run_id']}/sources");r.raise_for_status();sources={s['source_label']:s for s in r.json()}
quotes={str(i+1):[f['text'] for f in s['facts']] for i,s in enumerate(raw['metadata']['fact_sections'])}
def through(label,start,end):
 text=sources[label]['original_text'];a=text.index(start);return text[a:text.index(end,a)+len(end)]
quotes['2'][0]=through('S3',"So to me, the hardest, I wouldn't obsess",'customer acquisition is almost the last step.')
s=sources['S5']['original_text'];a=s.index('One of my favorite questions is');quotes['4'][1]=s[a:s.index('\n\n(00:15:43)',a)].strip()
quotes['6'][1]=through('S7','So at LogMeIn, when we initially tried to grow the business',"per month profitably trying to grow the business.")
advice={
'1':'Which feedback should guide your next onboarding change? Start by writing the question you want the research to answer, then ask users what benefit they would miss. Preserve their wording rather than translating every response into a feature request. Compare the current signup promise with the first meaningful task, and track how many people start and complete that task. Treat better completion after a revision as a hypothesis. Review both the counts and the explanations before choosing whether to keep a change, revise your interpretation or collect more observations.',
'2':'Compare the explanations of users who complete the first task with those who stop. Keep separate notes for a confusing promise, an onboarding obstacle and a possible core-product issue. Treat each explanation as something to investigate, not a diagnosis already established. Choose one question for the next review and decide what observation would cause you to change direction. Leave the cause open when the observations conflict.',
'3':'Write down the benefit you think users value, then compare it with their own descriptions. Check whether the signup promise and first task reflect the same idea. Keep contradictory responses alongside the common themes. Treat clearer alignment as a hypothesis to test with a small revision. Track first-task completion and ask what users expected before deciding whether to keep the revision, change the promise or investigate a different benefit.',
'4':'Ask an open-ended benefit question before offering choices. Keep the original answers so the later options can be compared with what people actually described. After collecting responses, choose one benefit to investigate and note the reasons users give for valuing it. Review contrary answers before deciding whether to keep that interpretation. Use the next interview or small onboarding comparison to examine what remains unclear.',
'5':'Compare the existing signup promise and first meaningful task with one revision. Define completion before reviewing results, and record both completed tasks and the number of people who started each version. Keep user explanations beside the counts. Treat better completion as a hypothesis rather than a promised outcome. If the observations conflict, choose the next question instead of changing every part of the journey. Decide whether to retain the revision, revise the wording or gather more observations, and write down the evidence behind that decision.',
'6':'Preserve raw feedback before choosing an interpretation. Select one benefit hypothesis and one first task to investigate. Track completed tasks alongside the number of people who started, and read the explanations from both groups. If observations conflict, keep the cause open rather than declaring a result. After reviewing the data, decide whether to keep the revision, change the hypothesis or collect more observations before choosing.'}
sections=[]
for i,s in enumerate(raw['sections']):
 label=s['source_ids'][0];facts='\n\n'.join('> '+q.replace('\n','\n> ')+' ['+label+']' for q in quotes[str(i+1)]);app='Application: '+('**Treat improvement as a hypothesis.** ' if i==2 else '')+advice[str(i+1)]
 if i==5:
  import re
  app='\n'.join('- Application: '+x for x in re.split(r'(?<=[.!?])\s+',advice[str(i+1)]))
 body=app+'\n\n'+facts if i==0 else facts+'\n\n'+app;sections.append({'heading':s['heading'],'body':body})
count=word_count(assemble(raw['outline']['title'],sections))
plan={'session_id':g['session_id'],'run_id':g['run_id'],'advice':advice,'quotes':quotes,'expected_word_count':count,'editor':'Codex explicit UI edits after direct source review','reasons':['Remove dangling source quotation and incomplete95% statement without inventing missing result','Use the actual benefit-question sequence instead of duplicate retention commentary','Replace repeated feedback-rate assertions with proposed actions, observable metrics and hypotheses','Remove uncited Next action paragraph; keep reader hook before evidence'],'model_regenerated':False}
(folder/'manual-edit-plan.json').write_text(json.dumps(plan,indent=2,ensure_ascii=False)+'\n');print(json.dumps({'expected_words':count,'advice_sections':6,'changed_source_sections':[2,4,6]}))
