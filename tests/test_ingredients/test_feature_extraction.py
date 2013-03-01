import unittest
import trap.ingredients.feature_extraction
from tkp.database.database import DataBase
from tkp.database import query
from tkp.database.utils import generic as dbgeneric
from tkp.testutil import db_subs
from tkp.testutil.decorators import requires_database

@requires_database()
class TestFeatureExtraction(unittest.TestCase):
    def setUp(self):
        self.database = DataBase()
        #NB This is basically nonsense, we're just selecting any old
        #extracted source so we can check the feature extraction syntax.
        xtrsrc_qry = """SELECT id as trigger_xtrsrc 
                          FROM extractedsource"""
        cursor = query(self.database.connection, xtrsrc_qry)

        self.transients = dbgeneric.get_db_rows_as_dicts(cursor)

    @unittest.skip("TODO: extract_features recipe needs modification!!!")
    def test_extract_features(self):
        for t in self.transients:
            trap.ingredients.feature_extraction.extract_features(t)
