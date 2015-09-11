import unittest
from exceptions import StandardError
from tkp.testutil.decorators import requires_database
import tkp.db

class TestDatabaseConnection(unittest.TestCase):

    def setUp(self):
        self.database = tkp.db.database.Database()

    @requires_database()
    def test_basics(self):
        self.assertIsInstance(self.database, tkp.db.database.Database)

    @requires_database()
    def test_for_valid_exceptions(self):
        # Required exception names, as per PEP-0249 (DB-API):
        exceptions = [
            "Warning",
            "Error",
            "InterfaceError",
            "DatabaseError",
            "DataError",
            "OperationalError",
            "IntegrityError",
            "InternalError",
            "ProgrammingError",
            "NotSupportedError"
        ]


        # All DB-API exceptions are subclasses of StandardError:
        for exception in exceptions:
            self.assertTrue(
                issubclass(
                    getattr(self.database.connection.connection.connection, exception),
                    StandardError
                )
            )

    @requires_database()
    def test_for_invalid_exceptions(self):
        # The following are not valid database exceptions, but appear eg in
        # the psycopg2 namespace.
        bad_exceptions = [
            "test",
            "Date",
            "apilevel",
            "connect"
        ]

        for exception in bad_exceptions:
            with self.assertRaises(AttributeError):
                getattr(self.database.exceptions, exception)
