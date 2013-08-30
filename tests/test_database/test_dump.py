import os
import unittest2 as unittest
from tempfile import NamedTemporaryFile
from tkp.config import database_config
from tkp.db.dump import dump_db, dump_monetdb, dump_pg
from tkp.testutil.decorators import requires_database

class TestDump(unittest.TestCase):
    @requires_database()
    @unittest.skipUnless(database_config()['engine'] == "postgresql", "Postgres disabled")
    def test_database_dump_pg(self):
        raise NotImplementedError

    @requires_database()
    @unittest.skipUnless(database_config()['engine'] == "monetdb", "Monet disabled")
    def test_database_dump_monet(self):
        dbconfig = database_config()
        with NamedTemporaryFile() as dumpfile:
            dump_monetdb(
                dbconfig['host'], dbconfig['port'], dbconfig['database'],
                dbconfig['user'], dbconfig['password'], dumpfile.name
            )
            # Output should start with "START TRANSACTION;" and end with
            # "COMMIT;"
            dumpfile.seek(0)
            self.assertEqual(dumpfile.readline().strip(), "START TRANSACTION;")
            dumpfile.seek(-8, os.SEEK_END)
            self.assertEqual(dumpfile.readline().strip(), "COMMIT;")

    def test_database_dump_unknown(self):
        self.assertRaises(NotImplementedError, dump_db,
            "dummy_engine", None, None, None, None, None, None
        )
