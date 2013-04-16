import unittest2 as unittest
from tkp.testutil.decorators import requires_database
import tkp.db

class TestDatabaseConnection(unittest.TestCase):

    def setUp(self):
        self.database = tkp.db.database.Database()

    def tearDown(self):
        # reset database config
        tkp.db.configure()

    @unittest.skip("disable this for now since it doesn't make sense")
    @requires_database()
    def test_using_testdb(self):
        import tkp.config
        self.assertEquals(self.database.database,
                          tkp.config.config['test']['test_database_name'])
        
    @requires_database()
    def test_basics(self):
        self.assertIsInstance(self.database, tkp.db.database.Database)

