import os
import unittest
from tempfile import NamedTemporaryFile
from tkp.config import get_database_config
from tkp.db.dump import dump_db, dump_pg
from tkp.testutil.decorators import requires_database

class TestDump(unittest.TestCase):
    @requires_database()
    @unittest.skipUnless(get_database_config()['engine'] == "postgresql", "Postgres disabled")
    def test_database_dump_pg(self):
        dbconfig = get_database_config()
        with NamedTemporaryFile() as dumpfile:
            dump_pg(
                dbconfig['host'], dbconfig['port'], dbconfig['database'],
                dbconfig['user'], dbconfig['password'], dumpfile.name
            )

            # Output should start with "--\n-- PostgreSQL database dump\n":
            dumpfile.seek(0)
            self.assertEqual(dumpfile.readline().strip(), "--")
            self.assertEqual(dumpfile.readline().strip(), "-- PostgreSQL database dump")
            # And end with "-- PostgreSQL database dump complete\n--\n\n"
            dumpfile.seek(-41, os.SEEK_END)
            self.assertEqual(dumpfile.read().strip(), "-- PostgreSQL database dump complete\n--")


    def test_database_dump_unknown(self):
        self.assertRaises(NotImplementedError, dump_db,
            "dummy_engine", None, None, None, None, None, None
        )
