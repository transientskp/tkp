import os

import unittest
from tkp.testutil.decorators import requires_database, requires_data, duration
from tkp.testutil.data import DATAPATH


def debug_print(*args):
    return #Comment to switch on debug prints.
    print("**", end=' ')
    for a in args:
        print(a, end=' ')
    print("**")


testfile1 = '/bin/true'
testfile2 = '/bin/false'
dummypath = '/dummypath/dummypath'

class TestDatabaseDecorators(unittest.TestCase):
    @requires_database()
    def test_requires_database(self):
        debug_print("Database testing enabled.")


class TestDataDecorators(unittest.TestCase):
    def test_datapath_defined(self):
        self.assertNotEqual(DATAPATH, None)
        debug_print("Test data path:", DATAPATH)

    @requires_data(testfile1, testfile2)
    def test_requires_data_decorator(self):
        self.assertTrue(os.path.exists(testfile1))
        self.assertTrue(os.path.exists(testfile2))

    @requires_data(dummypath)
    def test_requires_data_decorator_skips(self):
        self.assertTrue(os.path.exists(dummypath))

    @requires_data(dummypath, testfile1)
    def test_requires_data_decorator_skips_for_partial_miss(self):
        self.assertTrue(os.path.exists(dummypath))


class TestDurationDecorator(unittest.TestCase):
    def test_max_duration_defined(self):
        debug_print("Max_duration:", os.environ.get("TKP_MAXTESTDURATION", False))

    @duration(5)
    def test_short(self):
        debug_print("Will run test duration = 5")
    @duration(25)
    def test_medium(self):
        debug_print("Will run test duration = 25")
    @duration(300)
    def test_long(self):
        debug_print("Will run test duration = 300")



