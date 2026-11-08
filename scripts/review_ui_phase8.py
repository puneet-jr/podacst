"""Apply reviewed edits and acceptance using normal UI controls; no inference."""
import asyncio,json
from pathlib import Path
from datetime import datetime,timezone
from hashlib import sha256
import httpx
from playwright.async_api import async_playwright,expect
ROOT=Path('docs/agent-transcripts/phase-08');SCREEN=Path('.cache/phase8-browser')
async def main():
 folder=next(ROOT.glob('live-*'));plan=json.loads((folder/'manual-edit-plan.json').read_text());req=json.loads((folder/'request.json').read_text());sid,rid=plan['session_id'],plan['run_id'];calls=[]
 if (folder/'accepted.json').exists():raise SystemExit('Already accepted; inspect/reopen instead')
 async with async_playwright() as p:
  b=await p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True);c=await b.new_context(viewport={'width':1512,'height':1050});page=await c.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:calls.append({'method':r.method,'path':r.url.split(':8080')[-1]}) if r.method=='POST' and '/api/' in r.url else None)
  await page.goto('http://127.0.0.1:8080/workspace');await page.get_by_role('button',name=req['title'],exact=False).click();await expect(page.get_by_role('heading',name='Essay draft · review required',exact=True)).to_be_visible()
  for i in range(6):
   await page.locator('.essay-review .review-section').nth(i).locator('summary').click()
   for n,text in enumerate(plan['quotes'][str(i+1)]):await page.get_by_label(f'Section {i+1} evidence {n+1}',exact=True).fill(text)
   await page.get_by_label(f'Section {i+1} application',exact=True).fill(plan['advice'][str(i+1)])
  await page.get_by_role('button',name='Inspect essay source',exact=False).first.click();await expect(page.locator('.source-inspector h3')).to_be_focused();await page.get_by_role('button',name='Close source',exact=True).click()
  await page.get_by_role('button',name='Save reviewed edits',exact=True).click();await expect(page.locator('.review-meta')).to_contain_text(str(plan['expected_word_count'])+' words',timeout=30_000);await expect(page.get_by_role('button',name='Save reviewed edits',exact=True)).to_be_disabled()
  await page.get_by_label('Review notes',exact=True).fill('Codex direct review of actual source passages. Three exact source selections corrected and all six advice paragraphs revised using the app. Original model output preserved; hypotheses and limitations retained. Not independent expert review.')
  for check in await page.locator('.essay-review input[type=checkbox]').all():await check.check()
  await expect(page.get_by_role('button',name='Accept and save essay',exact=True)).to_be_enabled();await page.get_by_role('button',name='Accept and save essay',exact=True).click();await expect(page.locator('.long-reply')).to_have_count(1,timeout=30_000)
  await page.get_by_role('button',name='Save Markdown',exact=True).click();await expect(page.get_by_text('Markdown document saved to this session.',exact=True)).to_be_visible();await page.get_by_role('button',name='Save HTML',exact=True).click();await expect(page.get_by_text('HTML document saved to this session.',exact=True)).to_be_visible();await expect(page.get_by_text('Live endpoint essay · manually reviewed and edited',exact=True)).to_be_visible();await expect(page.frame_locator('iframe').locator('h2')).to_have_count(6)
  async with httpx.AsyncClient(base_url='http://127.0.0.1:8080',trust_env=False,timeout=20) as client:
   r=await client.get(f'/api/sessions/{sid}/essays/{rid}');r.raise_for_status();accepted=r.json();assert accepted['status']=='completed' and accepted['validation']['passed_deterministic'];assert 1125<=accepted['validation']['word_count']<=1375
   (folder/'accepted.json').write_text(json.dumps(accepted,indent=2,ensure_ascii=False)+'\n');(folder/'essay.md').write_text(accepted['draft_md'])
   r=await client.get(f'/api/sessions/{sid}/artifacts');r.raise_for_status();artifacts=r.json();assert {a['type'] for a in artifacts}=={'markdown','html'};assert all(a['source_metadata']['provenance']=='live_endpoint' for a in artifacts)
   (folder/'artifacts.json').write_text(json.dumps(artifacts,indent=2,ensure_ascii=False)+'\n')
   r=await client.get(f'/api/sessions/{sid}/essays/{rid}/sources');r.raise_for_status();sources={s['source_label']:s for s in r.json()};checks=[]
   for i,section in enumerate(accepted['metadata']['fact_sections']):
    for f in section['facts']:
     original=sources[f['source_id']]['original_text'];valid=original[f['start']:f['end']]==f['text'];assert valid;checks.append({'section':i+1,'label':f['source_id'],'chunk_id':f['chunk_id'],'exact_original_span':valid,'sha256':sha256(f['text'].encode()).hexdigest()})
   (folder/'review-checks.json').write_text(json.dumps({'reviewed_at':datetime.now(timezone.utc).isoformat(),'surface':'Normal app review/source/advice/acceptance controls','factual_blocks':checks,'word_count':accepted['validation']['word_count'],'manual_advice_edits':len(accepted['metadata']['advice_edits']),'manual_source_edits':len(accepted['metadata'].get('evidence_edits',[])),'claims':'Guest quotations checked against actual passages; no inferred95% result or invented case outcome. Advice is proposed experimentation with hypotheses, metrics and decisions.','readability':'Reader question before evidence, six headings, selective bold and concrete takeaway. Evidence-led/quote-heavy style remains.','post_requests':calls,'page_errors':errors,'fixture':False},indent=2)+'\n')
  await page.screenshot(path=str(SCREEN/'live-accepted-desktop.png'));await page.reload();await page.get_by_role('button',name=req['title'],exact=False).click();await expect(page.frame_locator('iframe').locator('h2')).to_have_count(6);await expect(page.get_by_role('heading',name='Essay saved',exact=True)).to_be_visible();await page.set_viewport_size({'width':390,'height':844});await page.get_by_role('tab',name='Documents',exact=True).click();assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth');await page.get_by_role('button',name=accepted['validation']['citation_ids'][0]+' · View source',exact=True).last.click();await expect(page.locator('.source-inspector h3')).to_be_focused();await page.get_by_role('button',name='Close source',exact=True).click();await page.screenshot(path=str(SCREEN/'live-accepted-mobile.png'))
  assert not errors;print(json.dumps({'session_id':sid,'run_id':rid,'status':accepted['status'],'words':accepted['validation']['word_count'],'source_blocks_checked':len(checks),'artifacts':[(a['type'],a['id']) for a in artifacts],'reload_reopen':True,'mobile_source_focus_and_return':True,'browser':b.version,'page_errors':errors}));await b.close()
if __name__=='__main__':asyncio.run(main())
