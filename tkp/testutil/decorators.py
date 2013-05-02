import os
import unittest
from tkp.testutil import db_subs


if not  hasattr(unittest.TestCase, 'assertIsInstance'):
    import unittest2 as unittest

def requires_database():
    if os.environ.get("TKP_DISABLEDB", False):
        return unittest.skip("Database functionality disabled in configuration")
    return lambda func: func

def requires_mongodb():
    if os.environ.get("TKP_DISABLEMONGODB", False):
        return unittest.skip("mongodb functionality disabled in configuration")
    return lambda func: func

def requires_data(*args):
    for filename in args:
        if not os.path.exists(filename):
            return unittest.skip("Test data (%s) not available" % filename)
    return lambda func: func

def requires_module(module_name):
    try:
        __import__(module_name)
    except ImportError:
        return unittest.skip("Required module (%s) not available" % module_name)
    return lambda func: func

def duration(test_duration):
    max_duration = os.environ.get("TKP_MAXTESTDURATION", False)
    if max_duration:
        if max_duration < test_duration:
            return unittest.skip(
             "Tests of duration > %s disabled with TKP_MAXTESTDURATION" %
                max_duration)
    return lambda func: func
