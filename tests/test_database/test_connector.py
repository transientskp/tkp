import unittest2 as unittest
from tkp.testutil.decorators import requires_database
import tkp.db

class TestDatabaseConnection(unittest.TestCase):

    def setUp(self):
        self.database = tkp.db.database.Database()

    def tearDown(self):
        # reset database config
        tkp.db.configure()

    @requires_database()
    def test_basics(self):
        self.assertIsInstance(self.database, tkp.db.database.Database)

