import unittest
import tempfile
import trap.steps.quality
from tkp.testutil import db_subs
from tkp.database.database import DataBase
from tkp.database import query
import tkp.utility.accessors
import tkp.testutil.data as testdata
from tkp.testutil.decorators import requires_database

@requires_database()
class TestQuality(unittest.TestCase):
    def __init__(self, *args):
        super(TestQuality, self).__init__(*args)
        self.accessor = tkp.utility.accessors.open(testdata.casa_table)

    def test_parse_parset(self):
        parset = tempfile.NamedTemporaryFile()
        parset.flush()
        trap.steps.quality.parse_parset(parset.name)

    def test_check(self):
        parset = tempfile.NamedTemporaryFile()
        parset.flush()
        trap.steps.quality.reject_check(self.accessor.url, parset.name)
