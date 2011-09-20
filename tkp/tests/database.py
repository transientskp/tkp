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
        self.tkp_database = tkp.database.database
        self.monetdb = monetdb
        self.database = self.tkp_database.DataBase()

    def tearDown(self):
        self.database.close()

    @requires_database()
    def test_basics(self):
        self.assertIsInstance(self.database, self.tkp_database.DataBase)
        self.assertIsInstance(self.database.connection,
                              self.monetdb.sql.connections.Connection)
        self.assertIsInstance(self.database.cursor,
                              self.monetdb.sql.cursors.Cursor)

    @requires_database()
    def test_failures(self):
        self.assertRaises(self.monetdb.monetdb_exceptions.DatabaseError,
                          self.tkp_database.DataBase,
                          host='localhost',
                          name='non_existant_database',
                          user='unknown',
                          password='empty')


if __name__ == "__main__":
    unittest.main()
