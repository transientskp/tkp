import unittest2 as unittest
from tkp.testutil.decorators import requires_database

class TestDatabaseConnection(unittest.TestCase):

    def setUp(self):
        import tkp.db.database
        self.database = tkp.db.database.Database()

    @unittest.skip("disable this for now since it doesn't make sense")
    @requires_database()
    def test_using_testdb(self):
        import tkp.db.database
        import tkp.config
        self.assertEquals(self.database.database,
                          tkp.config.config['test']['test_database_name'])
        
    @requires_database()
    def test_basics(self):
        import tkp.db.database
        import monetdb
        self.assertIsInstance(self.database, tkp.db.database.Database)
        self.assertIsInstance(self.database.connection,
                              monetdb.sql.connections.Connection)
        self.assertIsInstance(self.database.cursor,
                              monetdb.sql.cursors.Cursor)

    @requires_database()
    def test_failures(self):
        import tkp.db.database
        import monetdb
        tkp.db.configure(hostname='localhost',
                               database='non_existant_database',
                               username='unknown',
                               password='empty')
        self.assertRaises(monetdb.monetdb_exceptions.DatabaseError,
                          tkp.db.connect)


if __name__ == "__main__":
    unittest.main()
