"""Stable final visual inspection of the live artifact after restart; no generation."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
p=Path('docs/agent-transcripts/phase-07')
SCREEN=Path('.cache/phase7-browser');SCREEN.mkdir(parents=True,exist_ok=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True);c=b.new_context(viewport={'width':1512,'height':1050});page=c.new_page();console=[];errors=[]
 page.on('console',lambda m:console.append({'type':m.type,'text':m.text}));page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8080');page.get_by_role('button',name='Phase7 fresh endpoint essay',exact=False).click();page.get_by_text('Live endpoint essay · manually reviewed and edited',exact=True).wait_for();page.get_by_text('Available',exact=True).first.wait_for()
 assert page.frame_locator('iframe').locator('h2').count()==6
 page.get_by_role('button',name='S2 · View source',exact=True).last.click();page.get_by_role('heading',name='Retrieval highlights',exact=True).wait_for()
 page.screenshot(path=str(SCREEN/'live-final-desktop.png'))
 page.set_viewport_size({'width':390,'height':844});page.locator('.artifact-panel').scroll_into_view_if_needed();assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.screenshot(path=str(SCREEN/'live-final-mobile.png'))
 report={'browser':b.version,'after_restart':True,'provenance_visible':True,'ready_available':True,'six_rendered_sections':True,'source_inspection':True,'mobile_no_horizontal_overflow':True,'console':console,'page_errors':errors,'scope':'Final viewer only; not comprehensive Phase8 UX/accessibility testing'}
 (p/'final-visual.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));b.close()
