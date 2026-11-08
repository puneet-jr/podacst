import unittest
from backend.app.artifacts import preview,CLEANER
class ArtifactSecurity(unittest.TestCase):
    def test_markdown_formatting_and_raw_html_is_text(self):
        d=preview('# Heading\n\n**Emphasis** [S2]\n\n- Action\n\n<script>bad()</script>','markdown','Fixture')
        self.assertIn('<h1>Heading</h1>',d);self.assertIn('<strong>Emphasis</strong>',d);self.assertIn('[S2]',d);self.assertNotIn('<script>',d)
    def test_active_html_network_and_navigation_removed(self):
        raw='<script>parent.pwned=true</script><img src="https://bad.test/x" onerror="bad()"><svg onload="bad()"><image href="x"/></svg><form action="/api/sessions"><input></form><iframe srcdoc="bad"></iframe><meta http-equiv="refresh" content="0;url=https://bad.test"><a href="javascript:bad()">link</a><style>@import "https://bad.test/x";body{position:fixed}</style><p style="color:red;background-image:url(https://bad.test/x);position:fixed" onclick="bad()">Safe</p>'
        safe=CLEANER.clean(raw)
        for needle in ['<script','<img','<svg','<form','<iframe','<meta','href=','onclick','background-image','position:','@import']:self.assertNotIn(needle,safe)
        self.assertIn('color:red',safe);self.assertIn('Safe',safe)
    def test_document_has_static_csp_and_escaped_title(self):
        d=preview('<h1>Good</h1>','html','</title><script>bad()</script>')
        self.assertTrue(d.startswith('<!doctype html>'));self.assertIn("default-src &#x27;none&#x27;",d);self.assertNotIn('<script>',d)
