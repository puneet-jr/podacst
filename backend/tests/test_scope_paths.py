"""Real pinned corpus slug shapes must be usable without accepting path traversal."""
import os
os.environ.setdefault("POSTGRES_PASSWORD","unit-test-placeholder")
import unittest
from uuid import uuid4
from backend.app.retrieval import SearchRequest
from backend.app.schemas import AnswerCreate
from backend.app.writing import EssayCreate
from backend.app.conversation import source_links

class SourcePathTests(unittest.TestCase):
    def test_pinned_unicode_and_underscore_slugs_work_at_all_boundaries(self):
        for slug in ['andy-raskin_','casey-winters_','gustav-söderström','teaser_2021']:
            path='episodes/'+slug+'/transcript.md'
            with self.subTest(path=path):
                self.assertEqual(SearchRequest(query='research',source_path=path).source_path,path)
                self.assertEqual(AnswerCreate(content='A research question',client_message_id=uuid4(),source_path=path).source_path,path)
                self.assertEqual(EssayCreate(topic='A research topic',audience='Product managers',client_message_id=uuid4(),source_path=path).source_path,path)

    def test_original_links_preserve_valid_pinned_paths(self):
        revision='be8ab89a890a833cbba2c892178f823fff178c65'
        for path in ['episodes/casey-winters_/transcript.md','episodes/gustav-söderström/transcript.md']:
            with self.subTest(path=path):
                source,_=source_links({'source_path':path,'corpus_revision':revision})
                self.assertEqual(source,'https://github.com/ChatPRD/lennys-podcast-transcripts/blob/'+revision+'/'+path)

    def test_unsafe_or_noncanonical_source_paths_remain_rejected(self):
        for path in ['../secret','episodes/../transcript.md','/episodes/sean-ellis/transcript.md','episodes/a/b/transcript.md','episodes/%2e%2e/transcript.md','https://other.invalid/transcript.md','episodes/a\\b/transcript.md','episodes/a\n/transcript.md']:
            with self.subTest(path=path):
                for cls,fields in [(SearchRequest,{'query':'research'}),(AnswerCreate,{'content':'A question','client_message_id':uuid4()}),(EssayCreate,{'topic':'Research topic','audience':'Product managers','client_message_id':uuid4()})]:
                    with self.assertRaises(ValueError):cls(source_path=path,**fields)
                self.assertIsNone(source_links({'source_path':path,'corpus_revision':'a'*40})[0])
