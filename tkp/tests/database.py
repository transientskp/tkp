import unittest
try:
    unittest.TestCase.assertIsInstance
except AttributeError:
    import unittest2 as unittest
import tkp.database.database
import monetdb

class TestDatabase(unittest.TestCase):

    def setUp(self):
        # Connect and verify that the default database is available
        self.database = tkp.database.database.DataBase()

    def tearDown(self):
        self.database.close()

    def test_basics(self):
        self.assertIsInstance(self.database, tkp.database.database.DataBase)
        self.assertIsInstance(self.database.connection,
                              monetdb.sql.connections.Connection)
        self.assertIsInstance(self.database.cursor,
                              monetdb.sql.cursors.Cursor)

    def test_failures(self):
        self.assertRaises(monetdb.monetdb_exceptions.DatabaseError,
                          tkp.database.database.DataBase,
                          hostname='localhost',
                          dbname='non_existant_database',
                          user='unknown',
                          password='empty')
        
    
if __name__ == "__main__":
    unittest.main()
