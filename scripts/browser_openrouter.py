"""OpenRouter UI fixture only; never a live cloud validation claim."""
import asyncio,json,sys
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from browser_phase8 import FixtureAPI
from playwright.async_api import async_playwright,expect
ROOT=Path('docs/agent-transcripts/phase-09');SCREEN=Path('.cache/phase9-openrouter-browser')
async def main():
    state=FixtureAPI();screen=SCREEN;screen.mkdir(parents=True,exist_ok=True)
    async def handle(route):
        url=route.request.url
        if url.endswith('/api/providers'):return await route.fulfill(json={'selected':'openrouter','model':'google/gemini-2.5-flash-lite','essay_model':'google/gemini-2.5-flash-lite','automatic_fallback':False,'privacy':'Cloud selected: bounded evidence may be sent to OpenRouter and the selected upstream model provider. No automatic fallback.'})
        if url.endswith('/api/health/ready'):return await route.fulfill(status=503,json={'status':'not_ready','checks':{'ollama':{'ready':True},'provider':{'ready':False,'code':'cloud_key_missing'}}})
        await state.handle(route)
    async with async_playwright() as p:
        browser=await p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True);context=await browser.new_context(viewport={'width':1512,'height':1050});page=await context.new_page();await page.route('**/api/**',handle)
        await page.goto('http://127.0.0.1:8080/workspace');await expect(page.get_by_text('OpenRouter · cloud',exact=True)).to_be_visible();await page.locator('.model-details summary').click();await expect(page.get_by_text('Chat: google/gemini-2.5-flash-lite',exact=True)).to_be_visible();await page.locator('.model-details summary').click();await expect(page.get_by_text('Cloud selected: bounded evidence',exact=False)).to_be_visible()
        await page.get_by_label('Name a new session').fill('OpenRouter UI fixture');await page.get_by_role('button',name='New session',exact=True).click();await page.get_by_label('Your question',exact=True).fill('Retain this unconfigured cloud request')
        await expect(page.get_by_role('button',name='Ask',exact=True)).to_be_disabled();await expect(page.get_by_label('Your question',exact=True)).to_have_value('Retain this unconfigured cloud request');assert state.answers==0
        await page.screenshot(path=str(screen/'missing-key.png'),full_page=True)
        record={'captured_at':datetime.now(timezone.utc).isoformat(),'provider':'openrouter','model':'google/gemini-2.5-flash-lite','fixture':True,'browser':browser.version,'model_calls':0,'database_writes':0,'checks':['actual OpenRouter label','model ID visible','OpenRouter/upstream privacy disclosure','missing-key retains input and disables generation'],'cloud_validation':'pending; UI fixture cannot validate cloud inference'}
        (ROOT/'browser-openrouter-fixture.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record));await browser.close()
if __name__=='__main__':asyncio.run(main())
