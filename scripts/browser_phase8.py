"""Deterministic UI regressions; API interception means ZERO model/DB evidence."""
import asyncio,json,time
from pathlib import Path
from uuid import uuid4
from datetime import datetime,timezone
from urllib.parse import urlparse
from playwright.async_api import async_playwright,expect
from backend.app.artifacts import preview
ROOT=Path('docs/agent-transcripts/phase-08');SCREEN=Path('.cache/phase8-browser');SCREEN.mkdir(parents=True,exist_ok=True)
class FixtureAPI:
 def __init__(self):
  self.sessions=[];self.messages={};self.essays={};self.artifacts={};self.answers=0;self.mode='normal';self.source_delay=0;self.save_error=False;self.pending_delay=0
  self.template=json.loads(Path('docs/agent-transcripts/phase-07/live-20261106T212600/accepted.json').read_text())
 async def handle(self,route):
  q=route.request;path=urlparse(q.url).path.removeprefix('/api');parts=path.strip('/').split('/');body=q.post_data_json if q.method=='POST' and q.post_data else {};method=q.method
  async def ok(data,status=200):await route.fulfill(status=status,json=data)
  async def fail(message):await ok({'error':{'message':message,'request_id':'fixture-only','code':'fixture','retryable':True}},503)
  if path=='/providers':return await ok({'selected':'ollama','model':'fixture-chat · no inference','essay_model':'fixture-essay · no inference','automatic_fallback':False})
  if path=='/health/ready':return await ok({'status':'ready','checks':{k:{'ready':self.mode!='missing_model','essay_model_available':self.mode!='missing_model'} for k in ['database','agent','ollama']}})
  if path=='/retrieval/scopes':return await ok([{'source_path':'episodes/sean-ellis/transcript.md','guest':'Sean Ellis','title':'Fixture interview'}])
  if path=='/ingestion/status':return await ok({'active_episodes':9,'active_chunks':373,'latest':{'discovered':303}})
  if path=='/sessions':
   if method=='POST':
    s={'id':str(uuid4()),'title':body['title'],'created_at':'2026-11-07T00:00:00Z','updated_at':'2026-11-07T00:00:00Z'};self.sessions.insert(0,s);self.messages[s['id']]=[];self.essays[s['id']]=[];self.artifacts[s['id']]=[];return await ok(s,201)
   return await ok(self.sessions)
  sid=parts[1] if len(parts)>1 else ''
  if len(parts)==3 and parts[2]=='messages':return await ok(self.messages[sid])
  if len(parts)>=6 and parts[-2]=='sources':
   await asyncio.sleep(self.source_delay);label=parts[-1];return await ok({'source_label':label,'chunk_id':str(uuid4()),'original_text':'Synthetic browser fixture: the stored original is displayed safely. <img src="https://ui-attack.invalid/x" onerror="alert(1)">','quote_spans':[{'text':'Synthetic browser evidence, not model grounding proof.'}],'source_url':None,'video_url':None,'metadata':{'title':'Synthetic original source','guest':'Fixture guest','source_path':'episodes/fixture/transcript.md','source_hash':'fixture-hash','version':1,'start_seconds':1,'end_seconds':2,'sponsor':False,'metadata_warnings':['Deterministic UI fixture; no live generation']}})
  if len(parts)==3 and parts[2]=='answers':
   self.answers+=1;rid=str(uuid4());existing=next((m for m in self.messages[sid] if m['client_message_id']==body['client_message_id']),None)
   if not existing:self.messages[sid].append({'id':str(uuid4()),'client_message_id':body['client_message_id'],'role':'user','content':body['content'],'created_at':'2026-11-07T00:00:00Z','run':{'id':rid,'status':'running','error_code':None},'citations':[]})
   events=[{'type':'started','run_id':rid,'data':{}},{'type':'retrieving','run_id':rid,'data':{}}]
   if self.mode=='timeout':
    self.messages[sid][-1]['run']={'id':rid,'status':'failed','error_code':'model_timeout'};events.append({'type':'failed','run_id':rid,'data':{'run':{'error_code':'model_timeout'}}})
   else:
    for record in self.messages[sid]:
     if record['client_message_id']==body['client_message_id']:record['run']={'id':rid,'status':'completed','error_code':None}
    label='S1' if self.answers==1 else 'S2';unsupported='unsupported' in body['content'].lower();text='The indexed evidence does not establish this. Try a narrower question.' if unsupported else f'Synthetic reply {self.answers} uses a frozen passage. [{label}]'
    self.messages[sid].append({'id':str(uuid4()),'client_message_id':str(uuid4()),'role':'assistant','content':text,'created_at':'2026-11-07T00:00:00Z','run':None,'citations':[] if unsupported else [{'source_label':label,'chunk_id':str(uuid4())}]});events.append({'type':'completed','run_id':rid,'data':{}})
   await asyncio.sleep(self.pending_delay or .15)
   try:await route.fulfill(content_type='application/x-ndjson',body='\n'.join(json.dumps(e) for e in events)+'\n')
   except Exception:pass
   return
  if len(parts)==3 and parts[2]=='essays':
   if method=='GET':return await ok([{'id':e['id'],'status':e['status'],'error_code':e.get('error_code'),'topic':e['request']['topic']} for e in self.essays[sid]])
   e=json.loads(json.dumps(self.template));e.update(id=str(uuid4()),session_id=sid,status='needs_review',assistant_message_id=None,error_code=None);e['request']['topic']=body['topic'];e['metadata']['model']='fixture-essay · no inference';self.essays[sid].insert(0,e)
   self.messages[sid].append({'id':str(uuid4()),'client_message_id':body['client_message_id'],'role':'user','content':'Fixture essay request: '+body['topic'],'created_at':'2026-11-07T00:00:00Z','run':None,'citations':[]})
   await asyncio.sleep(.2);return await route.fulfill(content_type='application/x-ndjson',body='\n'.join(json.dumps({'type':t,'run_id':e['id'],'data':{}}) for t in ['started','retrieving','drafting','needs_review'])+'\n')
  if len(parts)>=4 and parts[2]=='essays':
   e=next(e for e in self.essays[sid] if e['id']==parts[3])
   if len(parts)==4:return await ok(e)
   if parts[4]=='sources':return await ok([{'source_label':label,'original_text':'\n\n'.join(f['text'] for s in e['metadata']['fact_sections'] for f in s['facts'] if f['source_id']==label),'chunk_id':str(uuid4()),'quote_spans':[],'source_url':None,'video_url':None,'metadata':{'title':'Synthetic essay source','guest':'Fixture','source_path':'fixture','source_hash':'fixture','version':1,'start_seconds':None,'end_seconds':None,'sponsor':False,'metadata_warnings':['Fixture']}} for label in ['S1','S2','S3','S4','S5','S6']])
   if parts[4]=='review':
    e['status']='completed';e['assistant_message_id']=str(uuid4());self.messages[sid].append({'id':e['assistant_message_id'],'client_message_id':str(uuid4()),'role':'assistant','content':e['draft_md'],'created_at':'2026-11-07T00:00:00Z','run':None,'citations':[{'source_label':s,'chunk_id':str(uuid4())} for s in ['S1','S2','S3','S4','S5','S6']]});return await ok(e)
  if len(parts)==3 and parts[2]=='artifacts':
   if method=='GET':return await ok(self.artifacts[sid])
   if self.save_error:self.save_error=False;return await fail('Fixture save unavailable')
   m=next(m for m in self.messages[sid] if m['id']==body['message_id']);kind=body['format'];a={'id':str(uuid4()),'type':kind,'title':m['content'].splitlines()[0].lstrip('# '),'preview_html':preview(m['content'],'markdown','Deterministic fixture'),'source_metadata':{'provenance':'reviewed_fixture','citation_ids':[s['source_label'] for s in m['citations']]}};self.artifacts[sid].insert(0,a);return await ok(a,201)
  return await ok({'error':{'message':'Fixture route not implemented','request_id':'fixture'}},404)

