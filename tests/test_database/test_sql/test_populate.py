import unittest
from tkp.testutil.decorators import requires_test_db_managed
import tkp.db.sql.populate
import os
import getpass


config = {
    'engine':  os.environ.get('TKP_DBENGINE', 'postgresql'),
    'database': 'test_management',
    'user': os.environ.get('TKP_DBUSER', getpass.getuser()),
    'password': os.environ.get('TKP_DBPASSWORD', getpass.getuser()),
    'host': os.environ.get('TKP_DBHOST', 'localhost'),
    'port': os.environ.get('TKP_DBPORT', '5432'),
    'yes': True,
    'destroy': True,
}


class TestPopulate(unittest.TestCase):
    """
    To run these tests you need to enable TKP_TESTDBMANAGMENT.

    This is potentially dangerous, since it will create and destroy databases.

    This test expects a test_management db, other connection parameters can be
    set using TKP_DBUSER, TKP_DBPASSWORD, TKP_DBHOST and TKP_DBPORT.


    """
    def test_verify(self):
        tkp.db.sql.populate.get_input = lambda x: "N"
        with self.assertRaises(SystemExit):
            tkp.db.sql.populate.verify(config)
        tkp.db.sql.populate.get_input = lambda x: "y"
        tkp.db.sql.populate.verify(config)

    @requires_test_db_managed()
    def test_connect(self):
        tkp.db.sql.populate.connect(config)

    @requires_test_db_managed()
    def test_destroy_postgres(self):
        connection = tkp.db.sql.populate.connect(config)
        tkp.db.sql.populate.destroy_postgres(connection)

    @requires_test_db_managed()
    def test_destroy_monetdb(self):
        with self.assertRaises(SystemExit):
            tkp.db.sql.populate.destroy_monetdb()

    @requires_test_db_managed()
    def test_destroy(self):
        config2 = config.copy()
        config2['destroy'] = True
        tkp.db.sql.populate.destroy(config2)

        config2['destroy'] = False
        with self.assertRaises(AssertionError):
            tkp.db.sql.populate.destroy(config2)

    @requires_test_db_managed()
    def test_populate(self):
        tkp.db.sql.populate.populate(config)

