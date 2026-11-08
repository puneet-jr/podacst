"""Desktop split-pane browser checks. Fixtures are separate from real app reads.

Uses a fresh isolated Chrome profile. No model calls or real database writes.
Reports/screenshots stay private in ignored .cache/workspace-resize.
"""
import asyncio,json,sys
from pathlib import Path
from datetime import datetime,timezone
from playwright.async_api import async_playwright,expect
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from browser_phase8 import FixtureAPI
BASE='http://127.0.0.1:8080';ROOT=Path('.cache/workspace-resize');ROOT.mkdir(exist_ok=True,parents=True)
async def contained(page):
 assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth'),'horizontal page overflow'
async def sizes(page):
 return await page.evaluate("Object.fromEntries(['sessions-panel','research-panel','workspace-context'].map(id=>[id,Math.round(document.getElementById(id).getBoundingClientRect().width)]))")
async def open_saved_session(page,sid):
 offset=0;index=None
 while offset<=100000:
  response=await page.request.get(BASE+f'/api/sessions?limit=100&offset={offset}');assert response.ok,response.status;items=await response.json()
  found=next((i for i,s in enumerate(items) if s['id']==sid),None)
  if found is not None:index=offset+found;break
  if len(items)<100:break
  offset+=100
 assert index is not None,'Saved session missing'
 while await page.locator('.session').count()<=index:
  old=await page.locator('.session').count();await page.get_by_role('button',name='Load older sessions',exact=True).click()
  await page.wait_for_function('(old)=>document.querySelectorAll(".session").length>old',arg=old)
 await page.locator('.session').nth(index).click()
async def drag(page,handle,delta):
 b=await handle.bounding_box();x=b['x']+b['width']/2;y=b['y']+min(250,b['height']/2)
 await page.mouse.move(x,y);await page.mouse.down();await page.mouse.move(x+delta,y,steps=12);await page.mouse.up()
async def modes(page):
 for name,label,action in [('Research question','Your question','Ask'),('Evidence-led essay','Essay topic','Draft essay')]:
  await page.get_by_label(name,exact=True).check();await page.get_by_label(label,exact=True).fill('Keep this unsent research draft')
  field=page.get_by_label(label,exact=True);await field.focus();await expect(field).to_be_focused()
  button=page.get_by_role('button',name=action,exact=True);await button.scroll_into_view_if_needed();await expect(button).to_be_in_viewport();await expect(button).to_be_enabled()
  models=page.locator('.model-details summary');await models.scroll_into_view_if_needed();await models.click();await expect(page.locator('.model-details p').first).to_be_visible();await models.click();await contained(page)
