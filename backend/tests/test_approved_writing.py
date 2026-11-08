import unittest
from backend.app.approved_writing import render_approved,validate_facts
from backend.app.writing import EssayError

class ApprovedWritingTests(unittest.TestCase):
    def setUp(self):
        self.facts=[{'id':'F1','statement':'A synthetic observation.','source_id':'S2','chunk_id':'chunk-a','evidence_anchor':'synthetic anchor'}]
    def test_fixed_text_and_citation_are_atomic(self):
        validate_facts(self.facts,{'S2':{'chunk_id':'chunk-a','original_text':'A synthetic anchor exists.'}})
        result=render_approved('[[F1]]\n\nApplication: Inspect your own notes.',self.facts)
        self.assertEqual(result['markdown'],'A synthetic observation. [S2]\n\nApplication: Inspect your own notes.')
        self.assertEqual(result['placements'][0]['chunk_id'],'chunk-a')
        self.assertTrue(result['manual_review_required'])
    def test_no_factual_or_citation_injection_or_silent_repair(self):
        for raw in ['[[F1]] [S99]','[[F1]]\n\nA new factual assertion.','[[F1]]\n\nApplication: Lookout improved conversion.','[[F1]]\n\nApplication: This will guarantee success.','[[F1]]\n\nApplication: <script>bad()</script>','[[F1]]\n\nApplication: Inspect notes. [S3]','[[F1]]\n\n[[F1]]','Application: Inspect notes.','[[F9]]\n\nApplication: Inspect notes.']:
            with self.subTest(raw=raw),self.assertRaises(EssayError):render_approved(raw,self.facts)
    def test_source_refresh_or_anchor_drift_rejects_approval(self):
        for s in [{'chunk_id':'other','original_text':'synthetic anchor'},{'chunk_id':'chunk-a','original_text':'changed'}]:
            with self.assertRaises(EssayError):validate_facts(self.facts,{'S2':s})

class ServerAssemblyTests(unittest.TestCase):
    def test_no_model_ids_and_fixed_attached_citation(self):
        from backend.app.approved_writing import assemble_server_section
        facts=[{'id':'F1','statement':'A fixed synthetic observation.','source_id':'S3','chunk_id':'chunk-a'}]
        raw='Try reviewing your current signup message alongside the first task a new reader sees. Write down the promise and compare it with that task before choosing a small revision to discuss.'
        r=assemble_server_section('Foundation',facts,raw)
        self.assertIn('A fixed synthetic observation. [S3]',r['markdown'])
        self.assertTrue(r['markdown'].endswith('Application: '+raw))
        self.assertEqual(r['placements'][0]['chunk_id'],'chunk-a')
    def test_advice_rejects_ids_labels_outcomes_or_extra_paragraph(self):
        from backend.app.approved_writing import validate_application
        base='Try reviewing your current signup message alongside the first task a new reader sees. Write down the promise and compare it with that task before choosing a small revision to discuss.'
        for raw in ['Application: '+base,base+' [S2]',base+'\n\nAnother paragraph.',base+' This will guarantee success.',base+' Lookout was successful.']:
            with self.subTest(raw=raw),self.assertRaises(EssayError):validate_application(raw)

class ExperimentAdviceTests(unittest.TestCase):
    paragraph='Try comparing your existing signup promise and first onboarding task with a revised version. Track the proportion of new users who complete that task, and note how many users you observe in each group. Treat better completion as a hypothesis to test, rather than an expected result. After reviewing the data, decide whether to keep the revised version, revise the wording again, or collect more observations before choosing.'
    def test_proposed_metric_and_hypothesis_are_not_historical_claims(self):
        from backend.app.approved_writing import validate_experiment
        self.assertEqual(validate_experiment(self.paragraph),self.paragraph)
    def test_length_ids_and_guarantees_reject(self):
        from backend.app.approved_writing import validate_experiment
        for text in ['Try an experiment.',self.paragraph+' [S2]',self.paragraph.replace('Treat better completion','Guarantee better completion')]:
            with self.subTest(text=text),self.assertRaises(EssayError):validate_experiment(text)
