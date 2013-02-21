import unittest
import tempfile
import trap.steps.classification
from tkp.database import query
from tkp.classification.transient import Transient
from tkp.testutil import db_subs
from tkp.testutil.decorators import requires_database

@requires_database()
class TestClassification(unittest.TestCase):
    def __init__(self, *args):
        super(TestClassification, self).__init__(*args)
        self.dataset_id = db_subs.create_dataset_8images(extract_sources=True)

        runcat_query = "select id from runningcatalog where dataset=%s"
        cursor = query(runcat_query, [self.dataset_id])
        self.transients = [Transient(runcatid=i) for (i,) in cursor.fetchall()]

        self.parset = tempfile.NamedTemporaryFile()
        self.parset.write("weighting.cutoff = 0.2\n")
        self.parset.flush()

    def runTest(self):
        trap.steps.classification.classify(self.transients[0], self.parset.name)

