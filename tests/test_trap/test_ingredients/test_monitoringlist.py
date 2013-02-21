import unittest
import tempfile
import trap.steps.monitoringlist
from tkp.testutil import db_subs, db_queries
from tkp.testutil.decorators import requires_database

@requires_database()
class TestMonitoringlist(unittest.TestCase):
    def __init__(self, *args):
        super(TestMonitoringlist, self).__init__(*args)
        self.dataset_id = db_subs.create_dataset_8images()
        self.parset = tempfile.NamedTemporaryFile()
        self.parset.flush()

