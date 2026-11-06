"""Deterministic writing contracts; no live model quality is inferred here."""
import json
import unittest
from uuid import uuid4
from pydantic import ValidationError
from backend.app.writing import EssayCreate,EssayError,POLICY,parse_outline,validate_essay,word_count


def outline():
    return {'status':'ready','title':'Synthetic fixture outline','sections':[{'heading':f'Unique heading {i}','purpose':'Explain this synthetic source-backed point.','source_ids':['S1']} for i in range(6)]}


class WritingContracts(unittest.TestCase):
    def test_word_count_excludes_citations_and_markdown_and_keeps_contractions(self):
        self.assertEqual(word_count("# A title\nDon't re-write 12.5 **percent**. [S1]\n1. Act now."),8)
        self.assertEqual(word_count('Café teams’ work [S7]'),3)

    def test_outline_requires_six_distinct_cited_sections(self):
        valid=outline();self.assertEqual(len(parse_outline(json.dumps(valid),{'S1'}).sections),6)
        for change in ['unknown','duplicate','missing']:
            wrong=outline()
            if change=='unknown':wrong['sections'][0]['source_ids']=['S99']
            if change=='duplicate':wrong['sections'][1]['heading']=wrong['sections'][0]['heading']
            if change=='missing':wrong['sections'].pop()
            with self.subTest(change=change),self.assertRaises(EssayError):parse_outline(json.dumps(wrong),{'S1'})

    def test_unsupported_outline_cannot_smuggle_sections(self):
        wrong=outline();wrong['status']='insufficient_evidence'
        with self.assertRaises(EssayError):parse_outline(json.dumps(wrong),{'S1'})
        wrong['sections']=[];self.assertEqual(parse_outline(json.dumps(wrong),{}).status,'insufficient_evidence')

    def test_numeric_quotes_citation_scope_and_unattributed_text_fail(self):
        source={'S1':{'original_text':'This synthetic observation uses a seventeen-day review window.'},'S2':{'original_text':'Another synthetic passage.'}}
        sections=[{'heading':'A section','source_ids':['S1'],'body':'A 99% improvement is guaranteed. “This was proved in every company.” [S2]\n\nAn uncited factual paragraph. [S99]'}]
        codes={e['code'] for e in validate_essay('Fixture',sections,source)['errors']}
        self.assertTrue({'unknown_citation','citation_not_in_section_evidence','unsupported_numeric_claim','unmatched_direct_quote','word_count_outside_range','incomplete_sections'}<=codes)
        self.assertTrue(validate_essay('Fixture',sections,source)['manual_review_required'])
        sections[0]['body']='A malformed source reference must not count as a valid citation. [S#1]'
        self.assertIn('unknown_citation',{e['code'] for e in validate_essay('Fixture',sections,source)['errors']})

    def test_application_label_does_not_certify_factual_quality_or_allow_html(self):
        sections=[{'heading':'Fixture','source_ids':['S1'],'body':'Application: Try a small review.\n\n<script>bad()</script> [S1]'}]
        result=validate_essay('Fixture',sections,{'S1':{'original_text':'Synthetic source.'}})
        self.assertFalse(result['passed_deterministic']);self.assertIn('unsupported_html_or_external_link',{e['code'] for e in result['errors']})
        self.assertTrue(result['manual_review_required'])
        applications=[{'heading':'Applications','source_ids':['S1'],'body':'A source-backed sentence. [S1]\n\n- Application: Inspect your own evidence.\n- Application: Choose a small change.\n- Application: Record what you learn.'}]
        self.assertNotIn('unattributed_paragraph',{e['code'] for e in validate_essay('Fixture',applications,{'S1':{'original_text':'Synthetic source.'}})['errors']})

    def test_request_and_policy_are_bounded(self):
        base={'topic':'A supported topic','audience':'Product managers','client_message_id':uuid4()}
        for change in [{'focus_questions':['x'*221]},{'focus_questions':['query']*4},{'timeout_seconds':901},{'source_path':'../../secret'},{'workflow':'chat'}]:
            with self.subTest(change=change),self.assertRaises(ValidationError):EssayCreate(**{**base,**change})
        self.assertEqual((POLICY['min_words'],POLICY['target_words'],POLICY['max_words']),(1125,1250,1375));self.assertEqual(POLICY['max_repairs'],1)
