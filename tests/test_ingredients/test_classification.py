import unittest
import tempfile
import tkp.steps.classification
from tkp.database import query
from tkp.classification.transient import Transient
from tkp.testutil import db_subs
from tkp.testutil.decorators import requires_database

@requires_database()
class TestClassification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset_id = db_subs.create_dataset_8images(extract_sources=True)
        runcat_query = "select id from runningcatalog where dataset=%s"
        cursor = query(runcat_query, [cls.dataset_id])
        cls.transients = [Transient(runcatid=i) for (i,) in cursor.fetchall()]
        cls.parset = tempfile.NamedTemporaryFile()
        cls.parset.write("weighting.cutoff = 0.2\n")
        cls.parset.flush()

    def runTest(self):
        tkp.steps.classification.classify(self.transients[0], self.parset.name)

