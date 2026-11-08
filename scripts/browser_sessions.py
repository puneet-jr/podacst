"""Paginated fixture sessions: fetch older records without dropping selected work."""
import asyncio,json,sys
from pathlib import Path
from urllib.parse import urlparse,parse_qs
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from playwright.async_api import async_playwright,expect
from browser_phase8 import FixtureAPI
ROOT=Path('.cache/phase10/browser-pagination');ROOT.mkdir(parents=True,exist_ok=True)
async def main():
 state=FixtureAPI();corpus={'active_episodes':9,'active_chunks':373,'latest':{'discovered':303}}
 for i in range(42):
  sid='page-'+str(i);state.sessions.append({'id':sid,'title':'Saved fixture '+str(i),'created_at':'2026-11-07T00:00:00Z','updated_at':'2026-11-07T00:00:00Z'});state.messages[sid]=[];state.essays[sid]=[];state.artifacts[sid]=[]
 async def handle(route):
  q=route.request
  if urlparse(q.url).path=='/api/ingestion/status':return await route.fulfill(json=corpus)
  if urlparse(q.url).path=='/api/sessions' and q.method=='GET':
   params=parse_qs(urlparse(q.url).query);offset=int(params.get('offset',['0'])[0]);limit=int(params.get('limit',['25'])[0]);return await route.fulfill(json=state.sessions[offset:offset+limit])
  return await state.handle(route)
 checks=[]
 async with async_playwright() as p:
  b=await p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True)
  for width in [1440,390]:
   corpus['active_episodes']=9;corpus['active_chunks']=373
   c=await b.new_context(viewport={'width':width,'height':844});page=await c.new_page();await page.route('**/api/**',handle);await page.goto('http://127.0.0.1:8080/workspace')
   if width==390:await page.locator('#tab-sessions').click()
   await expect(page.locator('.session')).to_have_count(25);await page.locator('.session').first.click();await page.get_by_label('Your question',exact=True).fill('Keep this unsent pagination draft')
   if width==390:await page.locator('#tab-sessions').click()
   await page.get_by_role('button',name='Load older sessions',exact=True).click();await expect(page.locator('.session')).to_have_count(42);await expect(page.get_by_role('button',name='Load older sessions',exact=True)).to_have_count(0)
   assert await page.locator('.session.selected').count()==1
   if width==390:await page.locator('#tab-chat').click()
   await expect(page.get_by_label('Your question',exact=True)).to_have_value('Keep this unsent pagination draft');await page.get_by_role('button',name='Refresh',exact=True).click();await expect(page.get_by_label('Your question',exact=True)).to_have_value('Keep this unsent pagination draft');await expect(page.locator('.session')).to_have_count(42)
   await expect(page.get_by_text('9 of 303 episodes · partial library',exact=True)).to_be_visible();corpus['active_episodes']=303;corpus['active_chunks']=12770;await page.get_by_role('button',name='Refresh',exact=True).click();await expect(page.get_by_text('303 of 303 episodes · indexed library',exact=True)).to_be_visible()
   assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth');checks.append(f'{width}px:25→42 paginated rows, no duplicates/lost selection, draft and loaded pages survive refresh, partial/full corpus status, no overflow');await c.close()
  await b.close()
 report={'fixture':True,'checks':checks,'model_calls':0,'database_writes':0};(ROOT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
if __name__=='__main__':asyncio.run(main())
