"""Hand-calculated ranked lists guard reported metrics; no provider/model calls."""
from types import SimpleNamespace
import math
import unittest

from backend.evaluate_retrieval import metrics


class MetricTests(unittest.TestCase):
    def test_recall_is_not_precision_and_missing_evidence_matters(self):
        value=metrics([SimpleNamespace(id='a'),SimpleNamespace(id='x')],{'a','b','c'},[['a'],['b'],['c']])
        self.assertAlmostEqual(value['recall_at_8'],1/3)
        self.assertEqual(value['mrr_at_8'],1)

    def test_rank_discount_and_reciprocal_rank(self):
        value=metrics([SimpleNamespace(id='x'),SimpleNamespace(id='b'),SimpleNamespace(id='a')],{'a','b'},[['a'],['b']])
        self.assertEqual(value['recall_at_8'],1)
        self.assertEqual(value['mrr_at_8'],.5)
        self.assertAlmostEqual(value['ndcg_at_8'],(1/math.log2(3)+.5)/(1+1/math.log2(3)))

    def test_empty_output_and_equivalent_anchor_passages(self):
        empty=metrics([],{'a'},[['a']])
        self.assertTrue(all(value==0 for value in empty.values()))
        value=metrics([SimpleNamespace(id='b')],{'a','b'},[['a','b']])
        self.assertEqual(value['recall_at_8'],.5)
        self.assertEqual(value['anchor_recall_at_8'],1)
