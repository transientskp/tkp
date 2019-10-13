import unittest
from tkp.db.model import Version, SCHEMA_VERSION
from tkp.db.database import Database
from tkp.testutil.decorators import database_disabled


class TestVersion(unittest.TestCase):
    def setUp(self):
        # Can't use a regular skip here, due to a Nose bug:
        # https://github.com/nose-devs/nose/issues/946
        if database_disabled():
            raise unittest.SkipTest("Database functionality disabled "
                                    "in configuration.")
        self.database = Database()
        self.database.connect()

    def test_version(self):
        session = self.database.Session()
        v = session.query(Version).filter(Version.name == 'revision').one()
        self.assertEqual(v.value, SCHEMA_VERSION)
