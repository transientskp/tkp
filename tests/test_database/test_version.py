import unittest
from tkp.db.model import Version, SCHEMA_VERSION
from tkp.db.database import Database


class TestVersion(unittest.TestCase):
    def setUp(self):
        self.database = Database()
        self.database.connect()

    def test_version(self):
        session = self.database.Session()
        v = session.query(Version).filter(Version.name == 'revision').one()
        self.assertEqual(v.value, SCHEMA_VERSION)