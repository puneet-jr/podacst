"""Real artifact preservation across app restart, then actual browser reopening."""
import json,time,subprocess,sys
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import httpx
from playwright.sync_api import sync_playwright
ROOT=Path('docs/agent-transcripts/phase-07')
SCREEN=Path('.cache/phase7-browser');SCREEN.mkdir(parents=True,exist_ok=True)
def main():
 folder=next(ROOT.glob('live-*'));old=json.loads((folder/'result.json').read_text());accepted=json.loads((folder/'accepted.json').read_text());sid=old['session_id']
 artifacts=[json.loads((folder/(kind+'-artifact.json')).read_text()) for kind in ['markdown','html']]
 def snapshot(c):
  rows=[]
  for a in artifacts:
   r=c.get(f"/api/sessions/{sid}/artifacts/{a['id']}");r.raise_for_status();v=r.json();sources=[]
   for label in v['source_metadata']['citation_ids']:
    q=c.get(f"/api/sessions/{sid}/artifacts/{a['id']}/sources/{label}");q.raise_for_status();s=q.json();sources.append({'label':label,'id':s['chunk_id'],'body_sha256':sha256(s['original_text'].encode()).hexdigest(),'http_status':q.status_code})
   rows.append({'artifact_id':a['id'],'type':a['type'],'content_sha256':sha256(v['content'].encode()).hexdigest(),'preview_sha256':sha256(v['preview_html'].encode()).hexdigest(),'provenance':v['source_metadata']['provenance'],'sources':sources})
  return rows
 with httpx.Client(base_url='http://127.0.0.1:8080',trust_env=False,timeout=15) as c:
  before=snapshot(c)
  (ROOT/'restart-before.json').write_text(json.dumps(before,indent=2)+'\n')
  r=subprocess.run([sys.executable,'scripts/docker.py','compose','restart','api','web'],capture_output=True,text=True,timeout=60)
  (ROOT/'restart-command.json').write_text(json.dumps({'command':['python','scripts/docker.py','compose','restart','api','web'],'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr},indent=2)+'\n');r.check_returncode()
  for n in range(60):
   try:
    q=c.get('/api/health/ready')
    if q.status_code==200:break
   except httpx.HTTPError:pass
   time.sleep(.3)
  else:raise RuntimeError('Readiness did not return')
  after=snapshot(c);assert before==after
  r=c.get('/api/providers');r.raise_for_status();provider=r.json();assert provider['model']=='qwen3:0.6b' and not provider['automatic_fallback']
  r=c.get(f'/api/sessions/{sid}/messages');r.raise_for_status();msg=next(m for m in r.json() if m['id']==accepted['assistant_message_id']);assert msg['content']==(folder/'essay.md').read_text()
  r=c.get(f"/api/sessions/{sid}/essays/{old['run_id']}");r.raise_for_status();assert r.json()['status']=='completed'
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True);context=browser.new_context(viewport={'width':1512,'height':1050});page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto('http://127.0.0.1:8080');page.get_by_role('button',name='Phase7 fresh endpoint essay',exact=False).click();page.get_by_text('Live endpoint essay · manually reviewed and edited',exact=True).wait_for()
  checks=[]
  for a in artifacts:
   page.get_by_role('button',name=a['type']+' · '+a['title'][:32],exact=True).click();frame=page.frame_locator(f'iframe[title="{a["type"]} artifact preview"]')
   frame.get_by_role('heading',name=a['title'],exact=True).wait_for();assert frame.locator('h2').count()==6;assert '[S2]' in frame.locator('body').inner_text();assert page.locator('iframe').get_attribute('sandbox')==''
   checks.append({'format':a['type'],'reopened_in_actual_browser':True,'six_headings':True,'citations_rendered':True,'provenance_visible':True})
  page.get_by_role('button',name='S2 · View source',exact=True).last.click();page.get_by_role('heading',name='Stored original passage',exact=True).wait_for();assert 'Lookout' in page.locator('.source-inspector pre').inner_text()
  page.screenshot(path=str(SCREEN/'live-reopened-desktop.png'),full_page=True)
  page.set_viewport_size({'width':390,'height':844});assert page.locator('.artifact-panel').is_visible();assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
  page.screenshot(path=str(SCREEN/'live-reopened-mobile.png'),full_page=True)
  report={'captured_at':datetime.now(timezone.utc).isoformat(),'before_after_exact_match':before==after,'artifacts':after,'saved_message_matches_accepted_essay':True,'essay_completed_after_restart':True,'chat_provider':provider,'browser':'isolated Chrome '+browser.version,'browser_checks':checks,'S2_original_opened':True,'mobile_no_horizontal_overflow':True,'page_errors':errors,'scope':'Basic viewer containment/reopen, not Phase8 comprehensive responsive/accessibility acceptance'}
  (ROOT/'restart-reopen.json').write_text(json.dumps(report,indent=2)+'\n');browser.close();print(json.dumps(report))
if __name__=='__main__':main()
