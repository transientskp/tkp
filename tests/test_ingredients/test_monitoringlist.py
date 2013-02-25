import unittest
import tempfile
from tkp.testutil import db_subs
from tkp.testutil.decorators import requires_database

@requires_database()
class TestMonitoringlist(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset_id = db_subs.create_dataset_8images()
        cls.parset = tempfile.NamedTemporaryFile()
        cls.parset.flush()

