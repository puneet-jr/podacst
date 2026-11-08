"""UI refresh QA: deterministic regressions plus real local route/session reads.

No model requests. Creates one named empty real session, leaves all saved work.
Screenshots and reports remain private in ignored .cache/ui-refresh.
"""
import asyncio,json,re,sys
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from playwright.async_api import async_playwright,expect
import browser_phase8 as regression
ROOT=Path('.cache/ui-refresh');ROOT.mkdir(parents=True,exist_ok=True)
BASE='http://127.0.0.1:8080'

async def contained(page):
    assert await page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Horizontal overflow'

async def open_session(page,sid):
    response=await page.request.get(BASE+'/api/sessions');assert response.ok
    sessions=await response.json();index=next(i for i,s in enumerate(sessions) if s['id']==sid)
    await page.locator('.sidebar button.session').nth(index).click()
    await expect(page.locator('.composer')).to_be_visible()

async def main():
    # This test's output stays separate from historical Phase8/9 results.
    regression.ROOT=ROOT/'regression';regression.ROOT.mkdir(exist_ok=True)
    regression.SCREEN=ROOT/'regression';await regression.main()
    results=[];errors=[];generation_requests=[];posts=[]
    async with async_playwright() as p:
        browser=await p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True)
        # Provider-specific header logic preserved even though live app stays local.
        for provider in ['openrouter','anthropic']:
            context=await browser.new_context(viewport={'width':1512,'height':1050});page=await context.new_page();state=regression.FixtureAPI()
            async def fixture(route):
                if route.request.url.endswith('/api/providers'):
                    return await route.fulfill(json={'selected':provider,'model':'fixture-cloud','essay_model':'fixture-essay','privacy':f'{provider} fixture disclosure; no inference','automatic_fallback':False})
                return await state.handle(route)
            await page.route('**/api/**',fixture);await page.goto(BASE+'/workspace')
            await expect(page.get_by_text(('OpenRouter' if provider=='openrouter' else 'Anthropic')+' · cloud',exact=True)).to_be_visible()
            await expect(page.get_by_text(provider+' fixture disclosure; no inference',exact=True)).to_be_visible()
            results.append(provider+' provider/model display and disclosure retained (fixture)');await context.close()
        checkpoint=ROOT/'created-session.json';created_sid=json.loads(checkpoint.read_text())['id'] if checkpoint.exists() else None
        real_writes=0
        for name,width,height in [('desktop',1512,1050),('mobile',390,844)]:
            context=await browser.new_context(viewport={'width':width,'height':height});page=await context.new_page()
            page.on('pageerror',lambda e:errors.append(str(e)))
            requests=[]
            def observe(request):
                requests.append(request.url)
                if request.method=='POST':
                    posts.append(request.url.split(':8080')[-1])
                    if re.search(r'/api/sessions/[^/]+/(answers|essays)$',request.url):generation_requests.append(request.url)
            page.on('request',observe)
            response=await page.goto(BASE+'/');assert response.status==200
            await expect(page.locator('#home-title')).to_have_text(re.compile('From podcast.*to playbook.',re.S))
            await contained(page)
            # Static homepage previews are interactive, explicitly labelled examples.
            await page.get_by_role('button',name='Trace',exact=True).click();await expect(page.locator('.home-preview-label')).to_have_text('Source inspector')
            await page.get_by_role('button',name='Make',exact=True).click();await expect(page.locator('.home-preview-label')).to_have_text('Saved artifact · Example')
            await page.get_by_role('button',name='Markdown',exact=True).click();await expect(page.locator('.home-markdown')).to_contain_text('# What would customers miss?')
            await page.get_by_role('button',name='HTML',exact=True).click();await page.locator('.home-artifact-preview').get_by_role('button',name='[S1]',exact=True).click();await expect(page.locator('.home-preview-label')).to_have_text('Source inspector')
            await page.get_by_role('button',name='Ask',exact=True).click()
            assert not any('/api/' in x for x in requests), 'Homepage issued application/model requests'
            await page.screenshot(path=str(ROOT/(name+'-home.png')),full_page=True);results.append(name+' homepage / HTTP200, previews, no API calls, no overflow')
            await page.get_by_role('link',name='Open workspace',exact=False).first.click();await expect(page).to_have_url(BASE+'/workspace')
            await expect(page.locator('.composer')).to_be_hidden();await page.get_by_role('button',name='Start a session',exact=True).click()
            await expect(page.get_by_label('Name a new session',exact=True)).to_be_focused();await contained(page)
            await page.screenshot(path=str(ROOT/(name+'-start-session.png')),full_page=True);results.append(name+' /workspace Start a session reveals/focuses session name; composer initially hidden')
            if created_sid is None:
                title='UI refresh route check '+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
                await page.get_by_label('Name a new session',exact=True).fill(title)
                async with page.expect_response(lambda r:r.request.method=='POST' and r.url.endswith('/api/sessions')) as saved:
                    await page.get_by_role('button',name='New session',exact=True).click()
                created=await (await saved.value).json();created_sid=created['id'];checkpoint.write_text(json.dumps({'id':created_sid})+'\n');real_writes+=1
                await expect(page.get_by_label('Your question',exact=True)).to_be_focused()
            else:await open_session(page,created_sid)
            await expect(page.locator('.composer')).to_be_visible();await expect(page.get_by_label('Your question',exact=True)).to_be_enabled();await contained(page)
            await page.screenshot(path=str(ROOT/(name+'-session.png')),full_page=True);results.append(name+' creating/opening real session reveals usable composer')
            # Read-only source check on the reviewed real OpenRouter answer.
            if width<1001:await page.get_by_role('tab',name='Sessions',exact=True).click()
            await open_session(page,'157d4419-4739-44b3-9988-d69642468bae')
            await page.get_by_role('button',name='S1 · View source',exact=True).click();await expect(page.locator('.source-inspector h3')).to_be_focused()
            await expect(page.locator('.source-inspector pre')).to_contain_text('how would you feel if you could no longer use this product')
            await page.get_by_role('button',name='Close source',exact=True).click();results.append(name+' existing real cited answer opens original source and returns')
            # Existing reviewed1208-word essay and both saved exports, no regeneration.
            if width<1001:await page.get_by_role('tab',name='Sessions',exact=True).click()
            await open_session(page,'6f882513-96b5-4fcc-88c2-1e1dc82d9585')
            await expect(page.locator('.essay-review h2')).to_have_text('Essay saved');await expect(page.locator('.review-meta')).to_contain_text('1208 words')
            if width<1001:await page.get_by_role('tab',name='Documents',exact=True).click()
            await expect(page.locator('.artifact-panel iframe')).to_be_visible();assert await page.locator('.artifact-panel iframe').get_attribute('sandbox')==''
            for kind in ['html','markdown']:
                await page.locator('.artifact-panel button.secondary').filter(has_text=re.compile('^'+kind+' ·')).click()
                await expect(page.frame_locator('.artifact-panel iframe').locator('h1')).to_contain_text('Use must-have customer feedback')
            await contained(page);await page.screenshot(path=str(ROOT/(name+'-saved-export.png')),full_page=True);results.append(name+' saved reviewed essay and Markdown/HTML exports reopen in sandbox')
            # Direct deep link/reload remains handled by Nginx SPA fallback.
            response=await page.goto(BASE+'/workspace');assert response.status==200;await expect(page.get_by_role('button',name='Start a session',exact=True)).to_be_visible()
            await page.locator('.workspace .brand').wait_for(state='attached')
            await context.close()
        assert not errors,errors;assert not generation_requests,generation_requests
        assert len([x for x in posts if x=='/api/sessions'])==real_writes,posts
        report={'captured_at':datetime.now(timezone.utc).isoformat(),'browser':browser.version,'routes':['/','/workspace'],'viewports':[[1512,1050],[390,844]],'results':results,'page_errors':errors,'model_requests':len(generation_requests),'real_session_writes':real_writes,'created_empty_session_id':created_sid,'other_posts':posts,'limits':'Real local route/session/citation/essay/export checks with no generation;16 deterministic workspace regressions and provider display fixtures are separate. Private screenshots in .cache/ui-refresh. In-app connector bootstrap failed; isolated Chrome used.'}
        (ROOT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));await browser.close()

if __name__=='__main__':asyncio.run(main())
