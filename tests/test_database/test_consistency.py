from builtins import object
import unittest
import tkp.db.consistency as db_consistency
import tkp.db
from tkp.testutil.mock import Mock

class MockResult(object):
    def __init__(self, result):
        self.result = result

    def fetchone(self):
        return self.result

class TestDBConsistencyCheck(unittest.TestCase):
    def test_is_consistent(self):
        # We provide a mock database result from a consistent database.
        db_execute_old = tkp.db.execute
        tkp.db.execute = Mock(MockResult([0])) # This is the correct result
        self.assertTrue(db_consistency.isconsistent("dummy query"))
        tkp.db.execute = db_execute_old

    def test_is_inconsistent(self):
        # We provide a mock database result from an INconsistent database.
        db_execute_old = tkp.db.execute
        tkp.db.execute = Mock(MockResult([1])) # This is the wrong result
        self.assertFalse(db_consistency.isconsistent("dummy query"))
        tkp.db.execute = db_execute_old

    def test_bad_query(self):
        # We fail to provide a valid query result: this database also fails.
        db_execute_old = tkp.db.execute
        tkp.db.execute = Mock(MockResult([])) # This is an invalid result
        self.assertFalse(db_consistency.isconsistent("dummy query"))
        tkp.db.execute = db_execute_old

    def test_check_good(self):
        # db_consistency.check() is a wrapper over multiple calls to
        # isconsistent(). Check that it returns True if those calls succeed.
        db_execute_old = tkp.db.execute
        tkp.db.execute = Mock(MockResult([0])) # This is the correct result
        self.assertTrue(db_consistency.check())
        tkp.db.execute = db_execute_old

    def test_check_bad(self):
        # db_consistency.check() is a wrapper over multiple calls to
        # isconsistent(). Check that it returns False if those calls fail.
        db_execute_old = tkp.db.execute
        tkp.db.execute = Mock(MockResult([1])) # This is the wrong result
        self.assertFalse(db_consistency.check())
        tkp.db.execute = db_execute_old
