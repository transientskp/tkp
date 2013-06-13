import unittest
import tempfile
from tkp.testutil import db_subs
from tkp.testutil.decorators import requires_database

@unittest.skip('Monitoringlist not currently implemented')
@requires_database()
class TestMonitoringlist(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        pass

