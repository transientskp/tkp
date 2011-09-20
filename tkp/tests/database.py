import unittest
try:
    unittest.TestCase.assertIsInstance
except AttributeError:
    import unittest2 as unittest
from utility.decorators import requires_database

class TestDatabase(unittest.TestCase):

    def setUp(self):
        import tkp.database.database
        import monetdb
        self.database = tkp.database.database.DataBase()

    def tearDown(self):
        self.database.close()

    @requires_database()
    def test_basics(self):
        self.assertIsInstance(self.database, tkp.database.database.DataBase)
        self.assertIsInstance(self.database.connection,
                              monetdb.sql.connections.Connection)
        self.assertIsInstance(self.database.cursor,
                              monetdb.sql.cursors.Cursor)

    @requires_database()
    def test_failures(self):
        self.assertRaises(monetdb.monetdb_exceptions.DatabaseError,
                          tkp.database.database.DataBase,
                          host='localhost',
                          name='non_existant_database',
                          user='unknown',
                          password='empty')


if __name__ == "__main__":
    unittest.main()