async def main():
 checks=[];errors=[];real_posts=[]
 async with async_playwright() as p:
  browser=await p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True)
  ctx=await browser.new_context(viewport={'width':1440,'height':900});page=await ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)));state=FixtureAPI()
  for i in range(2):
   sid=f'resize-{i}';state.sessions.append({'id':sid,'title':f'Resize fixture session {i}','created_at':'2026-11-07T00:00:00Z','updated_at':'2026-11-07T00:00:00Z'});state.messages[sid]=[];state.essays[sid]=[];state.artifacts[sid]=[]
  state.messages['resize-0']=[{'id':'reply','role':'assistant','content':'Synthetic saved reply. [S1]','citations':[{'source_label':'S1'}],'created_at':'2026-11-07T00:00:00Z'}]
  state.artifacts['resize-0']=[{'id':'document','title':'Saved resize fixture','type':'html','preview_html':'<h1>Saved resize fixture</h1><p>Static preview only.</p>','source_metadata':{'provenance':'reviewed_fixture','citation_ids':['S1']}}]
  await page.route('**/api/**',state.handle);await page.goto(BASE+'/workspace')
  left=page.get_by_role('separator',name='Resize Sessions',exact=True);right=page.get_by_role('separator',name='Resize Sources and Documents',exact=True)
  original=await sizes(page);assert original['sessions-panel']==208 and original['workspace-context']==292
  await drag(page,left,60);a=await sizes(page);assert a['sessions-panel']==268 and a['workspace-context']==292;assert a['research-panel']==original['research-panel']-60
  await drag(page,right,-100);b=await sizes(page);assert b['workspace-context']==392 and b['sessions-panel']==268;assert b['research-panel']==a['research-panel']-100
  await left.focus();assert await left.evaluate('e=>getComputedStyle(e).outlineStyle')!='none';await left.press('ArrowLeft');await left.press('Shift+ArrowRight');assert (await sizes(page))['sessions-panel']==298
  await right.focus();await right.press('ArrowRight');assert (await sizes(page))['workspace-context']==382
  saved=await sizes(page);await page.reload();await expect(left).to_have_attribute('aria-valuenow','298');assert await sizes(page)==saved
  checks.append('fixture: mouse and keyboard resize take space only from Research; visible divider focus; saved widths restore after reload')
  await page.set_viewport_size({'width':1200,'height':900});assert (await sizes(page))['research-panel']>=480;await contained(page)
  await right.press('End');assert (await sizes(page))['research-panel']>=480;await left.press('Home');await right.press('Home');await contained(page)
  await page.set_viewport_size({'width':1440,'height':900});await left.dblclick();await right.dblclick();assert (await sizes(page))['sessions-panel']==208 and (await sizes(page))['workspace-context']==292
  await page.locator('.session').first.click();await right.press('End');await modes(page);assert (await sizes(page))['research-panel']>=480
  await right.press('Enter');await left.press('ArrowRight');await left.press('Enter');assert (await sizes(page))['sessions-panel']==208 and (await sizes(page))['workspace-context']==292
  checks.append('fixture: viewport clamp, min/max and Home/End; double-click/Enter reset; Ask/Essay composer and Models disclosure reachable with Research at its minimum')
  await page.get_by_label('Essay topic',exact=True).fill('Keep this unsent research draft');citation=page.get_by_role('button',name='S1 · View source',exact=True).first;await citation.click();await expect(page.locator('.source-inspector h3')).to_be_focused();text=await page.locator('.source-inspector pre').inner_text()
  await page.get_by_role('button',name='Collapse Sessions',exact=True).click();await expect(page.get_by_role('button',name='Expand Sessions',exact=True)).to_be_focused();assert (await sizes(page))['research-panel']>900
  await expect(page.locator('.source-inspector pre')).to_have_text(text);await page.get_by_role('button',name='Expand Sessions',exact=True).click();await expect(page.get_by_role('button',name='Collapse Sessions',exact=True)).to_be_focused()
  before=await sizes(page);await page.get_by_role('button',name='Expand reader',exact=True).click();assert (await sizes(page))['workspace-context']>before['workspace-context'];await expect(page.locator('#workspace-context')).to_be_focused();await right.press('ArrowLeft');await page.get_by_role('button',name='Close expanded reader',exact=True).click();assert await sizes(page)==before;await expect(page.get_by_role('button',name='Expand reader',exact=True)).to_be_focused()
  await page.get_by_role('button',name='Expand reader',exact=True).click();await page.locator('#workspace-context').press('Escape');await expect(page.get_by_role('button',name='Expand reader',exact=True)).to_be_focused();assert await sizes(page)==before
  await page.get_by_role('button',name='Expand reader',exact=True).click();await page.get_by_role('button',name='Close source',exact=True).click();await expect(citation).to_be_focused();assert await sizes(page)==before;await expect(page.get_by_label('Essay topic',exact=True)).to_have_value('Keep this unsent research draft')
  checks.append('fixture: collapse/expand Sessions preserves draft/source and returns focus; expanded reader restores widths/focus by button, Escape and closing a citation source')
  await page.locator('#context-tab-documents').click();frame=page.locator('.artifact-panel iframe');await expect(page.frame_locator('iframe').locator('h1')).to_have_text('Saved resize fixture');await frame.evaluate("e=>e.dataset.resizeIdentity='same-mounted-iframe'")
  await drag(page,right,-60);await page.get_by_role('button',name='Expand reader',exact=True).click();await page.get_by_role('button',name='Close expanded reader',exact=True).click();await page.get_by_role('button',name='Collapse Sessions',exact=True).click()
  for width in [1024,768,390,1440]:
   await page.set_viewport_size({'width':width,'height':844});await contained(page)
   if width<1200:await expect(left).to_be_hidden()
   if width in [1024,768]:
    await page.locator('#tab-documents').click();await page.get_by_role('button',name='Close context panel',exact=True).click();await expect(page.locator('#tab-documents')).to_be_focused();await expect(page.locator('.context')).to_be_hidden();await modes(page);await page.locator('#tab-documents').click()
   if width==390:
    await page.locator('#tab-chat').click();await modes(page);await page.locator('#tab-documents').click()
   await expect(frame).to_have_attribute('data-resize-identity','same-mounted-iframe');await expect(page.frame_locator('iframe').locator('h1')).to_have_text('Saved resize fixture')
  await page.get_by_role('button',name='Expand Sessions',exact=True).click();await page.get_by_label('Essay topic',exact=True).fill('Keep this unsent research draft');await citation.click()
  for width in [1024,768,390,1440]:
   await page.set_viewport_size({'width':width,'height':844});await expect(page.locator('.source-inspector pre')).to_have_text(text);await contained(page)
  await page.get_by_role('button',name='Close source',exact=True).click();await expect(citation).to_be_focused();await expect(page.get_by_label('Essay topic',exact=True)).to_have_value('Keep this unsent research draft')
  checks.append('fixture: draft, open source and identical mounted document iframe survive resize/collapse and 1440/1024/768/390px transitions; tablet on-demand dismissal returns focus; phone panels remain exclusive')
  await page.screenshot(path=str(ROOT/'fixture-desktop.png'));await ctx.close()
  # Independent real app reads. Never send a generation or write request.
  real=await browser.new_context(viewport={'width':1440,'height':900});page=await real.new_page();page.on('request',lambda r:real_posts.append(r.url) if r.method!='GET' else None);page.on('pageerror',lambda e:errors.append(str(e)));await page.goto(BASE+'/workspace')
  # Existing reviewed sessions may be beyond the first API page.
  for sid,kind in [('157d4419-4739-44b3-9988-d69642468bae','source'),('6f882513-96b5-4fcc-88c2-1e1dc82d9585','document')]:
   await open_saved_session(page,sid);await expect(page.locator('.composer')).to_be_visible()
   if kind=='source':
    c=page.get_by_role('button',name='S1 · View source',exact=True).first;await c.click();await expect(page.locator('.source-inspector h3')).to_be_focused()
   else:
    await page.locator('#context-tab-documents').click();await expect(page.frame_locator('iframe').locator('h1')).to_contain_text('Use must-have customer feedback')
   await page.get_by_role('button',name='Expand reader',exact=True).click();await contained(page);await page.screenshot(path=str(ROOT/f'real-expanded-{kind}.png'));await page.get_by_role('button',name='Close expanded reader',exact=True).click();await expect(page.get_by_role('button',name='Expand reader',exact=True)).to_be_focused()
   if kind=='source':await page.get_by_role('button',name='Close source',exact=True).click();await expect(c).to_be_focused()
   await modes(page)
  await real.close();assert not errors,errors;assert not real_posts,real_posts
  checks.append('real app reads: saved cited answer and reviewed essay export remain readable while expanded; restore/focus and both composer modes pass; no API writes or model calls')
  report={'at':datetime.now(timezone.utc).isoformat(),'browser':browser.version,'checks':checks,'page_errors':errors,'real_api_writes':real_posts,'model_calls':0,'limits':'Fixture behavior is separate from saved real app reads; no new generation or mobile device keyboard claim.'};(ROOT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));await browser.close()
if __name__=='__main__':asyncio.run(main())
