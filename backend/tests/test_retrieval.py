import unittest
from uuid import uuid4

from pydantic import ValidationError

from backend.app.retrieval import SearchRequest, overlaps, reciprocal_rank_fusion, select_passages


def row(key, episode='A', start=0, end=100, tokens=100, content=None):
    return {'id':key,'episode_id':episode,'version':1,'source_hash':episode*64,'char_start':start,'char_end':end,
            'estimated_tokens':tokens,'original_text':content or key}


class FusionTests(unittest.TestCase):
    def test_two_index_votes_and_exact_rank_formula(self):
        a,b,c=row('a'),row('b'),row('c')
        fused=reciprocal_rank_fusion({'dense':[a,b],'sparse':[c,b]})
        self.assertEqual([r['id'] for r in fused],['b','a','c'])
        self.assertAlmostEqual(fused[0]['rank_score'],2/62)
        self.assertEqual((fused[0]['dense_rank'],fused[0]['sparse_rank']),(2,2))

    def test_duplicate_id_cannot_vote_twice_in_one_index(self):
        a,b=row('a'),row('b')
        fused=reciprocal_rank_fusion({'dense':[a,a,b]})
        self.assertEqual(len(fused),2)
        self.assertAlmostEqual(fused[1]['rank_score'],1/62)

    def test_ties_are_stable_across_index_order(self):
        a,b=row('a'),row('b')
        first=reciprocal_rank_fusion({'dense':[a,b],'sparse':[b,a]})
        second=reciprocal_rank_fusion({'sparse':[b,a],'dense':[a,b]})
        self.assertEqual([r['id'] for r in first],[r['id'] for r in second])

    def test_empty_and_single_index(self):
        self.assertEqual(reciprocal_rank_fusion({'dense':[],'sparse':[]}),[])
        self.assertEqual(reciprocal_rank_fusion({'sparse':[row('b'),row('a')]})[0]['id'],'b')

    def test_overlap_requires_same_episode_version_and_substantial_span(self):
        a=row('a',start=0,end=1000)
        self.assertTrue(overlaps(a,row('b',start=100,end=900)))
        self.assertFalse(overlaps(a,row('c',start=900,end=1900)))
        self.assertFalse(overlaps(a,row('d',episode='B')))
        b=row('b');b['version']=2
        self.assertFalse(overlaps(a,b))

    def test_exact_normalized_duplicates_and_overlaps_do_not_consume_budget(self):
        rows=[row('a',content='Same  TEXT'),row('b',episode='B',content='same text'),row('c',start=100,end=200)]
        self.assertEqual([r['id'] for r in select_passages(rows,SearchRequest(query='test'))],['a','c'])

    def test_budget_and_episode_diversity_are_enforced(self):
        rows=[row(str(i),start=i*200,end=i*200+100,tokens=200) for i in range(6)]+[row('other',episode='B',tokens=200)]
        selected=select_passages(rows,SearchRequest(query='test',token_budget=800,per_episode=2))
        self.assertEqual([r['id'] for r in selected],['0','1','other'])

    def test_explicit_episode_scope_can_use_its_available_passages(self):
        rows=[row(str(i),start=i*200,end=i*200+100) for i in range(9)]
        selected=select_passages(rows,SearchRequest(query='test',episode_id=uuid4(),limit=8))
        self.assertEqual(len(selected),8)

    def test_validation_rejects_unbounded_or_ambiguous_inputs(self):
        for value in [{'query':' '},{'query':'x'*1001},{'query':'test','limit':11},{'query':'test','token_budget':9000},
                      {'query':'test','candidates':101},{'query':'test','source_path':'../../secrets'},
                      {'query':'test','guest':' '},{'query':'test','neighbor_radius':2},{'query':'test','provider':'cloud'}]:
            with self.subTest(value=value),self.assertRaises(ValidationError):SearchRequest(**value)
