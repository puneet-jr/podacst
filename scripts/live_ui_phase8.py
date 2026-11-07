"""Real browser -> app -> PostgreSQL/Pi/local Ollama. No request interception."""
import asyncio,json,time,sys
from pathlib import Path
from datetime import datetime,timezone
from hashlib import sha256
from playwright.async_api import async_playwright,expect
import httpx
ROOT=Path('docs/agent-transcripts/phase-08');SCREEN=Path('.cache/phase8-browser');SCREEN.mkdir(parents=True,exist_ok=True)
QUESTIONS=['According to Sean Ellis, what question identifies people who consider a product a must-have?','And what changes did Lookout make to onboarding after discovering antivirus mattered?']
async def main():
 existing=list(ROOT.glob('live-*'));folder=existing[0] if existing else ROOT/('live-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S'));folder.mkdir(exist_ok=True);title='Phase08 real local UI journey '+folder.name[-6:];sid=None
 if (folder/'generation.json').exists():
  previous=json.loads((folder/'generation.json').read_text())
  if '--resume-essay' not in sys.argv or previous['status']!='insufficient_evidence':raise SystemExit('Generation already captured; inspect instead of blindly rerunning')
  for name in ['generation.json','essay-raw.json','essay-raw.md']:
   src=folder/name;dest=folder/(src.stem+'-evidence-gap'+src.suffix)
   if dest.exists():raise SystemExit('Evidence-gap attempt already archived; inspect before another retry')
   dest.write_bytes(src.read_bytes())
 async with async_playwright() as p:
  b=await p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True);c=await b.new_context(viewport={'width':1512,'height':1050});page=await c.new_page();errors=[];calls=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  def request(q):
   if q.method=='POST' and '/api/' in q.url:calls.append({'method':q.method,'path':q.url.split(':8080')[-1],'at':datetime.now(timezone.utc).isoformat()})
  page.on('request',request);await page.goto('http://127.0.0.1:8080');await page.get_by_label('Name a new session').fill(title)
  if (folder/'request.json').exists():
   saved=json.loads((folder/'request.json').read_text());sid=saved['session_id'];title=saved['title'];await page.get_by_role('button',name=title,exact=False).click()
  else:
   async with page.expect_response(lambda r:'/api/sessions' in r.url and r.request.method=='POST') as response:await page.get_by_role('button',name='New session',exact=True).click()
   sid=(await (await response.value).json())['id'];(folder/'request.json').write_text(json.dumps({'session_id':sid,'title':title,'questions':QUESTIONS,'fixture':False,'generation_surface':'actual UI form; no route mocking'},indent=2)+'\n')
  await expect(page.get_by_label('Interview scope')).to_be_visible();await page.get_by_label('Interview scope').select_option('episodes/sean-ellis/transcript.md')
  checks=[]
  async with httpx.AsyncClient(base_url='http://127.0.0.1:8080',trust_env=False,timeout=20) as client:
   for i,q in enumerate(QUESTIONS):
    t=time.monotonic();old_r=await client.get(f'/api/sessions/{sid}/messages');old_r.raise_for_status();prior=next((m for m in old_r.json() if m['role']=='user' and m['content']==q and (m.get('run') or {}).get('status')=='completed'),None)
    if not prior:
     await page.get_by_label('Your question').fill(q);await page.get_by_role('button',name='Ask',exact=True).click();await expect(page.get_by_role('button',name='Ask',exact=True)).to_be_visible(timeout=100_000)
    r=await client.get(f'/api/sessions/{sid}/messages');r.raise_for_status();messages=r.json();user=next(m for m in reversed(messages) if m['role']=='user' and m['content']==q);assistant=next((m for m in reversed(messages) if m['role']=='assistant' and (m.get('run') or {}).get('id')==user['run']['id']),None)
    if not assistant or not assistant['citations']:raise RuntimeError('Local answer lacks citations; inspect saved session instead of rerunning')
    run_r=await client.get(f"/api/sessions/{sid}/runs/{user['run']['id']}");run_r.raise_for_status();run=run_r.json();spans=[]
    for label in [x['source_label'] for x in assistant['citations']]:
     r=await client.get(f"/api/sessions/{sid}/messages/{assistant['id']}/sources/{label}");r.raise_for_status();s=r.json();valid=all(s['original_text'][v['char_start']-s['metadata']['char_start']:v['char_end']-s['metadata']['char_start']]==v['text'] for v in s['quote_spans']);assert valid;spans.append({'label':label,'chunk_id':s['chunk_id'],'stored_span_matches':valid,'original_text_sha256':sha256(s['original_text'].encode()).hexdigest()})
    await page.locator('.message.assistant').nth(i).get_by_role('button',name=assistant['citations'][0]['source_label']+' · View source',exact=True).click();await expect(page.locator('.source-inspector h3')).to_be_focused();await page.get_by_role('button',name='Close source',exact=True).click()
    record={'name':'supported' if i==0 else 'follow_up','model':'qwen3:0.6b','browser_check_seconds':time.monotonic()-t,'resumed_existing_completed_request':bool(prior),'question':q,'actual_answer':assistant['content'],'run_id':run['id'],'status':run['status'],'actual_request_seconds':run['metadata'].get('duration_seconds'),'resolved_query':run['resolved_query'],'context_message_ids':run['context_message_ids'],'sources':spans,'retrieval_mode':run['retrieval_mode']};checks.append(record)
    (folder/'chat-checks.json').write_text(json.dumps(checks,indent=2,ensure_ascii=False)+'\n');print(json.dumps(record,ensure_ascii=False),flush=True)
    if i==0 and not ('how would you feel' in assistant['content'].lower() or 'no longer use' in assistant['content'].lower()):raise RuntimeError('Supported answer does not contain requested survey question')
    if i==1 and not ('onboarding' in assistant['content'].lower() and 'antivirus' in assistant['content'].lower()):raise RuntimeError('Follow-up answer incomplete for requested Lookout change')
   assert checks[0]['sources'][0]['chunk_id']!=checks[1]['sources'][0]['chunk_id']
   assert checks[1]['context_message_ids']
   await page.get_by_label('Evidence-led essay',exact=True).check();topic='Use must-have customer feedback to improve positioning and onboarding';await page.get_by_label('Essay topic',exact=True).fill(topic);await page.get_by_label('Audience',exact=True).fill('Early-stage product managers deciding how to move users toward first value');t=time.monotonic();await page.get_by_role('button',name='Draft essay',exact=True).click();await expect(page.get_by_role('button',name='Draft essay',exact=True)).to_be_enabled(timeout=650_000)
   r=await client.get(f'/api/sessions/{sid}/essays');r.raise_for_status();summary=r.json()[0];r=await client.get(f"/api/sessions/{sid}/essays/{summary['id']}");r.raise_for_status();essay=r.json();(folder/'essay-raw.json').write_text(json.dumps(essay,indent=2,ensure_ascii=False)+'\n');(folder/'essay-raw.md').write_text(essay['draft_md'] or '')
   await page.screenshot(path=str(SCREEN/'live-draft-review.png'))
   (folder/'generation.json').write_text(json.dumps({'session_id':sid,'run_id':essay['id'],'essay_seconds':time.monotonic()-t,'status':essay['status'],'validation':essay['validation'],'calls':calls,'page_errors':errors,'manual_review':'pending; this script does not accept the essay','fixture':False},indent=2)+'\n');print(json.dumps({'folder':str(folder),'session_id':sid,'run_id':essay['id'],'status':essay['status'],'validation':essay['validation'],'seconds':time.monotonic()-t}),flush=True)
  await b.close()
if __name__=='__main__':asyncio.run(main())