async def main():
 state=FixtureAPI();results=[]
 async with async_playwright() as p:
  b=await p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True);c=await b.new_context(viewport={'width':1512,'height':1050});page=await c.new_page();errors=[];network=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda q:network.append(q.url));await page.route('**/api/**',state.handle);await page.goto('http://127.0.0.1:8080/workspace')
  await page.get_by_label('Name a new session').fill('Phase08 deterministic browser fixture');await page.get_by_role('button',name='New session',exact=True).click();await expect(page.get_by_label('Your question')).to_be_focused();await page.get_by_label('Interview scope').select_option('episodes/sean-ellis/transcript.md')
  await page.get_by_label('Your question').fill('Fixture question');await page.get_by_role('button',name='Ask',exact=True).click();await expect(page.get_by_text('Synthetic reply 1 uses a frozen passage.',exact=False)).to_be_visible()
  source_button=page.get_by_role('button',name='S1 · View source',exact=True);await source_button.click();await expect(page.locator('.source-inspector h3')).to_be_focused();await expect(page.locator('.source-inspector pre')).to_contain_text('Synthetic browser fixture');await page.get_by_role('button',name='Close source',exact=True).click();await expect(source_button).to_be_focused();results.append('new session -> question -> source; focus moves and restores')
  await page.get_by_label('Your question').fill('Fixture follow-up');await page.get_by_role('button',name='Ask',exact=True).click();await expect(page.get_by_text('Synthetic reply 2 uses a frozen passage.',exact=False)).to_be_visible();results.append('follow-up displays distinct source')
  await page.get_by_label('Evidence-led essay',exact=True).check();await page.get_by_label('Essay topic',exact=True).fill('Deterministic fixture essay topic');await page.get_by_role('button',name='Draft essay',exact=True).click();await expect(page.get_by_role('heading',name='Essay draft · review required',exact=True)).to_be_visible();await expect(page.get_by_role('button',name='Accept and save essay')).to_be_disabled()
  await page.get_by_label('Name a new session').fill('Blocked while review is dirty');await expect(page.get_by_role('button',name='New session',exact=True)).to_be_enabled();await page.locator('.review-section').first.locator('summary').click();field=page.get_by_label('Section 1 application',exact=True);original=await field.input_value();await field.fill(original+' A proposed extra review step.');await expect(page.get_by_role('button',name='New session',exact=True)).to_be_disabled();home_link=page.get_by_role('link',name='Lenny Growth Assistant home',exact=True);await expect(home_link).to_have_attribute('aria-disabled','true');await home_link.click(force=True);await expect(page).to_have_url('http://127.0.0.1:8080/workspace');await page.get_by_role('button',name='Discard unsaved edits',exact=True).click();await expect(field).to_have_value(original);await expect(page.get_by_role('button',name='New session',exact=True)).to_be_enabled();await page.get_by_label('Name a new session').fill('');results.append('unsaved review edits protect navigation and can be explicitly discarded')
  for check in await page.locator('.essay-review input[type=checkbox]').all():await check.check()
  await page.get_by_label('Review notes',exact=True).fill('Deterministic fixture UI exercise, not real model grounding evidence.');await page.get_by_role('button',name='Accept and save essay').click();await expect(page.get_by_text('Essay accepted and saved. Open Documents',exact=False)).to_be_visible();results.append('essay draft -> explicit review gate -> accepted reply')
  state.save_error=True;await page.get_by_role('button',name='Save Markdown',exact=True).click();await expect(page.get_by_role('alert').filter(has_text='Could not save this document')).to_be_visible();await expect(page.locator('.message.assistant').last).to_be_visible();await page.get_by_role('button',name='Save Markdown',exact=True).click();await expect(page.get_by_text('Markdown document saved to this session.',exact=True)).to_be_visible();await page.get_by_role('button',name='Save HTML',exact=True).click();await expect(page.get_by_text('HTML document saved to this session.',exact=True)).to_be_visible();await expect(page.frame_locator('iframe').locator('h2')).to_have_count(6);results.append('artifact save failure/retry -> both formats rendered')
  await page.reload();await page.get_by_role('button',name='Phase08 deterministic browser fixture',exact=False).click();await page.get_by_role('tab',name='Documents',exact=True).click();await expect(page.frame_locator('iframe').locator('h2')).to_have_count(6);results.append('saved session/essay/artifact reopen after page reload')
  # Keyboard/native controls and visible focus treatment, not an automated WCAG certification.
  await page.locator('iframe').hover();await page.mouse.wheel(0,550);await asyncio.sleep(.1);assert await page.frame_locator('iframe').locator('body').evaluate('()=>window.scrollY>0');results.append('long artifact scrolls within isolated preview')
  samples=[]
  for selector in ['.message.assistant .message-text p','button:not(:disabled):not(.secondary):not(.session):not(.inline-citation)','.section-label']:
   colors=await page.locator(selector).first.evaluate("e=>{let p=e,bg;while(p){bg=getComputedStyle(p).backgroundColor;if(bg!=='rgba(0, 0, 0, 0)'&&bg!=='transparent')break;p=p.parentElement}return {fg:getComputedStyle(e).color,bg}}")
   import re
   def lum(color):
    rgb=[float(n)/255 for n in re.findall(r'[\d.]+',color)[:3]];linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb];return sum(a*b for a,b in zip(linear,[.2126,.7152,.0722]))
   a,z=lum(colors['fg']),lum(colors['bg']);ratio=(max(a,z)+.05)/(min(a,z)+.05);assert ratio>=4.5;samples.append({'selector':selector,**colors,'contrast':round(ratio,2)})
  results.append('sampled rendered text/control/label contrast >=4.5:1')
  await page.get_by_label('Your question').focus();outline=await page.get_by_label('Your question').evaluate('(e)=>getComputedStyle(e).outlineStyle');assert outline!='none'
  await page.get_by_label('Your question').fill('Remember this unsent thought');await page.get_by_label('Name a new session').fill('Independent fixture session');await page.get_by_role('button',name='New session',exact=True).click();await expect(page.locator('.message')).to_have_count(0);await expect(page.get_by_label('Interview scope')).to_have_value('');await page.get_by_role('button',name='Phase08 deterministic browser fixture',exact=False).click();await expect(page.get_by_label('Your question')).to_have_value('Remember this unsent thought');results.append('session isolation and unsent-input preservation')
  state.source_delay=.5;await page.get_by_role('button',name='S2 · View source',exact=True).first.click();await page.get_by_role('button',name='Independent fixture session',exact=False).click();await asyncio.sleep(.7);await expect(page.locator('.source-inspector')).to_have_count(0);state.source_delay=0;results.append('late source response does not cross sessions')
  # Timeout and bounded retry identity.
  state.mode='timeout';await page.get_by_label('Your question').fill('Timeout fixture question');await page.get_by_role('button',name='Ask',exact=True).click();await expect(page.get_by_role('alert')).to_contain_text('took too long');await expect(page.get_by_label('Your question')).to_have_value('Timeout fixture question');sid=state.sessions[0]['id'];before=len([m for m in state.messages[sid] if m['role']=='user']);state.mode='normal';await page.get_by_role('button',name='Retry question',exact=True).click();await expect(page.get_by_label('Your question')).to_have_value('');assert len([m for m in state.messages[sid] if m['role']=='user'])==before;results.append('timeout preserves input; retry reuses saved question identity')
  state.mode='missing_model';await page.get_by_label('Your question').fill('Keep this while model is missing');await page.get_by_role('button',name='Refresh',exact=True).click();await expect(page.get_by_text('The selected local model is unavailable.',exact=False)).to_be_visible();await expect(page.get_by_role('button',name='Ask',exact=True)).to_be_disabled();await expect(page.get_by_label('Your question')).to_have_value('Keep this while model is missing');state.mode='normal';await page.get_by_role('button',name='Refresh',exact=True).click();await expect(page.get_by_role('button',name='Ask',exact=True)).to_be_enabled();results.append('missing-model state and recovery retain input')
  await page.get_by_label('Your question').fill('Unsupported fixture request');await page.get_by_role('button',name='Ask',exact=True).click();await expect(page.locator('.message.assistant').last).to_contain_text('does not establish');await expect(page.locator('.message.assistant').last.locator('.citations button')).to_have_count(0);results.append('empty/unsupported evidence has no invented source buttons')
  state.pending_delay=1;await page.get_by_label('Your question').fill('Cancelled fixture input');await page.get_by_role('button',name='Ask',exact=True).click();await page.get_by_role('button',name='Cancel generation',exact=True).click();await expect(page.get_by_role('alert')).to_contain_text('Connection closed');await expect(page.get_by_label('Your question')).to_have_value('Cancelled fixture input');await asyncio.sleep(1.1);state.pending_delay=0;results.append('pre-start cancel keeps input; no model lifecycle claim from mocked API')
  await page.get_by_role('button',name='Phase08 deterministic browser fixture',exact=False).click();await page.get_by_role('tab',name='Documents',exact=True).click();await expect(page.frame_locator('iframe').locator('h2')).to_have_count(6);await page.screenshot(path=str(SCREEN/'fixture-desktop.png'))
  await page.set_viewport_size({'width':390,'height':844});await page.get_by_role('tab',name='Documents',exact=True).click();await expect(page.locator('#research-panel')).to_be_hidden();await expect(page.locator('#documents-panel')).to_be_visible();await page.get_by_role('tab',name='Documents',exact=True).press('ArrowRight');await expect(page.get_by_role('tab',name='Sources',exact=True)).to_be_focused();await expect(page.get_by_role('tab',name='Sources',exact=True)).to_have_attribute('aria-selected','true');await page.get_by_role('tab',name='Sources',exact=True).press('Home');await expect(page.locator('#sessions-panel')).to_be_visible();await page.get_by_role('tab',name='Documents',exact=True).click();await page.get_by_role('button',name='S2 · View source',exact=True).last.click();await expect(page.locator('#sources-panel')).to_be_visible();await expect(page.locator('.source-inspector h3')).to_be_focused();await page.get_by_role('button',name='Close source',exact=True).click();await expect(page.locator('#documents-panel')).to_be_visible();await expect(page.get_by_role('button',name='S2 · View source',exact=True).last).to_be_focused();assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth');await page.screenshot(path=str(SCREEN/'fixture-mobile.png'));results.append('mobile panel navigation, arrow/Home keys, source focus/return, no horizontal overflow')
  await page.set_viewport_size({'width':820,'height':1180});assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth');await page.set_viewport_size({'width':1024,'height':900});assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth');results.append('820px and1024px layout containment')
  assert not [u for u in network if 'ui-attack.invalid' in u];assert not errors
  report={'captured_at':datetime.now(timezone.utc).isoformat(),'fixture':True,'model_calls':0,'database_writes':0,'browser':b.version,'checks':results,'contrast_samples':samples,'page_errors':errors,'attack_requests':[],'screenshots':'private .cache/phase8-browser','limits':'Deterministic browser API interception; not local generation, persistence or factual-support evidence.'};(ROOT/'browser-fixture.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));await b.close()
if __name__=='__main__':asyncio.run(main())
