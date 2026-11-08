"""Repeat deterministic UI regressions plus explicit cloud/missing-key display."""
import asyncio,json
from pathlib import Path
from datetime import datetime,timezone
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import browser_phase8 as prior
from playwright.async_api import async_playwright,expect
ROOT=Path('docs/agent-transcripts/phase-09');SCREEN=Path('.cache/phase9-browser');SCREEN.mkdir(parents=True,exist_ok=True)
async def main():
    prior.ROOT=ROOT;prior.SCREEN=SCREEN
    await prior.main()
    report=json.loads((ROOT/"browser-fixture.json").read_text());report["screenshots"]=str(SCREEN);(ROOT/"browser-fixture.json").write_text(json.dumps(report,indent=2)+"\n")
    state=prior.FixtureAPI()
    async def handle(route):
        url=route.request.url
        if url.endswith('/api/providers'):
            return await route.fulfill(json={'selected':'anthropic','model':'fixture-cloud','essay_model':'fixture-cloud','automatic_fallback':False,'privacy':'Cloud selected: bounded transcript excerpts, relevant conversation and instructions may be sent to Anthropic. Embeddings remain local. Requests may incur charges; no automatic fallback.','providers':[{'id':'anthropic','implemented':True,'configured':False,'scope':'Fixture only; no key and no inference.'}]})
        if url.endswith('/api/health/ready'):
            return await route.fulfill(status=503,json={'status':'not_ready','checks':{'ollama':{'ready':True},'provider':{'ready':False,'code':'cloud_key_missing'}}})
        return await state.handle(route)
    async with async_playwright() as p:
        browser=await p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True)
        context=await browser.new_context(viewport={'width':1512,'height':1050});page=await context.new_page();await page.route('**/api/**',handle)
        await page.goto('http://127.0.0.1:8080/workspace');await expect(page.get_by_text('Anthropic · cloud',exact=True)).to_be_visible();await expect(page.get_by_text('Cloud selected: bounded transcript excerpts',exact=False)).to_be_visible()
        await page.get_by_label('Name a new session').fill('Cloud fixture');await page.get_by_role('button',name='New session',exact=True).click();await page.get_by_label('Your question',exact=True).fill('Retain this unavailable-provider request')
        await expect(page.get_by_role('button',name='Ask',exact=True)).to_be_disabled();await expect(page.get_by_label('Your question',exact=True)).to_have_value('Retain this unavailable-provider request');await expect(page.get_by_text('No fallback was attempted.',exact=False)).to_be_visible();assert state.answers==0
        await page.screenshot(path=str(SCREEN/'cloud-unavailable.png'),full_page=True)
        (ROOT/'browser-cloud-fixture.json').write_text(json.dumps({'captured_at':datetime.now(timezone.utc).isoformat(),'browser':browser.version,'checks':['selected provider/model visible','cloud privacy boundary visible','missing key disables generation and retains input','no provider request/fallback'],'fixture':True,'model_calls':0,'database_writes':0},indent=2)+'\n');await browser.close()
if __name__=='__main__':asyncio.run(main())
