import unittest
from tkp.steps.feature_extraction import extract_features
from tkp.db import execute
from tkp.testutil.decorators import requires_database
from tkp.db.generic import get_db_rows_as_dicts

@requires_database()
class TestFeatureExtraction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        #NB This is basically nonsense, we're just selecting any old
        #extracted source so we can check the feature extraction syntax.
        xtrsrc_qry = """SELECT id as trigger_xtrsrc
                          FROM extractedsource"""
        cursor = execute(xtrsrc_qry)
        cls.transients = get_db_rows_as_dicts(cursor)

    @unittest.skip("TODO: extract_features recipe needs modification!!!")
    def test_extract_features(self):
        for t in self.transients:
            extract_features(t)
